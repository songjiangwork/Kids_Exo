import { Component, ElementRef, OnDestroy, OnInit, ViewChild, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { Subscription } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { PracticeApi, PracticeResults, StudentSession } from '../core/practice-api';

type ScratchMode = 'type' | 'draw';
interface DrawPoint {
  x: number;
  y: number;
}

interface SpeechVoiceChoice {
  id: string;
  label: string;
  voice: SpeechSynthesisVoice | null;
}

@Component({
  selector: 'app-student-practice',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatSelectModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './student-practice.html',
  styleUrl: './student-practice.scss',
})
export class StudentPractice implements OnInit, OnDestroy {
  @ViewChild('scratchCanvas') private scratchCanvas?: ElementRef<HTMLCanvasElement>;

  protected readonly session = signal<StudentSession | null>(null);
  protected readonly loading = signal(true);
  protected readonly submitting = signal(false);
  protected readonly error = signal('');
  protected readonly index = signal(0);
  protected readonly feedback = signal<'correct' | 'incorrect' | 'saved' | null>(null);
  protected readonly complete = signal(false);
  protected readonly results = signal<PracticeResults | null>(null);
  protected readonly elapsedSeconds = signal(0);
  protected readonly timerPaused = signal(false);
  protected readonly timerUpdating = signal(false);
  protected answer: string | number | null = '';
  protected readonly scratchPadOpen = signal(false);
  protected readonly scratchPad = signal('');
  protected readonly scratchMode = signal<ScratchMode>('type');
  protected readonly drawStrokes = signal<DrawPoint[][]>([]);
  protected readonly speechVoices = signal<SpeechVoiceChoice[]>([]);
  protected selectedSpeechVoiceId = 'auto';

  protected readonly question = computed(() => this.session()?.questions[this.index()]);
  protected readonly progress = computed(() => {
    const total = this.session()?.questions.length ?? 1;
    return (this.index() / total) * 100;
  });

  private token = '';
  private routeSubscription?: Subscription;
  private timer?: ReturnType<typeof setInterval>;
  private activeStroke: DrawPoint[] | null = null;
  private speechVoicesLoaded = false;

  constructor(
    private readonly route: ActivatedRoute,
    private readonly api: PracticeApi,
  ) {}

  ngOnInit(): void {
    this.loadSpeechVoices();
    this.routeSubscription = this.route.paramMap.subscribe((params) => {
      this.token = params.get('token') ?? '';
      this.api.studentSession(this.token).subscribe({
        next: (session) => {
          this.stopLocalTimer();
          this.session.set(session);
          this.elapsedSeconds.set(session.active_elapsed_seconds);
          this.timerPaused.set(session.timer_status !== 'running');
          this.resumeSession(session);
          this.loading.set(false);
          if (this.shouldRunLocalTimer(session)) {
            this.startLocalTimer();
          }
        },
        error: () => {
          this.error.set('This practice link is not available.');
          this.loading.set(false);
        },
      });
    });
  }

  ngOnDestroy(): void {
    this.routeSubscription?.unsubscribe();
    this.stopLocalTimer();
  }

  protected checkAnswer(): void {
    const question = this.question();
    const normalizedAnswer = this.answer === null ? '' : String(this.answer).trim();
    if (!question || normalizedAnswer === '' || this.isPracticePaused()) {
      return;
    }
    this.submitting.set(true);
    this.api.submitAnswer(this.token, question.identifier, normalizedAnswer).subscribe({
      next: (result) => {
        if (result.is_correct === true) {
          this.feedback.set('correct');
        } else if (result.is_correct === false) {
          this.feedback.set('incorrect');
        } else {
          this.feedback.set('saved');
        }
        this.submitting.set(false);
      },
      error: () => {
        this.error.set('Your answer could not be saved.');
        this.submitting.set(false);
      },
    });
  }

  protected submitChoice(choiceIndex: number): void {
    if (this.feedback() !== null || this.isPracticePaused()) {
      return;
    }
    this.answer = choiceIndex;
    this.checkAnswer();
  }

  protected playQuestionAudio(): void {
    const question = this.question();
    if (
      !question?.speech_text ||
      window.speechSynthesis === undefined ||
      typeof SpeechSynthesisUtterance === 'undefined'
    ) {
      return;
    }
    this.loadSpeechVoices();
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(question.speech_text);
    const voice = this.selectedSpeechVoice(question.speech_locale ?? 'fr-CA');
    if (voice) {
      utterance.voice = voice;
      utterance.lang = voice.lang;
    } else {
      utterance.lang = question.speech_locale ?? 'fr-CA';
    }
    utterance.rate = 0.82;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  }

  protected nextQuestion(): void {
    const total = this.session()?.questions.length ?? 0;
    if (this.index() + 1 >= total) {
      this.loadResults();
      return;
    }
    this.index.update((value) => value + 1);
    this.feedback.set(null);
    this.answer = '';
    this.clearAllScratchWork();
  }

  protected timerText(): string {
    return this.formatSeconds(this.elapsedSeconds());
  }

  protected resultTimeText(): string {
    return this.formatSeconds(this.results()?.elapsed_seconds ?? 0);
  }

  protected isPracticePaused(): boolean {
    return Boolean(this.session()?.show_timer && this.timerPaused());
  }

  protected toggleScratchPad(): void {
    this.scratchPadOpen.update((isOpen) => !isOpen);
    if (this.scratchMode() === 'draw') {
      queueMicrotask(() => this.redrawScratchCanvas());
    }
  }

  protected clearScratchPad(): void {
    if (this.scratchMode() === 'draw') {
      this.drawStrokes.set([]);
      this.activeStroke = null;
      this.redrawScratchCanvas();
      return;
    }
    this.scratchPad.set('');
  }

  protected setScratchMode(mode: ScratchMode): void {
    this.scratchMode.set(mode);
    if (mode === 'draw') {
      queueMicrotask(() => this.redrawScratchCanvas());
    }
  }

  protected hasScratchContent(): boolean {
    return this.scratchMode() === 'draw'
      ? this.drawStrokes().length > 0
      : this.scratchPad().length > 0;
  }

  protected startDrawing(event: PointerEvent): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    canvas.setPointerCapture(event.pointerId);
    this.activeStroke = [this.canvasPoint(event, canvas)];
    this.drawStrokes.update((strokes) => [...strokes, this.activeStroke ?? []]);
    this.redrawScratchCanvas();
  }

  protected continueDrawing(event: PointerEvent): void {
    if (!this.activeStroke) {
      return;
    }
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    this.activeStroke.push(this.canvasPoint(event, canvas));
    this.redrawScratchCanvas();
  }

  protected stopDrawing(event: PointerEvent): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (canvas?.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }
    this.activeStroke = null;
  }

  protected pauseTimer(): void {
    if (!this.session()?.show_timer || this.timerPaused() || this.timerUpdating()) {
      return;
    }
    this.timerUpdating.set(true);
    this.api.pauseStudentTimer(this.token).subscribe({
      next: (timerStatus) => {
        this.stopLocalTimer();
        this.elapsedSeconds.set(timerStatus.active_elapsed_seconds);
        this.timerPaused.set(true);
        this.timerUpdating.set(false);
      },
      error: () => {
        this.error.set('The timer could not be paused.');
        this.timerUpdating.set(false);
      },
    });
  }

  protected resumeTimer(): void {
    if (!this.session()?.show_timer || !this.timerPaused() || this.timerUpdating()) {
      return;
    }
    this.timerUpdating.set(true);
    this.api.resumeStudentTimer(this.token).subscribe({
      next: (timerStatus) => {
        this.elapsedSeconds.set(timerStatus.active_elapsed_seconds);
        this.timerPaused.set(false);
        this.startLocalTimer();
        this.timerUpdating.set(false);
      },
      error: () => {
        this.error.set('The timer could not be resumed.');
        this.timerUpdating.set(false);
      },
    });
  }

  private resumeSession(session: StudentSession): void {
    if (session.status === 'completed' || session.answered_questions >= session.questions.length) {
      this.loadResults();
      return;
    }
    this.index.set(Math.max(0, session.answered_questions));
    this.feedback.set(null);
    this.answer = '';
    this.clearAllScratchWork();
  }

  private loadResults(): void {
    this.stopLocalTimer();
    this.submitting.set(true);
    this.api.studentResults(this.token).subscribe({
      next: (results) => {
        this.results.set(results);
        this.complete.set(true);
        this.submitting.set(false);
      },
      error: () => {
        this.error.set('Your results could not be loaded.');
        this.submitting.set(false);
      },
    });
  }

  private formatSeconds(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  private shouldRunLocalTimer(session: StudentSession): boolean {
    return (
      session.show_timer &&
      session.status !== 'completed' &&
      session.answered_questions < session.questions.length &&
      session.timer_status === 'running'
    );
  }

  private startLocalTimer(): void {
    this.stopLocalTimer();
    this.timer = setInterval(
      () => this.elapsedSeconds.update((seconds) => seconds + 1),
      1000,
    );
  }

  private stopLocalTimer(): void {
    if (this.timer) {
      clearInterval(this.timer);
      this.timer = undefined;
    }
  }

  private loadSpeechVoices(): void {
    if (window.speechSynthesis === undefined) {
      return;
    }
    const updateVoices = () => {
      const voices = window.speechSynthesis
        .getVoices()
        .filter((voice) => voice.lang.toLowerCase().startsWith('fr'))
        .sort((first, second) => this.voiceScore(second) - this.voiceScore(first));
      this.speechVoices.set([
        { id: 'auto', label: 'Best available French voice', voice: null },
        ...voices.map((voice) => ({
          id: `${voice.name}|${voice.lang}`,
          label: `${voice.name} (${voice.lang})`,
          voice,
        })),
      ]);
      this.speechVoicesLoaded = voices.length > 0;
    };
    updateVoices();
    if (!this.speechVoicesLoaded) {
      window.speechSynthesis.onvoiceschanged = updateVoices;
    }
  }

  private selectedSpeechVoice(preferredLocale: string): SpeechSynthesisVoice | null {
    const choices = this.speechVoices();
    if (this.selectedSpeechVoiceId !== 'auto') {
      return choices.find((choice) => choice.id === this.selectedSpeechVoiceId)?.voice ?? null;
    }
    return choices
      .map((choice) => choice.voice)
      .filter((voice): voice is SpeechSynthesisVoice => voice !== null)
      .sort((first, second) => (
        this.voiceScore(second, preferredLocale) - this.voiceScore(first, preferredLocale)
      ))[0] ?? null;
  }

  private voiceScore(voice: SpeechSynthesisVoice, preferredLocale = 'fr-CA'): number {
    const name = voice.name.toLowerCase();
    const lang = voice.lang.toLowerCase();
    const preferred = preferredLocale.toLowerCase();
    let score = 0;
    if (lang === preferred) {
      score += 80;
    }
    if (lang === 'fr-ca') {
      score += 35;
    }
    if (lang === 'fr-fr') {
      score += 30;
    }
    if (lang.startsWith('fr')) {
      score += 20;
    }
    if (voice.localService) {
      score += 12;
    }
    if (/(google|microsoft|natural|neural|amelie|amélie|denise|thomas|audrey|sylvie)/i.test(name)) {
      score += 18;
    }
    if (/(compact|eloquence|novelty)/i.test(name)) {
      score -= 30;
    }
    return score;
  }

  private clearAllScratchWork(): void {
    this.scratchPad.set('');
    this.drawStrokes.set([]);
    this.activeStroke = null;
    this.redrawScratchCanvas();
  }

  private canvasPoint(event: PointerEvent, canvas: HTMLCanvasElement): DrawPoint {
    const rect = canvas.getBoundingClientRect();
    return {
      x: ((event.clientX - rect.left) / rect.width) * canvas.width,
      y: ((event.clientY - rect.top) / rect.height) * canvas.height,
    };
  }

  private redrawScratchCanvas(): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    const context = canvas.getContext('2d');
    if (!context) {
      return;
    }
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = 5;
    context.strokeStyle = '#1f3431';
    for (const stroke of this.drawStrokes()) {
      if (stroke.length === 0) {
        continue;
      }
      context.beginPath();
      context.moveTo(stroke[0].x, stroke[0].y);
      for (const point of stroke.slice(1)) {
        context.lineTo(point.x, point.y);
      }
      context.stroke();
    }
  }
}
