import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import {
  Learner,
  OnlineCatalog,
  OnlinePlugin,
  PluginSetting,
  PracticeApi,
  PracticeRequest,
  SavedSession,
} from '../core/practice-api';

@Component({
  selector: 'app-parent-studio',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSlideToggleModule,
    RouterLink,
  ],
  templateUrl: './parent-studio.html',
  styleUrl: './parent-studio.scss',
})
export class ParentStudio implements OnInit {
  protected readonly catalog = signal<OnlineCatalog | null>(null);
  protected readonly loading = signal(true);
  protected readonly saving = signal(false);
  protected readonly error = signal('');
  protected readonly createdSession = signal<SavedSession | null>(null);
  protected readonly learners = signal<Learner[]>([]);

  protected nickname = 'Alex';
  protected learnerId: number | null = null;
  protected pluginId = 'multiply_by_11';
  protected questionCount = 10;
  protected digits = 2;
  protected selectedStrategies = new Set<string>();
  protected feedbackMode = 'immediate';
  protected showTimer = true;
  protected locale = 'en-CA';

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.api.catalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.questionCount = catalog.question_counts[0];
        this.selectPlugin(catalog.plugins[0].plugin);
        this.api.learners().subscribe({
          next: (learners) => {
            this.learners.set(learners);
            if (learners.length > 0) {
              const latestLearner = learners[learners.length - 1];
              this.learnerId = latestLearner.id;
              this.nickname = latestLearner.nickname;
            }
            this.loading.set(false);
          },
          error: () => {
            this.error.set('Could not load learners.');
            this.loading.set(false);
          },
        });
      },
      error: () => {
        this.error.set('Could not load practice choices. Is the API running?');
        this.loading.set(false);
      },
    });
  }

  protected startPractice(): void {
    const strategies = [...this.selectedStrategies];
    if (!this.nickname.trim() || strategies.length === 0) {
      this.error.set('Enter a learner name and choose at least one question type.');
      return;
    }
    this.error.set('');
    this.saving.set(true);
    this.createdSession.set(null);
    const learner = this.learnerId === null
      ? this.api.createLearner(this.nickname.trim())
      : of({ id: this.learnerId, nickname: this.nickname, active: true });
    learner.pipe(
      switchMap((savedLearner) => {
        this.learnerId = savedLearner.id;
        if (!this.learners().some((entry) => entry.id === savedLearner.id)) {
          this.learners.update((entries) => [...entries, savedLearner]);
        }
        return this.api.createSession(savedLearner.id, this.sessionRequest(strategies));
      }),
    ).subscribe({
      next: (session) => {
        this.createdSession.set(session);
        this.saving.set(false);
      },
      error: () => {
        this.error.set('Could not create this practice session.');
        this.saving.set(false);
      },
    });
  }

  protected selectLearner(learnerId: number | null): void {
    this.learnerId = learnerId;
    this.createdSession.set(null);
    if (learnerId === null) {
      this.nickname = '';
      return;
    }
    const learner = this.learners().find((entry) => entry.id === learnerId);
    this.nickname = learner?.nickname ?? '';
  }

  protected selectPlugin(pluginId: string): void {
    this.pluginId = pluginId;
    const digitDefault = this.setting('multiplicand_digits')?.default[0];
    this.digits = Number(digitDefault ?? 2);
    this.selectedStrategies = new Set(
      (this.setting('strategies')?.default ?? []).map(String),
    );
  }

  protected formatTime(seconds: number | null): string {
    if (seconds === null) {
      return '';
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  protected selectedPlugin(): OnlinePlugin | undefined {
    return this.catalog()?.plugins.find((plugin) => plugin.plugin === this.pluginId);
  }

  protected setting(name: string): PluginSetting | undefined {
    return this.selectedPlugin()?.settings.find((setting) => setting.name === name);
  }

  protected isSelectedStrategy(strategy: string): boolean {
    return this.selectedStrategies.has(strategy);
  }

  protected toggleStrategy(strategy: string, checked: boolean): void {
    const next = new Set(this.selectedStrategies);
    if (checked) {
      next.add(strategy);
    } else {
      next.delete(strategy);
    }
    this.selectedStrategies = next;
  }

  private sessionRequest(strategies: string[]): PracticeRequest {
    const pluginSettings: Record<string, Array<number | string>> = {};
    if (this.setting('multiplicand_digits')) {
      pluginSettings['multiplicand_digits'] = [this.digits];
    }
    if (this.setting('strategies')) {
      pluginSettings['strategies'] = strategies;
    }
    return {
      plugin: this.pluginId,
      plugin_settings: pluginSettings,
      question_count: this.questionCount,
      requested_locale: this.locale,
      feedback_mode: this.feedbackMode,
      show_timer: this.showTimer,
    };
  }
}
