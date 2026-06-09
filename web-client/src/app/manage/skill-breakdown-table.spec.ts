import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SkillBreakdownTable } from './skill-breakdown-table';

describe('SkillBreakdownTable', () => {
  let fixture: ComponentFixture<SkillBreakdownTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SkillBreakdownTable],
    }).compileComponents();

    fixture = TestBed.createComponent(SkillBreakdownTable);
    fixture.componentRef.setInput('skills', [
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
        correct_answers: 4,
        total_questions: 10,
        accuracy: 0.4,
      },
    ]);
    fixture.detectChanges();
  });

  it('renders ranked skill rows with accuracy and focus labels', () => {
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('80%');
    expect(fixture.nativeElement.textContent).toContain('Growing');
    expect(fixture.nativeElement.textContent).toContain('French Alphabet Sounds');
    expect(fixture.nativeElement.textContent).toContain('Focus');
  });

  it('filters by skill title', () => {
    const component = fixture.componentInstance as unknown as {
      setSearch(value: string): void;
    };
    component.setSearch('French');
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('French Alphabet Sounds');
    expect(fixture.nativeElement.textContent).not.toContain('Multiply by 11');
  });
});
