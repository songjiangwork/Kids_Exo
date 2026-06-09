import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { PracticeHistoryTable } from './practice-history-table';

describe('PracticeHistoryTable', () => {
  let fixture: ComponentFixture<PracticeHistoryTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PracticeHistoryTable],
      providers: [provideRouter([])],
    }).compileComponents();

    fixture = TestBed.createComponent(PracticeHistoryTable);
    fixture.componentRef.setInput('sessions', [
      {
        id: 1,
        student_token: 's1-token',
        plugin: 'multiply_by_11',
        subject: 'Math',
        category: 'Mental Multiplication',
        skill: 'Multiply by 11',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 8,
        elapsed_seconds: 90,
        created_at: '2026-05-29T17:00:00Z',
        completed_at: '2026-05-29T17:10:00Z',
      },
      {
        id: 2,
        student_token: 's2-token',
        plugin: 'french_alphabet_sounds',
        subject: 'French',
        category: 'Pronunciation',
        skill: 'French Alphabet Sounds',
        status: 'created',
        total_questions: 10,
        answered_questions: 0,
        correct_answers: 0,
        elapsed_seconds: null,
        created_at: '2026-05-30T17:00:00Z',
      },
    ]);
    fixture.detectChanges();
  });

  it('renders rows, actions, and paginator', () => {
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('French Alphabet Sounds');
    expect(fixture.nativeElement.textContent).toContain('Review results');
    expect(fixture.nativeElement.textContent).toContain('Open practice');
    expect(fixture.nativeElement.querySelector('mat-paginator')).not.toBeNull();
  });

  it('filters by status and emits completed review action', () => {
    const component = fixture.componentInstance as unknown as {
      setStatus(value: string): void;
    };
    component.setStatus('completed');
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).not.toContain('French Alphabet Sounds');

    const emitted: number[] = [];
    fixture.componentInstance.reviewResults.subscribe((session) => emitted.push(session.id));
    const button = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (entry) => entry.textContent?.includes('Review results'),
    ) as HTMLButtonElement;
    button.click();

    expect(emitted).toEqual([1]);
  });
});
