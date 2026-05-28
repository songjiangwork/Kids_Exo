import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LearnerManagement } from './learner-management';

describe('LearnerManagement', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [LearnerManagement],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerManagement);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners').flush([
      { id: 1, nickname: 'Alex', active: true },
      { id: 2, nickname: 'Herbert', active: false },
    ]);
    fixture.detectChanges();
    return { fixture, http };
  }

  it('renders learners in a table with action columns', async () => {
    const { fixture } = await createFixture();
    const text = fixture.nativeElement.textContent;
    const firstRowCells = Array.from(
      fixture.nativeElement.querySelectorAll('tbody tr:first-child td'),
    ).map((cell) => (cell as HTMLElement).textContent?.trim());

    expect(text).toContain('ID');
    expect(text).toContain('Nickname');
    expect(text).toContain('Status');
    expect(text).toContain('Detail');
    expect(text).toContain('Edit');
    expect(text).toContain('Delete');
    expect(text).toContain('Alex');
    expect(text).toContain('Inactive');
    expect(firstRowCells[0]).toBe('#1');
    expect(firstRowCells[1]).toBe('Alex');
  });

  it('deletes a learner after confirmation', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    component.deleteLearner({ id: 1, nickname: 'Alex', active: true });

    const request = http.expectOne('/api/learners/1');
    expect(request.request.method).toBe('DELETE');
    request.flush(null);
    expect(component.learners()).toEqual([
      { id: 2, nickname: 'Herbert', active: false },
    ]);
  });
});
