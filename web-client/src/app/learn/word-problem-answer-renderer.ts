import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AnswerValue, JsonObject, StudentQuestion } from '../core/practice-api';

interface WordProblemAnswerField {
  key: string;
  label: string;
  value_type: string;
  unit?: string;
  required?: boolean;
}

interface WorkArea {
  enabled?: boolean;
  required?: boolean;
  label?: string;
}

@Component({
  selector: 'app-word-problem-answer-renderer',
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './word-problem-answer-renderer.html',
  styleUrl: './word-problem-answer-renderer.scss',
})
export class WordProblemAnswerRenderer implements OnChanges {
  @Input({ required: true }) question!: StudentQuestion;
  @Input() disabled = false;
  @Input() submitting = false;
  @Output() readonly answerChange = new EventEmitter<AnswerValue>();
  @Output() readonly submitAnswer = new EventEmitter<void>();

  protected readonly values: Record<string, string> = {};
  protected work = '';
  protected validationMessage = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['question'] && !changes['question'].firstChange) {
      for (const key of Object.keys(this.values)) {
        delete this.values[key];
      }
      this.work = '';
      this.validationMessage = '';
      this.answerChange.emit(null);
    }
  }

  protected fields(): WordProblemAnswerField[] {
    const schema = this.question.public_payload?.['answer_schema'];
    if (!schema || typeof schema !== 'object') {
      return [];
    }
    const fields = (schema as JsonObject)['fields'];
    return Array.isArray(fields) ? fields as unknown as WordProblemAnswerField[] : [];
  }

  protected workArea(): WorkArea {
    const workArea = this.question.public_payload?.['work_area'];
    return workArea && typeof workArea === 'object' ? workArea as WorkArea : {};
  }

  protected workAreaEnabled(): boolean {
    return this.workArea().enabled === true;
  }

  protected workAreaLabel(): string {
    return this.workArea().label ?? 'Show your work';
  }

  protected updateAnswer(): void {
    this.validationMessage = '';
    this.answerChange.emit(this.buildAnswer());
  }

  protected submit(): void {
    const error = this.validate();
    if (error) {
      this.validationMessage = error;
      return;
    }
    this.answerChange.emit(this.buildAnswer());
    this.submitAnswer.emit();
  }

  private validate(): string {
    for (const field of this.fields()) {
      const raw = (this.values[field.key] ?? '').trim();
      if (field.required !== false && raw === '') {
        return `${field.label} is required.`;
      }
      if (raw !== '' && field.value_type === 'integer' && !/^-?\d+$/.test(raw)) {
        return `${field.label} must be an integer.`;
      }
    }
    if (this.workArea().required === true && this.work.trim() === '') {
      return `${this.workAreaLabel()} is required.`;
    }
    return '';
  }

  private buildAnswer(): JsonObject {
    const values: Record<string, number | string> = {};
    for (const field of this.fields()) {
      const raw = (this.values[field.key] ?? '').trim();
      if (field.value_type === 'integer' && raw !== '') {
        values[field.key] = Number(raw);
      } else {
        values[field.key] = raw;
      }
    }
    return {
      values,
      work: this.work,
    };
  }
}
