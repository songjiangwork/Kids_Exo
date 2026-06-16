import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { QuestionRendererHost } from './question-renderer-host';

describe('QuestionRendererHost', () => {
  async function createFixture(): Promise<ComponentFixture<QuestionRendererHost>> {
    await TestBed.configureTestingModule({
      imports: [QuestionRendererHost],
    }).compileComponents();
    return TestBed.createComponent(QuestionRendererHost);
  }

  it('renders numeric questions through the numeric answer renderer', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: '42 x 11 = __________',
      renderer_type: 'numeric_answer',
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('input')).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Check answer');
  });

  it('renders listening choice questions through the choice renderer', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: 'Which letter do you hear?',
      renderer_type: 'listening_choice',
      choices: ['A', 'B', 'C', 'D'],
    });
    fixture.detectChanges();

    const choices = fixture.nativeElement.querySelectorAll('.choice-button') as NodeListOf<HTMLButtonElement>;
    expect(choices.length).toBe(4);
    expect(fixture.nativeElement.textContent).not.toContain('Check answer');
  });

  it('falls back to legacy choices when renderer type is missing', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: 'Choose one',
      choices: ['One', 'Two'],
    });
    fixture.detectChanges();

    expect(fixture.debugElement.queryAll(By.css('.choice-button')).length).toBe(2);
  });

  it('renders structured word problems through the word problem renderer', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: 'There are chickens and rabbits.',
      renderer_type: 'word_problem_answer',
      public_payload: {
        answer_schema: {
          fields: [
            { key: 'chicken_count', label: 'Chickens', value_type: 'integer', unit: 'items', required: true },
            { key: 'rabbit_count', label: 'Rabbits', value_type: 'integer', unit: 'items', required: true },
          ],
        },
        work_area: { enabled: true, required: false, label: 'Show your work' },
      },
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Chickens');
    expect(fixture.nativeElement.textContent).toContain('Rabbits');
    expect(fixture.nativeElement.textContent).toContain('Show your work');
    expect(fixture.nativeElement.querySelector('app-word-problem-answer-renderer')).not.toBeNull();
  });

  it('shows an unsupported message for unknown renderer types', async () => {
    const fixture = await createFixture();
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: 'Draw the answer',
      renderer_type: 'drawing_answer',
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('This question type is not supported yet.');
  });
});
