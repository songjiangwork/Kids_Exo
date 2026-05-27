import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ParentStudio } from './parent-studio';

describe('ParentStudio', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [ParentStudio],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(ParentStudio);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
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
        {
          plugin: 'square_ending_in_5',
          title: 'Squares Ending in 5',
          description: 'Square numbers ending in 5.',
          subject: 'Math',
          category: 'Mental Multiplication',
          default_locale: 'en-CA',
          locale_coverage: [],
          settings: [
            {
              name: 'strategies',
              label: 'Question types',
              control: 'multiple_choice',
              default: ['ending_in_5_square'],
              options: [{ value: 'ending_in_5_square', label: 'Ending in 5 squares' }],
            },
          ],
        },
      ],
    });
    http.expectOne('/api/learners').flush([
      { id: 1, nickname: 'Alex', active: true },
    ]);
    http.expectOne('/api/learners/1/sessions').flush([]);
    fixture.detectChanges();
    return { fixture, http };
  }

  it('loads the online catalog and presents session controls', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Create a practice session');
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('Start practice');
    expect((fixture.componentInstance as any).catalog().question_counts).toEqual([
      10,
      20,
      30,
      40,
      50,
      100,
    ]);
  });

  it('shows recent sessions for the selected learner', async () => {
    const { fixture, http } = await createFixture();
    (fixture.componentInstance as any).loadHistory();
    http.expectOne('/api/learners/1/sessions').flush([
      {
        id: 8,
        student_token: 'student-token',
        plugin: 'multiply_by_11',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 9,
        elapsed_seconds: 82,
      },
    ]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Recent practice');
    expect(fixture.nativeElement.textContent).toContain('9 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Completed');
  });

  it('submits only settings exposed by a newly selected plugin', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;
    component.selectPlugin('square_ending_in_5');
    component.startPractice();

    const request = http.expectOne('/api/learners/1/sessions');
    expect(request.request.body.plugin).toBe('square_ending_in_5');
    expect(request.request.body.plugin_settings).toEqual({
      strategies: ['ending_in_5_square'],
    });
    expect(request.request.body.plugin_settings.multiplicand_digits).toBeUndefined();
  });
});
