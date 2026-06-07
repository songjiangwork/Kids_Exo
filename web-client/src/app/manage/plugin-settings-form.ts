import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import {
  PluginSetting,
  PluginSettingsValue,
  PluginSettingValue,
} from '../core/practice-api';

@Component({
  selector: 'app-plugin-settings-form',
  imports: [
    FormsModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
  ],
  templateUrl: './plugin-settings-form.html',
  styleUrl: './plugin-settings-form.scss',
})
export class PluginSettingsForm implements OnChanges {
  @Input() settings: PluginSetting[] = [];
  @Input() value: PluginSettingsValue = {};
  @Output() readonly valueChange = new EventEmitter<PluginSettingsValue>();

  protected currentValue: PluginSettingsValue = {};

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['settings'] || changes['value']) {
      this.currentValue = this.withDefaults(this.settings, this.value);
    }
  }

  protected selectedValue(setting: PluginSetting): PluginSettingValue | null {
    return this.currentValue[setting.name]?.[0] ?? null;
  }

  protected booleanValue(setting: PluginSetting): boolean {
    return Boolean(this.currentValue[setting.name]?.[0] ?? false);
  }

  protected textValue(setting: PluginSetting): string {
    const value = this.currentValue[setting.name]?.[0];
    return value === undefined || value === null ? '' : String(value);
  }

  protected numberValue(setting: PluginSetting): number | null {
    const value = this.currentValue[setting.name]?.[0];
    return typeof value === 'number' ? value : null;
  }

  protected isChecked(setting: PluginSetting, option: PluginSettingValue): boolean {
    return (this.currentValue[setting.name] ?? []).some((value) => value === option);
  }

  protected updateSingle(setting: PluginSetting, value: PluginSettingValue): void {
    this.updateSetting(setting.name, [value]);
  }

  protected updateBoolean(setting: PluginSetting, checked: boolean): void {
    this.updateSetting(setting.name, [checked]);
  }

  protected updateText(setting: PluginSetting, value: string): void {
    this.updateSetting(setting.name, [value]);
  }

  protected updateNumber(setting: PluginSetting, value: string): void {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      this.updateSetting(setting.name, [parsed]);
      return;
    }
    this.updateSetting(setting.name, []);
  }

  protected updateMultiple(setting: PluginSetting, option: PluginSettingValue, checked: boolean): void {
    const values = new Set(this.currentValue[setting.name] ?? []);
    if (checked) {
      values.add(option);
    } else {
      values.delete(option);
    }
    this.updateSetting(setting.name, [...values]);
  }

  private updateSetting(name: string, values: PluginSettingValue[]): void {
    this.currentValue = {
      ...this.currentValue,
      [name]: values,
    };
    this.valueChange.emit(this.currentValue);
  }

  private withDefaults(settings: PluginSetting[], value: PluginSettingsValue): PluginSettingsValue {
    const next: PluginSettingsValue = {};
    for (const setting of settings) {
      next[setting.name] = [...(value[setting.name] ?? setting.default ?? [])];
    }
    return next;
  }
}
