import { Component, OnDestroy, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { PracticeApi, PracticeResults, StudentSession } from '../core/practice-api';

@Component({
  selector: 'app-student-practice',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './student-practice.html',
  styleUrl: './student-practice.scss',
})
export class StudentPractice implements OnInit, OnDestroy {
  protected readonly session = signal<StudentSession | null>(null);
  protected readonly loading = signal(true);
  protected readonly submitting = signal(false);
  protected readonly error = signal('');
  protected readonly index = signal(0);
  protected readonly feedback = signal<'correct' | 'incorrect' | 'saved' | null>(null);
  protected readonly complete = signal(false);
  protected readonly results = signal<PracticeResults | null>(null);
  protected readonly elapsedSeconds = signal(0);
  protected readonly timerPaused = signal(false);
  protected readonly timerUpdating = signal(false);
  protected answer: string | number | null = '';

  protected readonly question = computed(() => this.session()?.questions[this.index()]);
  protected readonly progress = computed(() => {
    const total = this.session()?.questions.length ?? 1;
    return (this.index() / total) * 100;
  });

  private token = '';
  private routeSubscription?: Subscription;
  private timer?: ReturnType<typeof setInterval>;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly api: PracticeApi,
  ) {}

  ngOnInit(): void {
    this.routeSubscription = this.route.paramMap.subscribe((params) => {
      this.token = params.get('token') ?? '';
      this.api.studentSession(this.token).subscribe({
        next: (session) => {
          this.stopLocalTimer();
          this.session.set(session);
          this.elapsedSeconds.set(session.active_elapsed_seconds);
          this.timerPaused.set(session.timer_status !== 'running');
          this.resumeSession(session);
          this.loading.set(false);
          if (this.shouldRunLocalTimer(session)) {
            this.startLocalTimer();
          }
        },
        error: () => {
          this.error.set('This practice link is not available.');
          this.loading.set(false);
        },
      });
    });
  }

  ngOnDestroy(): void {
    this.routeSubscription?.unsubscribe();
    this.stopLocalTimer();
  }

  protected checkAnswer(): void {
    const question = this.question();
    const normalizedAnswer = this.answer === null ? '' : String(this.answer).trim();
    if (!question || normalizedAnswer === '' || this.isPracticePaused()) {
      return;
    }
    this.submitting.set(true);
    this.api.submitAnswer(this.token, question.identifier, normalizedAnswer).subscribe({
      next: (result) => {
        if (result.is_correct === true) {
          this.feedback.set('correct');
        } else if (result.is_correct === false) {
          this.feedback.set('incorrect');
        } else {
          this.feedback.set('saved');
        }
        this.submitting.set(false);
      },
      error: () => {
        this.error.set('Your answer could not be saved.');
        this.submitting.set(false);
      },
    });
  }

  protected nextQuestion(): void {
    const total = this.session()?.questions.length ?? 0;
    if (this.index() + 1 >= total) {
      this.loadResults();
      return;
    }
    this.index.update((value) => value + 1);
    this.feedback.set(null);
    this.answer = '';
  }

  protected timerText(): string {
    return this.formatSeconds(this.elapsedSeconds());
  }

  protected resultTimeText(): string {
    return this.formatSeconds(this.results()?.elapsed_seconds ?? 0);
  }

  protected isPracticePaused(): boolean {
    return Boolean(this.session()?.show_timer && this.timerPaused());
  }

  protected pauseTimer(): void {
    if (!this.session()?.show_timer || this.timerPaused() || this.timerUpdating()) {
      return;
    }
    this.timerUpdating.set(true);
    this.api.pauseStudentTimer(this.token).subscribe({
      next: (timerStatus) => {
        this.stopLocalTimer();
        this.elapsedSeconds.set(timerStatus.active_elapsed_seconds);
        this.timerPaused.set(true);
        this.timerUpdating.set(false);
      },
      error: () => {
        this.error.set('The timer could not be paused.');
        this.timerUpdating.set(false);
      },
    });
  }

  protected resumeTimer(): void {
    if (!this.session()?.show_timer || !this.timerPaused() || this.timerUpdating()) {
      return;
    }
    this.timerUpdating.set(true);
    this.api.resumeStudentTimer(this.token).subscribe({
      next: (timerStatus) => {
        this.elapsedSeconds.set(timerStatus.active_elapsed_seconds);
        this.timerPaused.set(false);
        this.startLocalTimer();
        this.timerUpdating.set(false);
      },
      error: () => {
        this.error.set('The timer could not be resumed.');
        this.timerUpdating.set(false);
      },
    });
  }

  private resumeSession(session: StudentSession): void {
    if (session.status === 'completed' || session.answered_questions >= session.questions.length) {
      this.loadResults();
      return;
    }
    this.index.set(Math.max(0, session.answered_questions));
    this.feedback.set(null);
    this.answer = '';
  }

  private loadResults(): void {
    this.stopLocalTimer();
    this.submitting.set(true);
    this.api.studentResults(this.token).subscribe({
      next: (results) => {
        this.results.set(results);
        this.complete.set(true);
        this.submitting.set(false);
      },
      error: () => {
        this.error.set('Your results could not be loaded.');
        this.submitting.set(false);
      },
    });
  }

  private formatSeconds(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  private shouldRunLocalTimer(session: StudentSession): boolean {
    return (
      session.show_timer &&
      session.status !== 'completed' &&
      session.answered_questions < session.questions.length &&
      session.timer_status === 'running'
    );
  }

  private startLocalTimer(): void {
    this.stopLocalTimer();
    this.timer = setInterval(
      () => this.elapsedSeconds.update((seconds) => seconds + 1),
      1000,
    );
  }

  private stopLocalTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }
}
