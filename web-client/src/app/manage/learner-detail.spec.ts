import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LearnerDetail } from './learner-detail';

function flushAssignmentRequests(http: HttpTestingController, body: unknown[] = []): void {
  http.match("/api/learners/0/assignments?status=all").forEach((request) => request.flush(body));
}

describe('LearnerDetail', () => {
  it('shows learner dashboard tabs and overview summaries', async () => {
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
        {
          plugin: 'french_alphabet_sounds',
          title: 'French Alphabet Sounds',
          correct_answers: 6,
          total_questions: 10,
          accuracy: 0.6,
        },
        {
          plugin: 'same_tens_ones_sum_to_ten',
          title: 'Same Tens, Ones Sum to 10',
          correct_answers: 7,
          total_questions: 10,
          accuracy: 0.7,
        },
        {
          plugin: 'hidden_skill',
          title: 'Hidden Fourth Skill',
          correct_answers: 9,
          total_questions: 10,
          accuracy: 0.9,
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
        {
          plugin: 'french_alphabet_sounds',
          title: 'French Alphabet Sounds',
          prompt: 'Choose the letter B',
          expected_answer: 1,
          last_submitted_answer: 2,
          times_missed: 5,
          last_seen_at: '2026-05-30T17:00:00Z',
        },
        {
          plugin: 'same_tens_ones_sum_to_ten',
          title: 'Same Tens, Ones Sum to 10',
          prompt: '43 x 47 = ____',
          expected_answer: 2021,
          last_submitted_answer: 2011,
          times_missed: 3,
          last_seen_at: '2026-05-31T17:00:00Z',
        },
        {
          plugin: 'hidden_mistake',
          title: 'Hidden Mistake Skill',
          prompt: 'Hidden fourth mistake',
          expected_answer: 1,
          last_submitted_answer: 0,
          times_missed: 1,
          last_seen_at: '2026-06-01T17:00:00Z',
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
      {
        id: 10,
        student_token: 's10-abcd2345',
        plugin: 'french_alphabet_sounds',
        subject: 'French',
        category: 'Pronunciation',
        skill: 'French Alphabet Sounds',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 7,
        elapsed_seconds: 100,
      },
      {
        id: 11,
        student_token: 's11-abcd2345',
        plugin: 'hidden_session',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Hidden Fourth Session',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 10,
        elapsed_seconds: 120,
      },
    ]);
    flushAssignmentRequests(http);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Alex');
    expect(fixture.nativeElement.textContent).toContain('Overview');
    expect(fixture.nativeElement.textContent).toContain('Practice History');
    expect(fixture.nativeElement.textContent).toContain('Mistakes');
    expect(fixture.nativeElement.textContent).toContain('Skills');
    expect(fixture.nativeElement.textContent).toContain('Statistics');
    expect(fixture.nativeElement.textContent).toContain('Badges');
    expect(fixture.nativeElement.textContent).toContain('Badge board coming later');
    expect(fixture.nativeElement.textContent).toContain('Statistics coming later');
    expect(fixture.nativeElement.textContent).toContain('8 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Average time');
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('34 x 11 = ____');
    expect(fixture.nativeElement.textContent).toContain('missed 2 times');
    expect(fixture.nativeElement.textContent).toContain('Review');
    expect(fixture.nativeElement.textContent).toContain('Open');
    expect(fixture.nativeElement.textContent).toContain('French Alphabet Sounds');
    expect(fixture.nativeElement.textContent).toContain('Same Tens, Ones Sum to 10');
    expect(fixture.nativeElement.textContent).toContain('Choose the letter B');
    expect(fixture.nativeElement.textContent).toContain('43 x 47 = ____');
    expect(fixture.nativeElement.textContent).not.toContain('Hidden Fourth Session');
    expect(fixture.nativeElement.textContent).not.toContain('Hidden Fourth Skill');
    expect(fixture.nativeElement.textContent).not.toContain('Hidden fourth mistake');
    const practiceLink = Array.from(fixture.nativeElement.querySelectorAll('a') as NodeListOf<HTMLAnchorElement>).find(
      (link) => link.textContent?.includes('Open'),
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
    flushAssignmentRequests(http);
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
    flushAssignmentRequests(http);
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
    flushAssignmentRequests(http);
    fixture.detectChanges();

    const reviewButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Review'),
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
    flushAssignmentRequests(http);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Session review');
    expect(fixture.nativeElement.textContent).toContain('8 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Answered 344; correct answer 374');
  });
});
