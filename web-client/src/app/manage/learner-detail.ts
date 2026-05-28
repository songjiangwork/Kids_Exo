import { Component, OnInit, computed, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Learner, PracticeApi, SessionSummary } from '../core/practice-api';

@Component({
  selector: 'app-learner-detail',
  imports: [MatButtonModule, MatCardModule, MatProgressSpinnerModule, RouterLink],
  templateUrl: './learner-detail.html',
  styleUrl: './learner-detail.scss',
})
export class LearnerDetail implements OnInit {
  protected readonly learner = signal<Learner | null>(null);
  protected readonly sessions = signal<SessionSummary[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal('');
  protected learnerId = 0;

  protected readonly completedSessions = computed(() =>
    this.sessions().filter((session) => session.status === 'completed'),
  );
  protected readonly totalQuestions = computed(() =>
    this.completedSessions().reduce((sum, session) => sum + session.total_questions, 0),
  );
  protected readonly correctAnswers = computed(() =>
    this.completedSessions().reduce((sum, session) => sum + session.correct_answers, 0),
  );

  constructor(
    private readonly api: PracticeApi,
    private readonly route: ActivatedRoute,
  ) {}

  ngOnInit(): void {
    this.learnerId = Number(this.route.snapshot.paramMap.get('id') ?? 0);
    this.api.learner(this.learnerId).subscribe({
      next: (learner) => {
        this.learner.set(learner);
        this.loadSessions();
      },
      error: () => {
        this.error.set('Could not load this learner.');
        this.loading.set(false);
      },
    });
  }

  protected formatTime(seconds: number | null): string {
    if (seconds === null) {
      return '';
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  private loadSessions(): void {
    this.api.learnerSessions(this.learnerId).subscribe({
      next: (sessions) => {
        this.sessions.set(sessions);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load learner history.');
        this.loading.set(false);
      },
    });
  }
}
