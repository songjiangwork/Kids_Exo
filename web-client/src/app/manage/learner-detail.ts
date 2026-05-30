import { Component, OnInit, computed, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Learner, LearnerAnalytics, PracticeApi, SessionSummary } from '../core/practice-api';

@Component({
  selector: 'app-learner-detail',
  imports: [MatButtonModule, MatCardModule, MatProgressSpinnerModule, RouterLink],
  templateUrl: './learner-detail.html',
  styleUrl: './learner-detail.scss',
})
export class LearnerDetail implements OnInit {
  protected readonly learner = signal<Learner | null>(null);
  protected readonly analytics = signal<LearnerAnalytics | null>(null);
  protected readonly sessions = signal<SessionSummary[]>([]);
  protected readonly loading = signal(true);
  protected readonly error = signal('');
  protected learnerId = 0;
  protected readonly summaryCards = computed(() => {
    const analytics = this.analytics();
    if (analytics === null) {
      return [];
    }
    return [
      { label: 'Total sessions', value: String(analytics.total_sessions), note: 'All saved practice sessions' },
      { label: 'Completed', value: String(analytics.completed_sessions), note: 'Finished sessions' },
      {
        label: 'Accuracy',
        value: analytics.total_questions > 0
          ? `${analytics.correct_answers} / ${analytics.total_questions}`
          : 'No data',
        note: analytics.total_questions > 0
          ? `${this.formatPercent(analytics.accuracy)} overall`
          : 'Complete a session to see results',
      },
      {
        label: 'Average time',
        value: this.formatTime(analytics.average_elapsed_seconds),
        note: analytics.last_completed_at === null
          ? 'No completed sessions yet'
          : `Last completed ${this.formatDate(analytics.last_completed_at)}`,
      },
    ];
  });

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
      return 'No data';
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  protected formatPercent(ratio: number): string {
    return `${Math.round(ratio * 100)}%`;
  }

  protected formatDate(value: string | null): string {
    if (value === null) {
      return 'No data';
    }
    return new Intl.DateTimeFormat('en-CA', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(new Date(value));
  }

  private loadLearnerData(): void {
    forkJoin({
      analytics: this.api.learnerAnalytics(this.learnerId),
      sessions: this.api.learnerSessions(this.learnerId),
    }).subscribe({
      next: ({ analytics, sessions }) => {
        this.analytics.set(analytics);
        this.sessions.set(sessions);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load learner history and statistics.');
        this.loading.set(false);
      },
    });
  }

  private loadSessions(): void {
    this.loadLearnerData();
  }
}
