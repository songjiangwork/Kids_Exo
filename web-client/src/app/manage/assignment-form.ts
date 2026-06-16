import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { provideNativeDateAdapter } from '@angular/material/core';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import {
  AssignmentCreateRequest,
  OnlineCatalog,
  OnlinePlugin,
  PluginSettingsValue,
} from '../core/practice-api';
import { PluginSettingsForm } from './plugin-settings-form';

interface PracticeTypeGroup {
  subject: string;
  category: string;
  label: string;
  plugins: OnlinePlugin[];
}

@Component({
  selector: 'app-assignment-form',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatDatepickerModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    PluginSettingsForm,
  ],
  providers: [provideNativeDateAdapter()],
  templateUrl: './assignment-form.html',
  styleUrl: './assignment-form.scss',
})
export class AssignmentForm implements OnChanges {
  @Input() catalog: OnlineCatalog | null = null;
  @Input() saving = false;
  @Input() sourceType = 'learner_added';
  @Input() createdByRole = 'learner';
  @Input() submitLabel = 'Create homework';
  @Output() readonly createAssignment = new EventEmitter<AssignmentCreateRequest>();

  protected title = '';
  protected description = '';
  protected selectedPluginId = '';
  protected questionCount = 10;
  protected feedbackMode = 'immediate';
  protected dueDate: Date | null = null;
  protected showTimer = true;
  protected pluginSettings: PluginSettingsValue = {};
  private titleWasEdited = false;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['catalog'] && this.selectedPluginId === '') {
      const firstPlugin = this.webPracticePlugins[0];
      if (firstPlugin !== undefined) {
        this.selectPlugin(firstPlugin.plugin);
      }
    }
  }

  protected get webPracticePlugins(): OnlinePlugin[] {
    return (this.catalog?.plugins ?? []).filter((plugin) =>
      (plugin.supported_delivery_modes ?? []).includes('web_practice'),
    );
  }

  protected get practiceTypeGroups(): PracticeTypeGroup[] {
    const groups = new Map<string, PracticeTypeGroup>();
    for (const plugin of this.webPracticePlugins) {
      const subject = plugin.subject || 'Other';
      const category = plugin.category || 'Other';
      const key = `${subject}::${category}`;
      const group = groups.get(key) ?? {
        subject,
        category,
        label: subject === 'Other' && category === 'Other' ? 'Other' : `${subject} / ${category}`,
        plugins: [],
      };
      group.plugins.push(plugin);
      groups.set(key, group);
    }
    return Array.from(groups.values())
      .map((group) => ({
        ...group,
        plugins: [...group.plugins].sort((left, right) => left.title.localeCompare(right.title)),
      }))
      .sort((left, right) =>
        left.subject.localeCompare(right.subject) || left.category.localeCompare(right.category),
      );
  }

  protected get selectedPlugin(): OnlinePlugin | undefined {
    return this.webPracticePlugins.find((plugin) => plugin.plugin === this.selectedPluginId);
  }

  protected selectPlugin(pluginId: string): void {
    this.selectedPluginId = pluginId;
    const plugin = this.selectedPlugin;
    this.pluginSettings = Object.fromEntries(
      (plugin?.settings ?? []).map((setting) => [setting.name, [...setting.default]]),
    );
    if (plugin !== undefined && !this.titleWasEdited) {
      this.title = this.defaultTitleFor(plugin);
    }
  }

  protected updateTitle(value: string): void {
    this.title = value;
    this.titleWasEdited = value.trim() !== this.defaultTitleFor(this.selectedPlugin);
  }

  protected updatePluginSettings(value: PluginSettingsValue): void {
    this.pluginSettings = value;
  }

  protected submit(): void {
    const plugin = this.selectedPlugin;
    if (plugin === undefined || this.title.trim() === '') {
      return;
    }
    this.createAssignment.emit({
      title: this.title.trim(),
      description: this.description.trim(),
      source_type: this.sourceType,
      due_at: this.formatDueDate(),
      created_by_role: this.createdByRole,
      items: [
        {
          item_type: 'practice_plugin',
          plugin: plugin.plugin,
          plugin_settings: this.pluginSettings,
          question_count: this.questionCount,
          feedback_mode: this.feedbackMode,
          show_timer: this.showTimer,
          required: true,
        },
      ],
    });
  }

  private formatDueDate(): string | null {
    if (this.dueDate === null) {
      return null;
    }
    const dueAt = new Date(
      this.dueDate.getFullYear(),
      this.dueDate.getMonth(),
      this.dueDate.getDate(),
      12,
      0,
      0,
      0,
    );
    return dueAt.toISOString();
  }

  private defaultTitleFor(plugin: OnlinePlugin | undefined): string {
    return plugin?.title ?? '';
  }
}
