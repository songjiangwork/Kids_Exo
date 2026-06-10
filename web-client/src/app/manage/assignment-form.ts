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

  protected get selectedPlugin(): OnlinePlugin | undefined {
    return this.webPracticePlugins.find((plugin) => plugin.plugin === this.selectedPluginId);
  }

  protected selectPlugin(pluginId: string): void {
    this.selectedPluginId = pluginId;
    const plugin = this.selectedPlugin;
    this.pluginSettings = Object.fromEntries(
      (plugin?.settings ?? []).map((setting) => [setting.name, [...setting.default]]),
    );
    if (plugin !== undefined && this.title.trim() === '') {
      this.title = `${plugin.title} homework`;
    }
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
}
