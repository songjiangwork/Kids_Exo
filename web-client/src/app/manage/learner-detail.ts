import { Component, OnInit, computed, signal } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import {
  Learner,
  LearnerAnalytics,
  OnlineCatalog,
  PracticeApi,
  PracticeRequest,
  PracticeResults,
  SavedSession,
  SessionSummary,
} from '../core/practice-api';

@Component({
  selector: 'app-learner-detail',
  imports: [MatButtonModule, MatCardModule, MatProgressSpinnerModule, RouterLink],
  templateUrl: './learner-detail.html',
  styleUrl: './learner-detail.scss',
})
export class LearnerDetail implements OnInit {
  protected readonly learner = signal<Learner | null>(null);
  protected readonly catalog = signal<OnlineCatalog | null>(null);
  protected readonly analytics = signal<LearnerAnalytics | null>(null);
  protected readonly sessions = signal<SessionSummary[]>([]);
  protected readonly createdSession = signal<SavedSession | null>(null);
  protected readonly selectedResults = signal<PracticeResults | null>(null);
  protected readonly loading = signal(true);
  protected readonly creatingPracticePlugin = signal<string | null>(null);
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
        this.loadLearnerData();
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

  protected createPracticeFromPlugin(pluginId: string): void {
    const catalog = this.catalog();
    if (catalog === null) {
      this.error.set('Practice choices are still loading.');
      return;
    }
    const plugin = catalog.plugins.find((entry) => entry.plugin === pluginId);
    if (plugin === undefined) {
      this.error.set('This practice type is not available online yet.');
      return;
    }
    this.error.set('');
    this.createdSession.set(null);
    this.creatingPracticePlugin.set(pluginId);
    this.api.createSession(this.learnerId, this.defaultPracticeRequest(pluginId)).subscribe({
      next: (session) => {
        this.createdSession.set(session);
        this.creatingPracticePlugin.set(null);
        this.refreshLearnerInsights();
      },
      error: () => {
        this.error.set('Could not create a follow-up practice session.');
        this.creatingPracticePlugin.set(null);
      },
    });
  }

  protected reviewResults(session: SessionSummary): void {
    if (session.status !== 'completed') {
      return;
    }
    this.error.set('');
    this.api.parentResults(this.learnerId, session.id).subscribe({
      next: (results) => this.selectedResults.set(results),
      error: () => this.error.set('Could not load these results.'),
    });
  }

  protected isCreatingPractice(pluginId: string): boolean {
    return this.creatingPracticePlugin() === pluginId;
  }

  protected pluginTitle(pluginId: string): string {
    return this.catalog()?.plugins.find((plugin) => plugin.plugin === pluginId)?.title ?? pluginId;
  }

  private loadLearnerData(): void {
    this.api.catalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.refreshLearnerInsights();
      },
      error: () => {
        this.error.set('Could not load practice choices.');
        this.loading.set(false);
      },
    });
  }

  private refreshLearnerInsights(): void {
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

  private defaultPracticeRequest(pluginId: string): PracticeRequest {
    const plugin = this.catalog()?.plugins.find((entry) => entry.plugin === pluginId);
    if (plugin === undefined) {
      throw new Error(`Unknown plugin: ${pluginId}`);
    }
    const pluginSettings = Object.fromEntries(
      plugin.settings.map((setting) => [setting.name, [...setting.default]]),
    );
    return {
      plugin: pluginId,
      plugin_settings: pluginSettings,
      question_count: 10,
      requested_locale: plugin.default_locale,
      feedback_mode: 'immediate',
      show_timer: true,
    };
  }
}
