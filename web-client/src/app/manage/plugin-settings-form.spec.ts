import { Component } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { PluginSettingsForm } from './plugin-settings-form';
import { PluginSetting, PluginSettingsValue } from '../core/practice-api';

@Component({
  imports: [PluginSettingsForm],
  template: `
    <app-plugin-settings-form
      [settings]="settings"
      [value]="value"
      (valueChange)="value = $event"
    />
  `,
})
class HostComponent {
  settings: PluginSetting[] = [
    {
      name: 'multiplicand_digits',
      label: 'Number size',
      control: 'single_choice',
      default: [2],
      options: [
        { value: 2, label: 'Two digits' },
        { value: 3, label: 'Three digits' },
      ],
    },
    {
      name: 'strategies',
      label: 'Include',
      control: 'multiple_choice',
      default: ['no_carrying'],
      options: [
        { value: 'no_carrying', label: 'Without carrying' },
        { value: 'with_carrying', label: 'With carrying' },
      ],
    },
  ];
  value: PluginSettingsValue = {};
}

describe('PluginSettingsForm', () => {
  async function createFixture(): Promise<ComponentFixture<HostComponent>> {
    await TestBed.configureTestingModule({
      imports: [HostComponent, NoopAnimationsModule],
    }).compileComponents();

    const fixture = TestBed.createComponent(HostComponent);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  it('renders generic plugin settings with defaults', async () => {
    const fixture = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Number size');
    expect(fixture.nativeElement.textContent).toContain('Include');
    expect(fixture.nativeElement.textContent).toContain('Without carrying');
    expect(fixture.nativeElement.textContent).toContain('With carrying');

    const checkboxes = fixture.debugElement.queryAll(By.css('mat-checkbox input'));
    expect((checkboxes[0].nativeElement as HTMLInputElement).checked).toBe(true);
    expect((checkboxes[1].nativeElement as HTMLInputElement).checked).toBe(false);
  });

  it('emits updated single choice values', async () => {
    const fixture = await createFixture();
    const form = fixture.debugElement.query(By.directive(PluginSettingsForm)).componentInstance as PluginSettingsForm;

    (form as any).updateSingle(fixture.componentInstance.settings[0], 3);
    fixture.detectChanges();

    expect(fixture.componentInstance.value).toEqual({
      multiplicand_digits: [3],
      strategies: ['no_carrying'],
    });
  });

  it('emits updated multiple choice values', async () => {
    const fixture = await createFixture();
    const checkbox = fixture.debugElement.queryAll(By.css('mat-checkbox input'))[1];

    (checkbox.nativeElement as HTMLInputElement).click();
    fixture.detectChanges();

    expect(fixture.componentInstance.value).toEqual({
      multiplicand_digits: [2],
      strategies: ['no_carrying', 'with_carrying'],
    });
  });
});
