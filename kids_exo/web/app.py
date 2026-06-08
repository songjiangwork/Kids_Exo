"""Compatibility entrypoint for existing imports and Uvicorn targets."""

from kids_exo.web.main import app, create_app

__all__ = ["app", "create_app"]
