import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LearnerDetail } from './learner-detail';

describe('LearnerDetail', () => {
  it('shows learner summary and practice history', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerDetail],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerDetail);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners/0').flush({ id: 0, nickname: 'Alex', active: true });
    http.expectOne('/api/learners/0/sessions').flush([
      {
        id: 8,
        student_token: 'token',
        plugin: 'multiply_by_11',
        status: 'completed',
        total_questions: 10,
        answered_questions: 10,
        correct_answers: 8,
        elapsed_seconds: 90,
      },
    ]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Alex');
    expect(fixture.nativeElement.textContent).toContain('8 / 10 correct');
    expect(fixture.nativeElement.textContent).toContain('Mistake notebook');
  });
});
