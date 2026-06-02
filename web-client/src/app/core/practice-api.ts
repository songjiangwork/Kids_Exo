import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpResponse } from '@angular/common/http';

export interface SettingOption {
  value: number | string;
  label: string;
}

export interface PluginSetting {
  name: string;
  label: string;
  control: string;
  default: Array<number | string>;
  options: SettingOption[];
}

export interface OnlinePlugin {
  plugin: string;
  subject: string;
  category: string;
  title: string;
  description: string;
  default_locale: string;
  settings: PluginSetting[];
}

export interface OnlineCatalog {
  default_locale: string;
  question_counts: number[];
  feedback_modes: string[];
  show_timer_configurable: boolean;
  plugins: OnlinePlugin[];
}

export interface PracticeRequest {
  plugin: string;
  plugin_settings: Record<string, Array<number | string>>;
  question_count: number;
  requested_locale: string;
  feedback_mode: string;
  show_timer: boolean;
  seed?: number;
}

export interface StudentQuestion {
  identifier: string;
  position: number;
  total_questions: number;
  prompt: string;
  question_type?: string;
  choices?: string[];
  speech_text?: string | null;
  speech_locale?: string | null;
}

export interface SavedSession {
  id: number;
  student_token: string;
  plugin: string;
  requested_locale: string;
  feedback_mode: string;
  show_timer: boolean;
  localization_fallback_keys: string[];
  questions: StudentQuestion[];
}

export interface Learner {
  id: number;
  nickname: string;
  active: boolean;
}

export interface LearnerSkillBreakdown {
  plugin: string;
  title: string;
  correct_answers: number;
  total_questions: number;
  accuracy: number;
}

export interface LearnerMistakeEntry {
  plugin: string;
  title: string;
  prompt: string;
  expected_answer: number;
  last_submitted_answer: number;
  times_missed: number;
  last_seen_at: string;
}

export interface LearnerAnalytics {
  total_sessions: number;
  completed_sessions: number;
  total_questions: number;
  correct_answers: number;
  accuracy: number;
  average_elapsed_seconds: number | null;
  last_completed_at: string | null;
  skill_breakdown: LearnerSkillBreakdown[];
  mistake_notebook: LearnerMistakeEntry[];
}

export interface SessionSummary {
  id: number;
  student_token: string;
  plugin: string;
  status: string;
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  elapsed_seconds: number | null;
  created_at?: string;
  completed_at?: string | null;
}

export interface IncorrectQuestion {
  prompt: string;
  submitted_answer: number;
  expected_answer: number;
}

export interface PracticeResults {
  status: string;
  total_questions: number;
  answered_questions: number;
  correct_answers: number;
  elapsed_seconds: number | null;
  incorrect_questions: IncorrectQuestion[];
}

export interface PrintableWorksheetChoice {
  identifier: string;
  subject: string;
  category: string;
  title: string;
}

export interface StudentSession {
  plugin: string;
  status: string;
  timer_status: string;
  requested_locale: string;
  feedback_mode: string;
  show_timer: boolean;
  answered_questions: number;
  correct_answers: number;
  active_elapsed_seconds: number;
  questions: StudentQuestion[];
}

export interface TimerStatus {
  timer_status: string;
  active_elapsed_seconds: number;
}

export interface AnswerResult {
  normalized_answer: number;
  is_correct: boolean | null;
}

@Injectable({ providedIn: 'root' })
export class PracticeApi {
  constructor(private readonly http: HttpClient) {}

  catalog(): Observable<OnlineCatalog> {
    return this.http.get<OnlineCatalog>('/api/practice-plugins');
  }

  createLearner(nickname: string): Observable<Learner> {
    return this.http.post<Learner>('/api/learners', { nickname });
  }

  updateLearner(learner: Learner): Observable<Learner> {
    return this.http.patch<Learner>(`/api/learners/${learner.id}`, {
      nickname: learner.nickname,
      active: learner.active,
    });
  }

  learner(learnerId: number): Observable<Learner> {
    return this.http.get<Learner>(`/api/learners/${learnerId}`);
  }

  deleteLearner(learnerId: number): Observable<void> {
    return this.http.delete<void>(`/api/learners/${learnerId}`);
  }

  learners(): Observable<Learner[]> {
    return this.http.get<Learner[]>('/api/learners');
  }

  createSession(learnerId: number, request: PracticeRequest): Observable<SavedSession> {
    return this.http.post<SavedSession>(`/api/learners/${learnerId}/sessions`, request);
  }

  studentSession(token: string): Observable<StudentSession> {
    return this.http.get<StudentSession>(`/api/student/sessions/${token}`);
  }

  pauseStudentTimer(token: string): Observable<TimerStatus> {
    return this.http.post<TimerStatus>(`/api/student/sessions/${token}/timer/pause`, {});
  }

  resumeStudentTimer(token: string): Observable<TimerStatus> {
    return this.http.post<TimerStatus>(`/api/student/sessions/${token}/timer/resume`, {});
  }

  learnerSessions(learnerId: number): Observable<SessionSummary[]> {
    return this.http.get<SessionSummary[]>(`/api/learners/${learnerId}/sessions`);
  }

  learnerAnalytics(learnerId: number): Observable<LearnerAnalytics> {
    return this.http.get<LearnerAnalytics>(`/api/learners/${learnerId}/analytics`);
  }

  parentResults(learnerId: number, sessionId: number): Observable<PracticeResults> {
    return this.http.get<PracticeResults>(`/api/learners/${learnerId}/sessions/${sessionId}/results`);
  }

  studentResults(token: string): Observable<PracticeResults> {
    return this.http.get<PracticeResults>(`/api/student/sessions/${token}/results`);
  }

  printableWorksheets(): Observable<PrintableWorksheetChoice[]> {
    return this.http.get<PrintableWorksheetChoice[]>('/api/printable-worksheets');
  }

  downloadPrintablePdf(
    presetId: string,
    seed: number | null,
    includeWarmup: boolean,
    pageCount: number | null,
    questionCount: number | null,
  ): Observable<HttpResponse<Blob>> {
    return this.http.post('/api/printable-worksheets/pdf', {
      preset_id: presetId,
      ...(seed === null ? {} : { seed }),
      include_warmup: includeWarmup,
      ...(questionCount === null ? { page_count: pageCount ?? 1 } : { question_count: questionCount }),
    }, {
      observe: 'response',
      responseType: 'blob',
    });
  }

  submitAnswer(token: string, questionId: string, answer: string): Observable<AnswerResult> {
    return this.http.post<AnswerResult>(
      `/api/student/sessions/${token}/questions/${questionId}/attempts`,
      { answer },
    );
  }
}
