#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATE_DIR="$ROOT_DIR/.dev-services"
PID_DIR="$STATE_DIR/pids"
LOG_DIR="$STATE_DIR/logs"

BACKEND_PID_FILE="$PID_DIR/backend.pid"
FRONTEND_PID_FILE="$PID_DIR/frontend.pid"
BACKEND_LOG_FILE="$LOG_DIR/backend.log"
FRONTEND_LOG_FILE="$LOG_DIR/frontend.log"

BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://127.0.0.1:4200"
BACKEND_PORT="8000"
FRONTEND_PORT="4200"

mkdir -p "$PID_DIR" "$LOG_DIR"

usage() {
  cat <<'EOF'
Usage: scripts/dev-services.sh [start|restart|stop|status|logs]

Commands:
  start     Stop any recorded dev servers, then start backend and frontend.
  restart   Same as start.
  stop      Stop recorded backend and frontend processes. Safe if already stopped.
  status    Show recorded process status.
  logs      Print log file paths.

Default: start
EOF
}

read_pid() {
  local pid_file="$1"
  [[ -f "$pid_file" ]] || return 1
  local pid
  pid="$(tr -d '[:space:]' < "$pid_file")"
  [[ -n "$pid" ]] || return 1
  printf '%s' "$pid"
}

is_running() {
  local pid="$1"
  kill -0 "$pid" 2>/dev/null
}

port_pids() {
  local port="$1"
  local pids
  pids="$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t 2>/dev/null || true)"
  if [[ -z "$pids" ]] && command -v fuser >/dev/null 2>&1; then
    pids="$(fuser "$port/tcp" 2>/dev/null || true)"
  fi
  printf '%s\n' "$pids" | tr ' ' '\n' | sed '/^$/d' | sort -u
}

stop_process() {
  local name="$1"
  local pid_file="$2"

  local pid
  if ! pid="$(read_pid "$pid_file")"; then
    echo "$name: not running (no pid file)"
    rm -f "$pid_file"
    return 0
  fi

  if ! is_running "$pid"; then
    echo "$name: not running (stale pid $pid)"
    rm -f "$pid_file"
    return 0
  fi

  echo "$name: stopping pid $pid"
  kill -TERM "-$pid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true

  for _ in {1..30}; do
    if ! is_running "$pid"; then
      rm -f "$pid_file"
      echo "$name: stopped"
      return 0
    fi
    sleep 0.2
  done

  echo "$name: force stopping pid $pid"
  kill -KILL "-$pid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
  rm -f "$pid_file"
}

stop_port_processes() {
  local name="$1"
  local port="$2"

  local pids
  pids="$(port_pids "$port")"
  [[ -n "$pids" ]] || return 0

  echo "$name: stopping existing process(es) on port $port: $pids"
  while read -r pid; do
    [[ -n "$pid" ]] || continue
    kill -TERM "$pid" 2>/dev/null || true
  done <<< "$pids"

  for _ in {1..30}; do
    if [[ -z "$(port_pids "$port")" ]]; then
      echo "$name: port $port is free"
      return 0
    fi
    sleep 0.2
  done

  pids="$(port_pids "$port")"
  while read -r pid; do
    [[ -n "$pid" ]] || continue
    kill -KILL "$pid" 2>/dev/null || true
  done <<< "$pids"
}

start_process() {
  local name="$1"
  local pid_file="$2"
  local log_file="$3"
  local port="$4"
  local workdir="$5"
  shift 5

  : > "$log_file"
  (
    cd "$workdir"
    nohup setsid "$@" > "$log_file" 2>&1 &
    echo "$!" > "$pid_file"
  )
  local pid
  pid="$(read_pid "$pid_file")"
  for _ in {1..240}; do
    if is_running "$pid" && [[ -n "$(port_pids "$port")" ]]; then
      echo "$name: started pid $pid on port $port"
      return 0
    fi
    if ! is_running "$pid"; then
      echo "$name: failed to start. Last log lines:" >&2
      tail -40 "$log_file" >&2 || true
      rm -f "$pid_file"
      exit 1
    fi
    sleep 0.5
  done

  echo "$name: did not open port $port in time. Last log lines:" >&2
  tail -40 "$log_file" >&2 || true
  exit 1
}

start_backend() {
  if [[ ! -x "$ROOT_DIR/.venv/bin/python" ]]; then
    echo "backend: missing $ROOT_DIR/.venv/bin/python" >&2
    echo "Create the virtualenv and install dependencies before starting services." >&2
    exit 1
  fi
  start_process \
    "backend" \
    "$BACKEND_PID_FILE" \
    "$BACKEND_LOG_FILE" \
    "$BACKEND_PORT" \
    "$ROOT_DIR" \
    "$ROOT_DIR/.venv/bin/python" -m uvicorn kids_exo.web.app:app --reload --host 127.0.0.1 --port 8000
}

start_frontend() {
  if [[ ! -d "$ROOT_DIR/web-client/node_modules" ]]; then
    echo "frontend: missing $ROOT_DIR/web-client/node_modules" >&2
    echo "Run npm install in web-client before starting services." >&2
    exit 1
  fi
  start_process \
    "frontend" \
    "$FRONTEND_PID_FILE" \
    "$FRONTEND_LOG_FILE" \
    "$FRONTEND_PORT" \
    "$ROOT_DIR/web-client" \
    npm start -- --host 127.0.0.1 --port 4200
}

stop_all() {
  stop_process "frontend" "$FRONTEND_PID_FILE"
  stop_process "backend" "$BACKEND_PID_FILE"
  stop_port_processes "frontend" "$FRONTEND_PORT"
  stop_port_processes "backend" "$BACKEND_PORT"
}

start_all() {
  stop_all
  start_backend
  start_frontend
  echo
  echo "Backend:  $BACKEND_URL"
  echo "Frontend: $FRONTEND_URL"
  echo "Logs:"
  echo "  backend:  $BACKEND_LOG_FILE"
  echo "  frontend: $FRONTEND_LOG_FILE"
}

status_process() {
  local name="$1"
  local pid_file="$2"
  local pid
  if pid="$(read_pid "$pid_file")" && is_running "$pid"; then
    echo "$name: running pid $pid"
  else
    echo "$name: stopped"
  fi
}

case "${1:-start}" in
  start | restart)
    start_all
    ;;
  stop)
    stop_all
    ;;
  status)
    status_process "backend" "$BACKEND_PID_FILE"
    status_process "frontend" "$FRONTEND_PID_FILE"
    ;;
  logs)
    echo "backend:  $BACKEND_LOG_FILE"
    echo "frontend: $FRONTEND_LOG_FILE"
    ;;
  -h | --help | help)
    usage
    ;;
  *)
    usage
    exit 2
    ;;
esac
