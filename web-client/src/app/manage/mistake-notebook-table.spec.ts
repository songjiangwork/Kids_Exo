import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MistakeNotebookTable } from './mistake-notebook-table';

describe('MistakeNotebookTable', () => {
  let fixture: ComponentFixture<MistakeNotebookTable>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MistakeNotebookTable],
    }).compileComponents();

    fixture = TestBed.createComponent(MistakeNotebookTable);
    fixture.componentRef.setInput('mistakes', [
      {
        plugin: 'multiply_by_11',
        title: 'Multiply by 11',
        prompt: '34 x 11 = ____',
        expected_answer: 374,
        last_submitted_answer: 344,
        expected_display: '374',
        last_submitted_display: '344',
        times_missed: 2,
        last_seen_at: '2026-05-29T17:00:00Z',
      },
      {
        plugin: 'french_common_word_sounds',
        title: 'French Common Word Sounds',
        prompt: 'Listen and choose',
        expected_answer: 1,
        last_submitted_answer: 2,
        expected_display: 'maman',
        last_submitted_display: 'papa',
        times_missed: 1,
        last_seen_at: '2026-05-30T17:00:00Z',
      },
    ]);
    fixture.detectChanges();
  });

  it('renders rows with generic display answers and paginator', () => {
    expect(fixture.nativeElement.textContent).toContain('34 x 11 = ____');
    expect(fixture.nativeElement.textContent).toContain('maman');
    expect(fixture.nativeElement.textContent).toContain('papa');
    expect(fixture.nativeElement.querySelector('mat-paginator')).not.toBeNull();
  });

  it('filters by prompt and emits create practice action', () => {
    const component = fixture.componentInstance as unknown as {
      setSearch(value: string): void;
    };
    component.setSearch('34 x 11');
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).not.toContain('French Common Word Sounds');

    const emitted: string[] = [];
    fixture.componentInstance.createPracticeFromPlugin.subscribe((plugin) => emitted.push(plugin));
    const button = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (entry) => entry.textContent?.includes('Create practice from mistakes'),
    ) as HTMLButtonElement;
    button.click();

    expect(emitted).toEqual(['multiply_by_11']);
  });
});
