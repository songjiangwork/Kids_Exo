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
    {
      plugin: 'signed_integer',
      title: 'Signed Integer Addition and Subtraction',
      description: 'Practice signed integers.',
      subject: 'Math',
      category: 'Integer Arithmetic',
      default_locale: 'en-CA',
      settings: [],
      supported_delivery_modes: ['web_practice'],
    },
    {
      plugin: 'french_alphabet_sounds',
      title: 'French Alphabet Sounds',
      description: 'Listen to French letter sounds.',
      subject: 'French',
      category: 'Listening',
      default_locale: 'en-CA',
      settings: [],
      supported_delivery_modes: ['web_practice'],
    },
    {
      plugin: 'print_only',
      title: 'Print Only Practice',
      description: 'Only available as a printable worksheet.',
      subject: 'Math',
      category: 'Worksheets',
      default_locale: 'en-CA',
      settings: [],
      supported_delivery_modes: ['pdf_printable'],
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
    expect(fixture.nativeElement.textContent).toContain('Homework title');
  });

  it('labels the plugin picker as practice type and groups web practice plugins', () => {
    expect(fixture.nativeElement.textContent).toContain('Practice type');
    expect(fixture.nativeElement.textContent).not.toContain('Skill');

    const groups = (fixture.componentInstance as any).practiceTypeGroups;
    expect(groups.map((group: any) => group.label)).toEqual([
      'French / Listening',
      'Math / Integer Arithmetic',
      'Math / Mental Multiplication',
    ]);
    expect(groups.find((group: any) => group.label === 'French / Listening').plugins[0].plugin)
      .toBe('french_alphabet_sounds');
    expect(groups.flatMap((group: any) => group.plugins.map((plugin: any) => plugin.plugin)))
      .not.toContain('print_only');
  });

  it('defaults the title to the selected practice type name', () => {
    expect((fixture.componentInstance as any).title).toBe('Multiply by 11');

    (fixture.componentInstance as any).selectPlugin('signed_integer');

    expect((fixture.componentInstance as any).title).toBe('Signed Integer Addition and Subtraction');
  });

  it('keeps a manually edited title when switching practice types', () => {
    (fixture.componentInstance as any).updateTitle('Monday fluency sprint');
    (fixture.componentInstance as any).selectPlugin('signed_integer');

    expect((fixture.componentInstance as any).title).toBe('Monday fluency sprint');
  });

  it('keeps selected value as the internal plugin id and updates plugin settings', () => {
    (fixture.componentInstance as any).selectPlugin('signed_integer');

    expect((fixture.componentInstance as any).selectedPluginId).toBe('signed_integer');
    expect((fixture.componentInstance as any).selectedPlugin?.plugin).toBe('signed_integer');
    expect((fixture.componentInstance as any).pluginSettings).toEqual({});

    (fixture.componentInstance as any).selectPlugin('multiply_by_11');

    expect((fixture.componentInstance as any).selectedPluginId).toBe('multiply_by_11');
    expect((fixture.componentInstance as any).pluginSettings).toEqual({ multiplicand_digits: [2] });
  });

  it('validates title and emits homework request payload', () => {
    const emitted: unknown[] = [];
    fixture.componentInstance.createAssignment.subscribe((value) => emitted.push(value));

    (fixture.componentInstance as any).updateTitle('');
    (fixture.componentInstance as any).submit();
    expect(emitted.length).toBe(0);

    (fixture.componentInstance as any).updateTitle('New homework');
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
