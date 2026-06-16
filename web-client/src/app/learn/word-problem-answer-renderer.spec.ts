import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { WordProblemAnswerRenderer } from './word-problem-answer-renderer';

describe('WordProblemAnswerRenderer', () => {
  async function createFixture(): Promise<ComponentFixture<WordProblemAnswerRenderer>> {
    await TestBed.configureTestingModule({
      imports: [WordProblemAnswerRenderer],
    }).compileComponents();
    const fixture = TestBed.createComponent(WordProblemAnswerRenderer);
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
    return fixture;
  }

  it('renders fields from answer_schema and optional work area', async () => {
    const fixture = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Chickens');
    expect(fixture.nativeElement.textContent).toContain('Rabbits');
    expect(fixture.nativeElement.textContent).toContain('Show your work');
    expect(fixture.nativeElement.querySelectorAll('input').length).toBe(2);
    expect(fixture.nativeElement.querySelector('textarea')).not.toBeNull();
  });

  it('validates required integer fields before submit', async () => {
    const fixture = await createFixture();
    const submitSpy = vi.spyOn(fixture.componentInstance.submitAnswer, 'emit');

    fixture.nativeElement.querySelector('button').click();
    fixture.detectChanges();

    expect(submitSpy).not.toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Chickens is required.');
  });

  it('emits structured values and optional work', async () => {
    const fixture = await createFixture();
    const submitSpy = vi.spyOn(fixture.componentInstance.submitAnswer, 'emit');
    const answerSpy = vi.spyOn(fixture.componentInstance.answerChange, 'emit');
    const inputs = fixture.nativeElement.querySelectorAll('input') as NodeListOf<HTMLInputElement>;
    const textarea = fixture.nativeElement.querySelector('textarea') as HTMLTextAreaElement;

    inputs[0].value = '12';
    inputs[0].dispatchEvent(new Event('input'));
    inputs[1].value = '8';
    inputs[1].dispatchEvent(new Event('input'));
    textarea.value = 'Assume all are chickens.';
    textarea.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    fixture.debugElement.query(By.css('button')).nativeElement.click();

    expect(submitSpy).toHaveBeenCalled();
    expect(answerSpy).toHaveBeenLastCalledWith({
      values: { chicken_count: 12, rabbit_count: 8 },
      work: 'Assume all are chickens.',
    });
  });

  it('allows empty work when work area is optional', async () => {
    const fixture = await createFixture();
    const submitSpy = vi.spyOn(fixture.componentInstance.submitAnswer, 'emit');
    const inputs = fixture.nativeElement.querySelectorAll('input') as NodeListOf<HTMLInputElement>;

    inputs[0].value = '12';
    inputs[0].dispatchEvent(new Event('input'));
    inputs[1].value = '8';
    inputs[1].dispatchEvent(new Event('input'));
    fixture.detectChanges();
    fixture.nativeElement.querySelector('button').click();

    expect(submitSpy).toHaveBeenCalled();
  });

  it('clears previous values when the question changes', async () => {
    const fixture = await createFixture();
    const answerSpy = vi.spyOn(fixture.componentInstance.answerChange, 'emit');
    const inputs = fixture.nativeElement.querySelectorAll('input') as NodeListOf<HTMLInputElement>;

    inputs[0].value = '12';
    inputs[0].dispatchEvent(new Event('input'));
    fixture.componentRef.setInput('question', {
      identifier: 'question-2',
      position: 2,
      total_questions: 2,
      prompt: 'There are bicycles and cars.',
      renderer_type: 'word_problem_answer',
      public_payload: {
        answer_schema: {
          fields: [
            { key: 'bicycle_count', label: 'Bicycles', value_type: 'integer', unit: 'items', required: true },
            { key: 'car_count', label: 'Cars', value_type: 'integer', unit: 'items', required: true },
          ],
        },
        work_area: { enabled: true, required: false, label: 'Show your work' },
      },
    });
    fixture.detectChanges();

    const nextInputs = fixture.nativeElement.querySelectorAll('input') as NodeListOf<HTMLInputElement>;
    expect(nextInputs[0].value).toBe('');
    expect(fixture.nativeElement.textContent).toContain('Bicycles');
    expect(answerSpy).toHaveBeenLastCalledWith(null);
  });
});
