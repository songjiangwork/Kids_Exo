import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LearnerDetail } from './learner-detail';

describe('LearnerDetail', () => {
  it('shows learner summary and practice history', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerDetail],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerDetail);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners/0').flush({ id: 0, nickname: 'Alex', active: true });
    http.expectOne('/api/practice-plugins').flush({
      default_locale: 'en-CA',
      question_counts: [10, 20, 30, 40, 50, 100],
      feedback_modes: ['immediate', 'deferred'],
      show_timer_configurable: true,
      plugins: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          description: 'Practise multiplying by 11.',
          subject: 'Math',
          category: 'Mental Multiplication',
          default_locale: 'en-CA',
          locale_coverage: [],
          settings: [
            {
              name: 'multiplicand_digits',
              label: 'Number of digits',
              control: 'single_choice',
              default: [2],
              options: [{ value: 2, label: 'Two digits' }],
            },
            {
              name: 'strategies',
              label: 'Question types',
              control: 'multiple_choice',
              default: ['no_carrying'],
              options: [{ value: 'no_carrying', label: 'Without carrying' }],
            },
          ],
        },
      ],
    });
    http.expectOne('/api/learners/0/analytics').flush({
      total_sessions: 2,
      completed_sessions: 1,
      total_questions: 10,
      correct_answers: 8,
      accuracy: 0.8,
      average_elapsed_seconds: 90,
      last_completed_at: '2026-05-29T17:00:00Z',
      skill_breakdown: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          correct_answers: 8,
          total_questions: 10,
          accuracy: 0.8,
        },
      ],
      mistake_notebook: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          prompt: '34 x 11 = ____',
          expected_answer: 374,
          last_submitted_answer: 344,
          times_missed: 2,
          last_seen_at: '2026-05-29T17:00:00Z',
        },
      ],
    });
    http.expectOne('/api/learners/0/sessions').flush([
      {
        id: 8,
        student_token: 'token',
        plugin: 'multiply_by_11',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Multiply by 11',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 8,
        elapsed_seconds: 90,
      },
      {
        id: 9,
        student_token: 's9-abcd2345',
        plugin: 'multiply_by_11',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Multiply by 11',
        status: 'created',
        total_questions: 10,
        answered_questions: 0,
        correct_answers: 0,
        elapsed_seconds: null,
      },
    ]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Alex');
    expect(fixture.nativeElement.textContent).toContain('8 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Average time');
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('34 x 11 = ____');
    expect(fixture.nativeElement.textContent).toContain('Missed 2 times');
    expect(fixture.nativeElement.textContent).toContain('Review results');
    expect(fixture.nativeElement.textContent).toContain('Open practice');
    const practiceLink = Array.from(fixture.nativeElement.querySelectorAll('a') as NodeListOf<HTMLAnchorElement>).find(
      (link) => link.textContent?.includes('Open practice'),
    ) as HTMLAnchorElement;
    expect(practiceLink.getAttribute('href')).toBe('/s/s9-abcd2345');
  });

  it('creates a focused practice session from a mistake row', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerDetail],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerDetail);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners/0').flush({ id: 0, nickname: 'Alex', active: true });
    http.expectOne('/api/practice-plugins').flush({
      default_locale: 'en-CA',
      question_counts: [10, 20, 30, 40, 50, 100],
      feedback_modes: ['immediate', 'deferred'],
      show_timer_configurable: true,
      plugins: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          description: 'Practise multiplying by 11.',
          subject: 'Math',
          category: 'Mental Multiplication',
          default_locale: 'en-CA',
          locale_coverage: [],
          settings: [
            {
              name: 'multiplicand_digits',
              label: 'Number of digits',
              control: 'single_choice',
              default: [2],
              options: [{ value: 2, label: 'Two digits' }],
            },
            {
              name: 'strategies',
              label: 'Question types',
              control: 'multiple_choice',
              default: ['no_carrying'],
              options: [{ value: 'no_carrying', label: 'Without carrying' }],
            },
          ],
        },
      ],
    });
    http.expectOne('/api/learners/0/analytics').flush({
      total_sessions: 2,
      completed_sessions: 1,
      total_questions: 10,
      correct_answers: 8,
      accuracy: 0.8,
      average_elapsed_seconds: 90,
      last_completed_at: '2026-05-29T17:00:00Z',
      skill_breakdown: [],
      mistake_notebook: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          prompt: '34 x 11 = ____',
          expected_answer: 374,
          last_submitted_answer: 344,
          times_missed: 2,
          last_seen_at: '2026-05-29T17:00:00Z',
        },
      ],
    });
    http.expectOne('/api/learners/0/sessions').flush([]);
    fixture.detectChanges();

    (fixture.componentInstance as any).createPracticeFromPlugin('multiply_by_11');

    const request = http.expectOne('/api/learners/0/sessions');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      plugin: 'multiply_by_11',
      plugin_settings: {
        multiplicand_digits: [2],
        strategies: ['no_carrying'],
      },
      question_count: 10,
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: true,
    });
    request.flush({
      id: 10,
      student_token: 'student-token',
      plugin: 'multiply_by_11',
      subject: 'Math',
      category: 'Mental Multiplication',
      skill: 'Multiply by 11',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      localization_fallback_keys: [],
      questions: [{ identifier: 'q1', position: 1, total_questions: 10, prompt: '34 x 11 = ____' }],
    });
    http.expectOne('/api/learners/0/analytics').flush({
      total_sessions: 3,
      completed_sessions: 1,
      total_questions: 10,
      correct_answers: 8,
      accuracy: 0.8,
      average_elapsed_seconds: 90,
      last_completed_at: '2026-05-29T17:00:00Z',
      skill_breakdown: [],
      mistake_notebook: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          prompt: '34 x 11 = ____',
          expected_answer: 374,
          last_submitted_answer: 344,
          times_missed: 2,
          last_seen_at: '2026-05-29T17:00:00Z',
        },
      ],
    });
    http.expectOne('/api/learners/0/sessions').flush([
      {
        id: 10,
        student_token: 'student-token',
        plugin: 'multiply_by_11',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Multiply by 11',
        status: 'created',
        total_questions: 10,
        answered_questions: 0,
        correct_answers: 0,
        elapsed_seconds: null,
      },
    ]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('New practice ready');
    expect(fixture.nativeElement.textContent).toContain('Open learner practice');
  });

  it('loads completed practice results from history', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerDetail],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerDetail);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners/0').flush({ id: 0, nickname: 'Alex', active: true });
    http.expectOne('/api/practice-plugins').flush({
      default_locale: 'en-CA',
      question_counts: [10, 20, 30, 40, 50, 100],
      feedback_modes: ['immediate', 'deferred'],
      show_timer_configurable: true,
      plugins: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          description: 'Practise multiplying by 11.',
          subject: 'Math',
          category: 'Mental Multiplication',
          default_locale: 'en-CA',
          locale_coverage: [],
          settings: [],
        },
      ],
    });
    http.expectOne('/api/learners/0/analytics').flush({
      total_sessions: 1,
      completed_sessions: 1,
      total_questions: 10,
      correct_answers: 8,
      accuracy: 0.8,
      average_elapsed_seconds: 90,
      last_completed_at: '2026-05-29T17:00:00Z',
      skill_breakdown: [],
      mistake_notebook: [],
    });
    http.expectOne('/api/learners/0/sessions').flush([
      {
        id: 8,
        student_token: 'token',
        plugin: 'multiply_by_11',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Multiply by 11',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 8,
        elapsed_seconds: 90,
      },
    ]);
    fixture.detectChanges();

    const reviewButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Review results'),
    ) as HTMLButtonElement;
    reviewButton.click();

    http.expectOne('/api/learners/0/sessions/8/results').flush({
      status: 'completed',
      total_questions: 10,
      answered_questions: 10,
      correct_answers: 8,
      elapsed_seconds: 90,
      incorrect_questions: [
        {
          prompt: '34 x 11 = ____',
          submitted_answer: 344,
          expected_answer: 374,
        },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Session review');
    expect(fixture.nativeElement.textContent).toContain('8 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Answered 344; correct answer 374');
  });
});
