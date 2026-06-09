import { Component, EventEmitter, Input, Output } from '@angular/core';
import { StudentQuestion } from '../core/practice-api';
import { ChoiceAnswerRenderer } from './choice-answer-renderer';
import { NumericAnswerRenderer } from './numeric-answer-renderer';

@Component({
  selector: 'app-question-renderer-host',
  imports: [
    ChoiceAnswerRenderer,
    NumericAnswerRenderer,
  ],
  templateUrl: './question-renderer-host.html',
})
export class QuestionRendererHost {
  @Input({ required: true }) question!: StudentQuestion;
  @Input() answer: string | number | null = '';
  @Input() disabled = false;
  @Input() submitting = false;
  @Output() readonly answerChange = new EventEmitter<string | number | null>();
  @Output() readonly submitAnswer = new EventEmitter<void>();
  @Output() readonly submitChoice = new EventEmitter<number>();

  protected rendererType(): string {
    if (this.question.renderer_type) {
      return this.question.renderer_type;
    }
    return (this.question.choices?.length ?? 0) > 0
      ? 'multiple_choice'
      : 'numeric_answer';
  }
}
