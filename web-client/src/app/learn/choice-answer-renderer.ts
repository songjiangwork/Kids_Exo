import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-choice-answer-renderer',
  imports: [MatButtonModule],
  templateUrl: './choice-answer-renderer.html',
  styleUrl: './choice-answer-renderer.scss',
})
export class ChoiceAnswerRenderer {
  @Input() choices: string[] = [];
  @Input() disabled = false;
  @Output() readonly submitChoice = new EventEmitter<number>();
}
