import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-numeric-answer-renderer',
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './numeric-answer-renderer.html',
  styleUrl: './numeric-answer-renderer.scss',
})
export class NumericAnswerRenderer {
  @Input() answer: string | number | null = '';
  @Input() disabled = false;
  @Input() submitting = false;
  @Output() readonly answerChange = new EventEmitter<string | number | null>();
  @Output() readonly submitAnswer = new EventEmitter<void>();
}
