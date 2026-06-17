import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideRouter } from '@angular/router';
import { PracticeResultsCard } from './practice-results-card';

describe('PracticeResultsCard', () => {
  async function createFixture(): Promise<ComponentFixture<PracticeResultsCard>> {
    await TestBed.configureTestingModule({
      imports: [PracticeResultsCard],
      providers: [provideRouter([])],
    }).compileComponents();
    return TestBed.createComponent(PracticeResultsCard);
  }

  it('displays structured submitted answer, expected answer, and submitted work', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('results', {
      status: 'completed',
      total_questions: 1,
      answered_questions: 1,
      correct_answers: 0,
      elapsed_seconds: null,
      incorrect_questions: [
        {
          prompt: 'There are chickens and rabbits.',
          submitted_answer: { values: { chicken_count: 10, rabbit_count: 10 }, work: '20 x 2 = 40' },
          expected_answer: { values: { chicken_count: 12, rabbit_count: 8 } },
          submitted_display: 'Chickens: 10, Rabbits: 10',
          expected_display: 'Chickens: 12, Rabbits: 8',
          submitted_work: '20 x 2 = 40',
          answer_type: 'structured_word_problem',
        },
      ],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Your answer: Chickens: 10, Rabbits: 10');
    expect(fixture.nativeElement.textContent).toContain('Answer: Chickens: 12, Rabbits: 8');
    expect(fixture.nativeElement.textContent).toContain('Your work:');
    expect(fixture.nativeElement.textContent).toContain('20 x 2 = 40');
  });

  it('defaults the back button to home instead of parent studio', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('results', {
      status: 'completed',
      total_questions: 1,
      answered_questions: 1,
      correct_answers: 1,
      elapsed_seconds: null,
      incorrect_questions: [],
    });
    fixture.detectChanges();

    const link = fixture.debugElement.query(By.css('a')).nativeElement as HTMLAnchorElement;
    expect(fixture.nativeElement.textContent).toContain('Back to Home');
    expect(fixture.nativeElement.textContent).not.toContain('Back to Parent Studio');
    expect(link.getAttribute('href')).toBe('/home');
  });

  it('allows callers to configure the back button', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('backUrl', '/manage/students/3');
    fixture.componentRef.setInput('backLabel', 'Back to Student Dashboard');
    fixture.componentRef.setInput('results', {
      status: 'completed',
      total_questions: 1,
      answered_questions: 1,
      correct_answers: 1,
      elapsed_seconds: null,
      incorrect_questions: [],
    });
    fixture.detectChanges();

    const link = fixture.debugElement.query(By.css('a')).nativeElement as HTMLAnchorElement;
    expect(fixture.nativeElement.textContent).toContain('Back to Student Dashboard');
    expect(link.getAttribute('href')).toBe('/manage/students/3');
  });
});
