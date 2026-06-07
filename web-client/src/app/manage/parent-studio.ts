import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
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
  PluginSettingsValue,
  PracticeApi,
  PracticeRequest,
  SavedSession,
} from '../core/practice-api';
import { PluginSettingsForm } from './plugin-settings-form';

@Component({
  selector: 'app-parent-studio',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    MatSlideToggleModule,
    PluginSettingsForm,
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
  protected subject = 'Math';
  protected pluginId = 'multiply_by_11';
  protected questionCount = 10;
  protected pluginSettings: PluginSettingsValue = {};
  protected feedbackMode = 'immediate';
  protected showTimer = true;
  protected locale = 'en-CA';

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.api.catalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.questionCount = catalog.question_counts[0];
        this.selectSubject(catalog.plugins[0].subject);
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
    if (!this.nickname.trim() || this.hasEmptyMultipleChoiceSetting()) {
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
        return this.api.createSession(savedLearner.id, this.sessionRequest());
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
    const plugin = this.selectedPlugin();
    if (plugin) {
      this.subject = plugin.subject;
      this.locale = plugin.default_locale;
    }
    this.pluginSettings = this.defaultPluginSettings(plugin);
  }

  protected selectSubject(subject: string): void {
    this.subject = subject;
    const firstPlugin = this.pluginsForSubject()[0];
    if (firstPlugin) {
      this.selectPlugin(firstPlugin.plugin);
    }
  }

  protected subjects(): string[] {
    return [...new Set((this.catalog()?.plugins ?? []).map((plugin) => plugin.subject))];
  }

  protected pluginsForSubject(): OnlinePlugin[] {
    return (this.catalog()?.plugins ?? []).filter((plugin) => plugin.subject === this.subject);
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

  protected updatePluginSettings(settings: PluginSettingsValue): void {
    this.pluginSettings = settings;
  }

  private sessionRequest(): PracticeRequest {
    return {
      plugin: this.pluginId,
      plugin_settings: this.pluginSettings,
      question_count: this.questionCount,
      requested_locale: this.locale,
      feedback_mode: this.feedbackMode,
      show_timer: this.showTimer,
    };
  }

  private defaultPluginSettings(plugin: OnlinePlugin | undefined): PluginSettingsValue {
    const settings: PluginSettingsValue = {};
    for (const setting of plugin?.settings ?? []) {
      settings[setting.name] = [...setting.default];
    }
    return settings;
  }

  private hasEmptyMultipleChoiceSetting(): boolean {
    return (this.selectedPlugin()?.settings ?? []).some((setting) => (
      setting.control === 'multiple_choice' && (this.pluginSettings[setting.name] ?? []).length === 0
    ));
  }
}
