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
import { PracticeApi, StudentSession } from '../core/practice-api';

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
  protected readonly correctCount = signal(0);
  protected readonly elapsedSeconds = signal(0);
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
          this.session.set(session);
          this.loading.set(false);
          if (session.show_timer) {
            this.timer = setInterval(
              () => this.elapsedSeconds.update((seconds) => seconds + 1),
              1000,
            );
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
    if (this.timer) {
      clearInterval(this.timer);
    }
  }

  protected checkAnswer(): void {
    const question = this.question();
    const normalizedAnswer = this.answer === null ? '' : String(this.answer).trim();
    if (!question || normalizedAnswer === '') {
      return;
    }
    this.submitting.set(true);
    this.api.submitAnswer(this.token, question.identifier, normalizedAnswer).subscribe({
      next: (result) => {
        if (result.is_correct === true) {
          this.feedback.set('correct');
          this.correctCount.update((count) => count + 1);
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
      this.complete.set(true);
      if (this.timer) {
        clearInterval(this.timer);
      }
      return;
    }
    this.index.update((value) => value + 1);
    this.feedback.set(null);
    this.answer = '';
  }

  protected timerText(): string {
    const seconds = this.elapsedSeconds();
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }
}
