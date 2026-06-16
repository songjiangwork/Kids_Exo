import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpResponse } from '@angular/common/http';

export type PluginSettingValue = string | number | boolean;
export type PluginSettingsValue = Record<string, PluginSettingValue[]>;
export type JsonObject = Record<string, unknown>;
export type AnswerValue = number | string | JsonObject | null;

export interface SettingOption {
  value: PluginSettingValue;
  label: string;
}

export interface PluginSetting {
  name: string;
  label: string;
  control: 'single_choice' | 'multiple_choice' | 'boolean' | 'number' | 'text' | string;
  default: PluginSettingValue[];
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
  supported_delivery_modes?: string[];
  answer_types?: string[];
  release_stage?: string;
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
  plugin_settings: PluginSettingsValue;
  question_count: number;
  requested_locale: string;
  feedback_mode: string;
  show_timer: boolean;
  seed?: number;
}

export interface AssignmentItemCreateRequest {
  item_type?: string;
  plugin: string;
  plugin_settings: PluginSettingsValue;
  question_count: number;
  feedback_mode: string;
  show_timer: boolean;
  required?: boolean;
}

export interface AssignmentCreateRequest {
  title: string;
  description: string;
  source_type?: string;
  due_at?: string | null;
  created_by_role?: string;
  items: AssignmentItemCreateRequest[];
}

export interface StudentQuestion {
  identifier: string;
  position: number;
  total_questions: number;
  prompt: string;
  renderer_type?: string;
  prompt_payload?: JsonObject;
  public_payload?: JsonObject;
  question_type?: string;
  choices?: string[];
  speech_text?: string | null;
  speech_locale?: string | null;
  audio_url?: string | null;
}

export interface SavedSession {
  id: number;
  student_token: string;
  plugin: string;
  subject: string;
  category: string;
  skill: string;
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
  student_code?: string | null;
}

export interface HouseholdStudent {
  id: number;
  nickname: string;
  avatar_key: string;
  student_login_enabled: boolean;
  student_code?: string | null;
}

export interface HouseholdSummary {
  id: number;
  name: string;
  household_code: string;
}

export interface HouseholdStudentsResponse {
  household: HouseholdSummary;
  students: HouseholdStudent[];
}

export interface ParentUnlockStatus {
  unlocked: boolean;
  expires_at?: string | null;
}

export interface StudentLoginResponse {
  student: HouseholdStudent;
}

export interface StudentAuthState {
  student: HouseholdStudent | null;
}

export interface StudentDirectLoginResponse {
  student: HouseholdStudent;
  redirect_to: string;
}

export interface StudentDirectAuthState {
  student: HouseholdStudent;
  household: HouseholdSummary;
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
  expected_answer: AnswerValue;
  last_submitted_answer: AnswerValue;
  expected_display?: string | null;
  last_submitted_display?: string | null;
  answer_type?: string | null;
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
  subject: string;
  category: string;
  skill: string;
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
  submitted_answer: AnswerValue;
  expected_answer: AnswerValue;
  submitted_display?: string | null;
  expected_display?: string | null;
  submitted_work?: string | null;
  answer_type?: string | null;
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
  subject: string;
  category: string;
  skill: string;
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

export interface AssignmentItem {
  id: number;
  item_type: string;
  plugin: string;
  plugin_settings: PluginSettingsValue;
  question_count: number;
  feedback_mode: string;
  show_timer: boolean;
  order_index: number;
  required: boolean;
  status: string;
  linked_session_id: number | null;
  student_token?: string | null;
  skill?: string | null;
  subject?: string | null;
  category?: string | null;
  created_at: string;
  completed_at?: string | null;
}

export interface Assignment {
  id: number;
  learner_id: number;
  title: string;
  description: string;
  status: string;
  source_type: string;
  due_at?: string | null;
  created_by_role: string;
  created_at: string;
  updated_at: string;
  completed_at?: string | null;
  items: AssignmentItem[];
}

export interface AssignmentStartResponse {
  assignment: Assignment;
  item: AssignmentItem;
  student_token: string;
  student_url: string;
}

export interface AnswerResult {
  normalized_answer: AnswerValue;
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

  resetStudentPin(learnerId: number, pin: string): Observable<void> {
    return this.http.post<void>(`/api/learners/${learnerId}/student-pin`, { pin });
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

  householdStudents(): Observable<HouseholdStudentsResponse> {
    return this.http.get<HouseholdStudentsResponse>('/api/household/students');
  }

  unlockParent(pin: string): Observable<ParentUnlockStatus> {
    return this.http.post<ParentUnlockStatus>('/api/household/parent-unlock', { pin });
  }

  lockParent(): Observable<ParentUnlockStatus> {
    return this.http.post<ParentUnlockStatus>('/api/household/parent-lock', {});
  }

  changeParentPin(currentPin: string, newPin: string): Observable<ParentUnlockStatus> {
    return this.http.post<ParentUnlockStatus>('/api/household/parent-pin', {
      current_pin: currentPin,
      new_pin: newPin,
    });
  }

  parentUnlockStatus(): Observable<ParentUnlockStatus> {
    return this.http.get<ParentUnlockStatus>('/api/household/parent-unlock/status');
  }

  studentLogin(studentId: number, pin: string): Observable<StudentLoginResponse> {
    return this.http.post<StudentLoginResponse>('/api/household/students/' + studentId + '/login', { pin });
  }

  studentAuthMe(): Observable<StudentAuthState> {
    return this.http.get<StudentAuthState>('/api/student-auth/me');
  }

  directStudentLogin(
    householdCode: string,
    studentCode: string,
    pin: string,
  ): Observable<StudentDirectLoginResponse> {
    return this.http.post<StudentDirectLoginResponse>('/api/student-direct-auth/login', {
      household_code: householdCode,
      student_code: studentCode,
      pin,
    });
  }

  directStudentMe(): Observable<StudentDirectAuthState> {
    return this.http.get<StudentDirectAuthState>('/api/student-direct-auth/me');
  }

  directStudentLogout(): Observable<void> {
    return this.http.post<void>('/api/student-direct-auth/logout', {});
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

  learnerAssignments(learnerId: number, status: string = 'all'): Observable<Assignment[]> {
    return this.http.get<Assignment[]>('/api/learners/' + learnerId + '/assignments', {
      params: { status },
    });
  }

  createAssignment(learnerId: number, request: AssignmentCreateRequest): Observable<Assignment> {
    return this.http.post<Assignment>('/api/learners/' + learnerId + '/assignments', request);
  }

  startAssignmentItem(assignmentId: number, itemId: number): Observable<AssignmentStartResponse> {
    return this.http.post<AssignmentStartResponse>('/api/assignments/' + assignmentId + '/items/' + itemId + '/start', {});
  }

  archiveAssignment(assignmentId: number): Observable<Assignment> {
    return this.http.post<Assignment>('/api/assignments/' + assignmentId + '/archive', {});
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

  submitAnswer(token: string, questionId: string, answer: Exclude<AnswerValue, null>): Observable<AnswerResult> {
    return this.http.post<AnswerResult>(
      `/api/student/sessions/${token}/questions/${questionId}/attempts`,
      { answer },
    );
  }
}
