import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { StudentPractice } from './student-practice';

describe('StudentPractice', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 'student-token' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/student-token').flush({
      plugin: 'multiply_by_11',
      status: 'created',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      timer_status: 'paused',
      answered_questions: 0,
      correct_answers: 0,
      active_elapsed_seconds: 0,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 10, prompt: '42 x 11 = __________' },
      ],
    });
    fixture.detectChanges();
    return { fixture, http };
  }

  it('shows one focused question loaded from a session token', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Question 1 of 10');
    expect(fixture.nativeElement.textContent).toContain('42 x 11');
    expect(fixture.nativeElement.textContent).toContain('Check answer');
  });

  it('supports the short /s/:token route token shape', async () => {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 's12-k7m4p9qx' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/s12-k7m4p9qx').flush({
      plugin: 'multiply_by_11',
      status: 'created',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      timer_status: 'paused',
      answered_questions: 0,
      correct_answers: 0,
      active_elapsed_seconds: 0,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 10, prompt: '42 x 11 = __________' },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('42 x 11');
  });

  it('submits a value entered through the numeric answer input', async () => {
    const { fixture, http } = await createFixture();
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '462';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement;
    button.click();

    const submission = http.expectOne(
      '/api/student/sessions/student-token/questions/question-1/attempts',
    );
    expect(submission.request.body).toEqual({ answer: '462' });
    submission.flush({ normalized_answer: 462, is_correct: true });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Nice work. That is correct.');
  });

  it('offers a local scratch pad that can be cleared', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Scratch pad');
    const scratchPad = fixture.nativeElement.querySelector('.scratch-pad textarea') as HTMLTextAreaElement;
    scratchPad.value = '42 x 11: 4 + 2 = 6';
    scratchPad.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    expect((fixture.componentInstance as any).scratchPad()).toBe('42 x 11: 4 + 2 = 6');
    const clearButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Clear'),
    ) as HTMLButtonElement;
    clearButton.click();
    fixture.detectChanges();

    expect((fixture.componentInstance as any).scratchPad()).toBe('');
  });

  it('switches between typed notes and drawing mode without losing typed notes', async () => {
    const { fixture } = await createFixture();
    const component = fixture.componentInstance as any;
    const scratchPad = fixture.nativeElement.querySelector('.scratch-pad textarea') as HTMLTextAreaElement;
    scratchPad.value = '42 x 11: 4 + 2 = 6';
    scratchPad.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    component.setScratchMode('draw');
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('.scratch-pad textarea')).toBeNull();
    expect(fixture.nativeElement.querySelector('.scratch-pad canvas')).not.toBeNull();

    component.setScratchMode('type');
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect(component.scratchPad()).toBe('42 x 11: 4 + 2 = 6');
    expect((fixture.nativeElement.querySelector('.scratch-pad textarea') as HTMLTextAreaElement).value).toBe(
      '42 x 11: 4 + 2 = 6',
    );
  });

  it('records and clears draw-mode scratch strokes', async () => {
    const { fixture } = await createFixture();
    const component = fixture.componentInstance as any;
    component.setScratchMode('draw');
    fixture.detectChanges();

    const canvas = fixture.nativeElement.querySelector('.scratch-pad canvas') as HTMLCanvasElement;
    canvas.getBoundingClientRect = () => ({
      x: 0,
      y: 0,
      top: 0,
      left: 0,
      right: 300,
      bottom: 120,
      width: 300,
      height: 120,
      toJSON: () => ({}),
    });
    canvas.setPointerCapture = () => undefined;
    canvas.releasePointerCapture = () => undefined;
    canvas.hasPointerCapture = () => true;

    canvas.dispatchEvent(new PointerEvent('pointerdown', { clientX: 10, clientY: 10, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent('pointermove', { clientX: 50, clientY: 60, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent('pointerup', { clientX: 50, clientY: 60, pointerId: 1 }));
    fixture.detectChanges();

    expect(component.drawStrokes().length).toBe(1);
    expect(component.drawStrokes()[0].length).toBe(2);

    component.clearScratchPad();
    fixture.detectChanges();

    expect(component.drawStrokes().length).toBe(0);
  });

  it('loads server results after the last answered question', async () => {
    const { fixture, http } = await createFixture();
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '0';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement).click();
    http.expectOne('/api/student/sessions/student-token/questions/question-1/attempts').flush({
      normalized_answer: 0,
      is_correct: false,
    });
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.next-button') as HTMLButtonElement).click();
    http.expectOne('/api/student/sessions/student-token/results').flush({
      status: 'completed',
      total_questions: 1,
      answered_questions: 1,
      correct_answers: 0,
      elapsed_seconds: 12,
      incorrect_questions: [
        { prompt: '42 x 11 = __________', submitted_answer: 0, expected_answer: 462 },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('0 / 1 correct');
    expect(fixture.nativeElement.textContent).toContain('42 x 11');
    expect(fixture.nativeElement.textContent).toContain('Your answer: 0');
    expect(fixture.nativeElement.textContent).toContain('Answer: 462');
  });

  it('clears scratch notes when moving to the next question', async () => {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 'student-token' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/student-token').flush({
      plugin: 'multiply_by_11',
      status: 'created',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      timer_status: 'paused',
      answered_questions: 0,
      correct_answers: 0,
      active_elapsed_seconds: 0,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 2, prompt: '42 x 11 = __________' },
        { identifier: 'question-2', position: 2, total_questions: 2, prompt: '53 x 11 = __________' },
      ],
    });
    fixture.detectChanges();

    (fixture.componentInstance as any).scratchPad.set('carry the 1');
    (fixture.componentInstance as any).drawStrokes.set([[{ x: 1, y: 1 }]]);
    (fixture.componentInstance as any).feedback.set('correct');
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.next-button') as HTMLButtonElement).click();
    fixture.detectChanges();

    expect((fixture.componentInstance as any).scratchPad()).toBe('');
    expect((fixture.componentInstance as any).drawStrokes()).toEqual([]);
    expect(fixture.nativeElement.textContent).toContain('Question 2 of 2');
  });

  it('resumes an in-progress session at the next unanswered question', async () => {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 'student-token' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/student-token').flush({
      plugin: 'same_prefix_three_digit',
      status: 'in_progress',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      timer_status: 'paused',
      answered_questions: 3,
      correct_answers: 3,
      active_elapsed_seconds: 0,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 30, prompt: '123 x 127 = __________' },
        { identifier: 'question-2', position: 2, total_questions: 30, prompt: '234 x 236 = __________' },
        { identifier: 'question-3', position: 3, total_questions: 30, prompt: '345 x 345 = __________' },
        { identifier: 'question-4', position: 4, total_questions: 30, prompt: '456 x 454 = __________' },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Question 4 of 30');
    expect(fixture.nativeElement.textContent).toContain('456 x 454');

    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '207024';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    (fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement).click();

    http.expectOne('/api/student/sessions/student-token/questions/question-4/attempts').flush({
      normalized_answer: 207024,
      is_correct: true,
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Nice work. That is correct.');
  });

  it('pauses and resumes a visible timer before accepting answers', async () => {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 'student-token' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/student-token').flush({
      plugin: 'multiply_by_11',
      status: 'in_progress',
      timer_status: 'running',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: true,
      answered_questions: 0,
      correct_answers: 0,
      active_elapsed_seconds: 12,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 10, prompt: '42 x 11 = __________' },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('0:12');
    const pauseButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Pause'),
    ) as HTMLButtonElement;
    pauseButton.click();
    http.expectOne('/api/student/sessions/student-token/timer/pause').flush({
      timer_status: 'paused',
      active_elapsed_seconds: 17,
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('0:17');
    expect(fixture.nativeElement.textContent).toContain('Timer paused.');
    expect((fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement).disabled).toBe(true);

    const resumeButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Resume'),
    ) as HTMLButtonElement;
    resumeButton.click();
    http.expectOne('/api/student/sessions/student-token/timer/resume').flush({
      timer_status: 'running',
      active_elapsed_seconds: 17,
    });
    fixture.detectChanges();

    expect((fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement).disabled).toBe(false);
  });
});
