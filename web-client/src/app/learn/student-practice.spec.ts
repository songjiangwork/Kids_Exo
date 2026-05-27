import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap } from '@angular/router';
import { of } from 'rxjs';
import { StudentPractice } from './student-practice';

describe('StudentPractice', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [StudentPractice],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        {
          provide: ActivatedRoute,
          useValue: { paramMap: of(convertToParamMap({ token: 'student-token' })) },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentPractice);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/student/sessions/student-token').flush({
      plugin: 'multiply_by_11',
      requested_locale: 'en-CA',
      feedback_mode: 'immediate',
      show_timer: false,
      questions: [
        { identifier: 'question-1', position: 1, total_questions: 10, prompt: '42 x 11 = __________' },
      ],
    });
    fixture.detectChanges();
    return { fixture, http };
  }

  it('shows one focused question loaded from a session token', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Question 1 of 10');
    expect(fixture.nativeElement.textContent).toContain('42 x 11');
    expect(fixture.nativeElement.textContent).toContain('Check answer');
  });

  it('submits a value entered through the numeric answer input', async () => {
    const { fixture, http } = await createFixture();
    const input = fixture.nativeElement.querySelector('input') as HTMLInputElement;
    input.value = '462';
    input.dispatchEvent(new Event('input'));
    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector('.check-button') as HTMLButtonElement;
    button.click();

    const submission = http.expectOne(
      '/api/student/sessions/student-token/questions/question-1/attempts',
    );
    expect(submission.request.body).toEqual({ answer: '462' });
    submission.flush({ normalized_answer: 462, is_correct: true });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Nice work. That is correct.');
  });
});
