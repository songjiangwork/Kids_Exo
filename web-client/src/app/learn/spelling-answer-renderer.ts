import { Component, ElementRef, EventEmitter, Input, Output, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AnswerValue, StudentQuestion } from '../core/practice-api';

interface ArticleHint {
  article: string;
  gender?: string;
  number?: string;
  display_text?: string;
  full_display_text?: string;
  mode?: string;
  teaches_gender?: boolean;
}

@Component({
  selector: 'app-spelling-answer-renderer',
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './spelling-answer-renderer.html',
  styleUrl: './spelling-answer-renderer.scss',
})
export class SpellingAnswerRenderer {
  private currentQuestion!: StudentQuestion;

  @Input({ required: true })
  set question(value: StudentQuestion) {
    if (this.currentQuestion && this.currentQuestion.identifier !== value.identifier) {
      this.text = '';
      this.validationMessage = '';
      this.answerChange.emit(null);
    }
    this.currentQuestion = value;
  }

  get question(): StudentQuestion {
    return this.currentQuestion;
  }

  @Input() disabled = false;
  @Input() submitting = false;
  @Output() readonly answerChange = new EventEmitter<AnswerValue>();
  @Output() readonly submitAnswer = new EventEmitter<void>();
  @ViewChild('spellingInput') private spellingInput?: ElementRef<HTMLInputElement>;

  protected text = '';
  protected validationMessage = '';

  protected inputLabel(): string {
    return this.payloadString('input_label') || 'Answer';
  }

  protected promptMode(): string {
    return this.payloadString('prompt_mode') || 'translation';
  }

  protected translation(): string {
    return this.payloadString('translation');
  }

  protected audioUrl(): string {
    return this.payloadString('audio_url');
  }

  protected articleHint(): ArticleHint | null {
    const value = this.question.public_payload?.['article_hint'];
    if (!value || typeof value !== 'object' || Array.isArray(value)) {
      return null;
    }
    const article = (value as Record<string, unknown>)['article'];
    return typeof article === 'string' && article ? { ...(value as ArticleHint), article } : null;
  }

  protected accentKeys(): string[] {
    const keys = this.question.public_payload?.['accent_keys'];
    return Array.isArray(keys) ? keys.map(String) : [];
  }

  protected showAudio(): boolean {
    return Boolean(this.audioUrl()) && this.promptMode() !== 'translation';
  }

  protected showTranslation(): boolean {
    return Boolean(this.translation()) && this.promptMode() !== 'dictation';
  }

  protected updateAnswer(): void {
    this.validationMessage = '';
    this.answerChange.emit({ text: this.text });
  }

  protected insertCharacter(character: string): void {
    const input = this.spellingInput?.nativeElement;
    if (!input) {
      this.text = `${this.text}${character}`;
      this.updateAnswer();
      return;
    }
    const start = input.selectionStart ?? this.text.length;
    const end = input.selectionEnd ?? this.text.length;
    this.text = `${this.text.slice(0, start)}${character}${this.text.slice(end)}`;
    this.updateAnswer();
    queueMicrotask(() => {
      input.focus();
      input.setSelectionRange(start + character.length, start + character.length);
    });
  }

  protected playAudio(): void {
    const audioUrl = this.audioUrl();
    if (!audioUrl) {
      return;
    }
    void new Audio(audioUrl).play();
  }

  protected submit(): void {
    if (!this.text.trim()) {
      this.validationMessage = `Please enter ${this.inputLabel()}.`;
      return;
    }
    this.answerChange.emit({ text: this.text.trim() });
    this.submitAnswer.emit();
  }

  private payloadString(key: string): string {
    const value = this.question.public_payload?.[key];
    return typeof value === 'string' ? value : '';
  }
}
