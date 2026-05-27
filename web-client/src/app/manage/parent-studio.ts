import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { switchMap } from 'rxjs';
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
import { OnlineCatalog, OnlinePlugin, PluginSetting, PracticeApi, SavedSession } from '../core/practice-api';

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

  protected nickname = 'Alex';
  protected pluginId = 'multiply_by_11';
  protected questionCount = 10;
  protected digits = 2;
  protected selectedStrategies = new Set<string>();
  protected feedbackMode = 'immediate';
  protected showTimer = false;
  protected locale = 'en-CA';

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.api.catalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.questionCount = catalog.question_counts[0];
        this.pluginId = catalog.plugins[0].plugin;
        const digitDefault = this.setting('multiplicand_digits')?.default[0];
        this.digits = Number(digitDefault ?? 2);
        this.selectedStrategies = new Set(
          (this.setting('strategies')?.default ?? []).map(String),
        );
        this.loading.set(false);
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
    this.api.createLearner(this.nickname.trim()).pipe(
      switchMap((learner) => this.api.createSession(learner.id, {
        plugin: this.pluginId,
        plugin_settings: {
          multiplicand_digits: [this.digits],
          strategies,
        },
        question_count: this.questionCount,
        requested_locale: this.locale,
        feedback_mode: this.feedbackMode,
        show_timer: this.showTimer,
      })),
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
}
