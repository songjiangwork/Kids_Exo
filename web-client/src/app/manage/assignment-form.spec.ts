import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AssignmentForm } from './assignment-form';
import { OnlineCatalog } from '../core/practice-api';

const catalog: OnlineCatalog = {
  default_locale: 'en-CA',
  question_counts: [10, 20, 30],
  feedback_modes: ['immediate', 'deferred'],
  show_timer_configurable: true,
  plugins: [
    {
      plugin: 'multiply_by_11',
      title: 'Multiply by 11',
      description: 'Practice multiplying by 11.',
      subject: 'Math',
      category: 'Mental Multiplication',
      default_locale: 'en-CA',
      settings: [
        {
          name: 'multiplicand_digits',
          label: 'Number size',
          control: 'single_choice',
          default: [2],
          options: [{ value: 2, label: 'Two digits' }],
        },
      ],
      supported_delivery_modes: ['web_practice'],
    },
  ],
};

describe('AssignmentForm', () => {
  let fixture: ComponentFixture<AssignmentForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AssignmentForm],
    }).compileComponents();

    fixture = TestBed.createComponent(AssignmentForm);
    fixture.componentRef.setInput('catalog', catalog);
    fixture.componentRef.setInput('sourceType', 'learner_added');
    fixture.componentRef.setInput('createdByRole', 'learner');
    fixture.detectChanges();
  });

  it('renders shared description notes copy', () => {
    expect(fixture.nativeElement.textContent).toContain('Description / notes (optional)');
    expect(fixture.nativeElement.textContent).toContain('Due date (optional)');
  });

  it('validates title and emits homework request payload', () => {
    const emitted: unknown[] = [];
    fixture.componentInstance.createAssignment.subscribe((value) => emitted.push(value));

    (fixture.componentInstance as any).title = '';
    (fixture.componentInstance as any).submit();
    expect(emitted.length).toBe(0);

    (fixture.componentInstance as any).title = 'New homework';
    (fixture.componentInstance as any).description = 'Practice before dinner.';
    (fixture.componentInstance as any).submit();

    expect(emitted.length).toBe(1);
    expect(emitted[0]).toEqual({
      title: 'New homework',
      description: 'Practice before dinner.',
      source_type: 'learner_added',
      due_at: null,
      created_by_role: 'learner',
      items: [
        {
          item_type: 'practice_plugin',
          plugin: 'multiply_by_11',
          plugin_settings: { multiplicand_digits: [2] },
          question_count: 10,
          feedback_mode: 'immediate',
          show_timer: true,
          required: true,
        },
      ],
    });
  });

  it('emits an optional due date when selected', () => {
    const emitted: unknown[] = [];
    fixture.componentInstance.createAssignment.subscribe((value) => emitted.push(value));

    (fixture.componentInstance as any).title = 'Due homework';
    (fixture.componentInstance as any).dueDate = new Date(2026, 5, 15);
    (fixture.componentInstance as any).submit();

    expect(emitted.length).toBe(1);
    expect((emitted[0] as any).due_at).toBe(new Date(2026, 5, 15, 12, 0, 0, 0).toISOString());
  });
});
