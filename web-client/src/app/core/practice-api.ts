import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

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

export interface StudentSession {
  plugin: string;
  requested_locale: string;
  feedback_mode: string;
  show_timer: boolean;
  questions: StudentQuestion[];
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

  createLearner(nickname: string): Observable<{ id: number; nickname: string }> {
    return this.http.post<{ id: number; nickname: string }>('/api/learners', { nickname });
  }

  createSession(learnerId: number, request: PracticeRequest): Observable<SavedSession> {
    return this.http.post<SavedSession>(`/api/learners/${learnerId}/sessions`, request);
  }

  studentSession(token: string): Observable<StudentSession> {
    return this.http.get<StudentSession>(`/api/student/sessions/${token}`);
  }

  submitAnswer(token: string, questionId: string, answer: string): Observable<AnswerResult> {
    return this.http.post<AnswerResult>(
      `/api/student/sessions/${token}/questions/${questionId}/attempts`,
      { answer },
    );
  }
}
