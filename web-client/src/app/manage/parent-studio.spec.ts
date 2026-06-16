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
          supported_delivery_modes: ['web_practice'],
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
          supported_delivery_modes: ['web_practice'],
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
        {
          plugin: 'difference_of_squares',
          title: 'Difference of Squares',
          description: 'Use symmetric factors around a round number.',
          subject: 'Math',
          category: 'Mental Multiplication',
          default_locale: 'en-CA',
          locale_coverage: [],
          supported_delivery_modes: ['web_practice'],
          settings: [
            {
              name: 'strategies',
              label: 'Question types',
              control: 'multiple_choice',
              default: ['symmetric_around_round'],
              options: [{ value: 'symmetric_around_round', label: 'Symmetric factors around a round number' }],
            },
          ],
        },
        {
          plugin: 'french_alphabet_sounds',
          title: 'French Alphabet Sounds',
          description: 'Listen and choose what you hear.',
          subject: 'French',
          category: 'Pronunciation',
          default_locale: 'en-CA',
          locale_coverage: [],
          supported_delivery_modes: ['web_practice'],
          settings: [
            {
              name: 'strategies',
              label: 'Question types',
              control: 'multiple_choice',
              default: ['letter_name_to_letter'],
              options: [{ value: 'letter_name_to_letter', label: 'French letter names' }],
            },
          ],
        },
      ],
    });
    http.expectOne('/api/learners').flush([
      { id: 1, nickname: 'Alex', active: true },
    ]);
    fixture.detectChanges();
    return { fixture, http };
  }

  it('loads the online catalog and presents homework controls', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Assign homework');
    expect(fixture.nativeElement.textContent).toContain('Who is this homework for?');
    expect(fixture.nativeElement.textContent).toContain('Practice type');
    expect(fixture.nativeElement.textContent).toContain('Description / notes (optional)');
    expect((fixture.componentInstance as any).catalog().plugins.map((plugin: any) => plugin.plugin)).toContain(
      'difference_of_squares',
    );
    expect((fixture.componentInstance as any).catalog().question_counts).toEqual([
      10,
      20,
      30,
      40,
      50,
      100,
    ]);
  });

  it('assigns homework to the selected learner', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;
    component.assignHomework({
      title: 'Multiply by 11 homework',
      description: 'Practice before dinner.',
      source_type: 'learner_added',
      due_at: null,
      created_by_role: 'learner',
      items: [
        {
          item_type: 'practice_plugin',
          plugin: 'multiply_by_11',
          plugin_settings: {
            multiplicand_digits: [2],
            strategies: ['no_carrying'],
          },
          question_count: 10,
          feedback_mode: 'immediate',
          show_timer: true,
          required: true,
        },
      ],
    });

    const request = http.expectOne('/api/learners/1/assignments');
    expect(request.request.method).toBe('POST');
    expect(request.request.body.source_type).toBe('parent_assigned');
    expect(request.request.body.created_by_role).toBe('parent');
    expect(request.request.body.description).toBe('Practice before dinner.');
    expect(request.request.body.items[0].plugin).toBe('multiply_by_11');
    request.flush({
      id: 12,
      learner_id: 1,
      title: 'Multiply by 11 homework',
      description: 'Practice before dinner.',
      status: 'assigned',
      source_type: 'parent_assigned',
      due_at: null,
      created_by_role: 'parent',
      created_at: '2026-06-09T10:00:00Z',
      updated_at: '2026-06-09T10:00:00Z',
      completed_at: null,
      items: [],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Homework assigned');
    expect(fixture.nativeElement.textContent).toContain('Open student dashboard');
  });

  it('keeps learner history on the learner detail page instead of the setup page', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).not.toContain('Recent practice');
    expect(fixture.nativeElement.textContent).not.toContain("Alex's sessions");
  });

  it('creates a learner before assigning homework to a new learner', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;
    component.selectLearner(null);
    component.nickname = 'Linsey';

    component.assignHomework({
      title: 'New learner homework',
      description: '',
      items: [
        {
          plugin: 'multiply_by_11',
          plugin_settings: { multiplicand_digits: [2] },
          question_count: 10,
          feedback_mode: 'immediate',
          show_timer: true,
        },
      ],
    });

    http.expectOne('/api/learners').flush({ id: 4, nickname: 'Linsey', active: true });
    const assignment = http.expectOne('/api/learners/4/assignments');
    expect(assignment.request.body.created_by_role).toBe('parent');
    assignment.flush({
      id: 18,
      learner_id: 4,
      title: 'New learner homework',
      description: '',
      status: 'assigned',
      source_type: 'parent_assigned',
      due_at: null,
      created_by_role: 'parent',
      created_at: '2026-06-09T10:00:00Z',
      updated_at: '2026-06-09T10:00:00Z',
      completed_at: null,
      items: [],
    });
    fixture.detectChanges();

    expect(component.learnerId).toBe(4);
    expect(fixture.nativeElement.textContent).toContain('Linsey');
  });
});
