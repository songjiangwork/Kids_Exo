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
    http.expectOne('/api/learners/0/analytics').flush({
      total_sessions: 2,
      completed_sessions: 1,
      total_questions: 10,
      correct_answers: 8,
      accuracy: 0.8,
      average_elapsed_seconds: 90,
      last_completed_at: '2026-05-29T17:00:00Z',
      skill_breakdown: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          correct_answers: 8,
          total_questions: 10,
          accuracy: 0.8,
        },
      ],
      mistake_notebook: [
        {
          plugin: 'multiply_by_11',
          title: 'Multiply by 11',
          prompt: '34 x 11 = ____',
          expected_answer: 374,
          last_submitted_answer: 344,
          times_missed: 2,
          last_seen_at: '2026-05-29T17:00:00Z',
        },
      ],
    });
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
    expect(fixture.nativeElement.textContent).toContain('Average time');
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('34 x 11 = ____');
    expect(fixture.nativeElement.textContent).toContain('Missed 2 times');
  });
});
