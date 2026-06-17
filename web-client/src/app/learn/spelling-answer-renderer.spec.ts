import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SpellingAnswerRenderer } from './spelling-answer-renderer';

describe('SpellingAnswerRenderer', () => {
  async function createFixture(promptMode = 'combined'): Promise<ComponentFixture<SpellingAnswerRenderer>> {
    await TestBed.configureTestingModule({
      imports: [SpellingAnswerRenderer],
    }).compileComponents();
    const fixture = TestBed.createComponent(SpellingAnswerRenderer);
    fixture.componentRef.setInput('question', {
      identifier: 'question-1',
      position: 1,
      total_questions: 1,
      prompt: 'Spell the French word.',
      renderer_type: 'spelling_answer',
      public_payload: {
        prompt_mode: promptMode,
        input_label: 'French word',
        translation: promptMode === 'dictation' ? undefined : 'brother',
        audio_url: promptMode === 'translation' ? undefined : '/audio/frere.mp3',
        accent_keys: ['é', 'è', 'œ', '-'],
      },
    });
    fixture.detectChanges();
    return fixture;
  }

  it('renders a text input and accent buttons', async () => {
    const fixture = await createFixture();

    expect(fixture.nativeElement.querySelector('input')).not.toBeNull();
    expect(fixture.nativeElement.textContent).toContain('Special characters');
    expect(fixture.nativeElement.textContent).toContain('œ');
  });

  it('shows audio only for dictation mode', async () => {
    const fixture = await createFixture('dictation');

    expect(fixture.nativeElement.textContent).toContain('Replay audio');
    expect(fixture.nativeElement.textContent).not.toContain('Meaning:');
  });

  it('shows translation only for translation mode', async () => {
    const fixture = await createFixture('translation');

    expect(fixture.nativeElement.textContent).toContain('Meaning:');
    expect(fixture.nativeElement.textContent).toContain('brother');
    expect(fixture.nativeElement.textContent).not.toContain('Replay audio');
  });

  it('shows translation and audio for combined mode', async () => {
    const fixture = await createFixture('combined');

    expect(fixture.nativeElement.textContent).toContain('Meaning:');
    expect(fixture.nativeElement.textContent).toContain('Replay audio');
  });

  it('clicking an accent button inserts the character', async () => {
    const fixture = await createFixture();
    const answerSpy = vi.spyOn(fixture.componentInstance.answerChange, 'emit');
    const buttons = fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>;
    const button = Array.from(buttons)
      .find((item): item is HTMLButtonElement => item.textContent?.includes('é') ?? false);

    if (!button) {
      throw new Error('Expected accent button');
    }
    button.click();
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    expect(input.value).toBe('é');
    expect(answerSpy).toHaveBeenLastCalledWith({ text: 'é' });
  });

  it('submits structured spelling text', async () => {
    const fixture = await createFixture();
    const answerSpy = vi.spyOn(fixture.componentInstance.answerChange, 'emit');
    const submitSpy = vi.spyOn(fixture.componentInstance.submitAnswer, 'emit');
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;

    input.value = 'frère';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();
    fixture.nativeElement.querySelector('.check-button').click();

    expect(answerSpy).toHaveBeenLastCalledWith({ text: 'frère' });
    expect(submitSpy).toHaveBeenCalled();
  });

  it('validates required spelling input', async () => {
    const fixture = await createFixture();
    const submitSpy = vi.spyOn(fixture.componentInstance.submitAnswer, 'emit');

    fixture.nativeElement.querySelector('.check-button').click();
    fixture.detectChanges();

    expect(submitSpy).not.toHaveBeenCalled();
    expect(fixture.nativeElement.textContent).toContain('Please enter French word.');
  });

  it('clears the input when the question changes', async () => {
    const fixture = await createFixture();
    const answerSpy = vi.spyOn(fixture.componentInstance.answerChange, 'emit');
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;

    input.value = 'mari';
    input.dispatchEvent(new Event('input', { bubbles: true }));
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.componentRef.setInput('question', {
      identifier: 'question-2',
      position: 2,
      total_questions: 2,
      prompt: 'Spell the French word.',
      renderer_type: 'spelling_answer',
      public_payload: {
        prompt_mode: 'combined',
        input_label: 'French word',
        translation: 'female cousin',
        audio_url: '/audio/cousine.mp3',
        accent_keys: ['é', 'è', 'œ', '-'],
      },
    });
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    const nextInput = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    expect(nextInput.value).toBe('');
    expect(fixture.nativeElement.textContent).toContain('female cousin');
    expect(answerSpy).toHaveBeenLastCalledWith(null);
  });
});
