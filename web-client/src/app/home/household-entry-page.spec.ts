import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { vi } from 'vitest';
import { HouseholdEntryPage } from './household-entry-page';

describe('HouseholdEntryPage', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [HouseholdEntryPage],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(HouseholdEntryPage);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/household/students').flush({
      household: { id: 1, name: 'Song Family', household_code: 'SONGH2' },
      students: [
        { id: 3, nickname: 'Herbert', avatar_key: 'fox', student_login_enabled: true, student_code: 'H' },
        { id: 4, nickname: 'Linsey', avatar_key: 'panda', student_login_enabled: true, student_code: 'L' },
      ],
    });
    fixture.detectChanges();
    return {
      fixture,
      http,
      router: TestBed.inject(Router),
    };
  }

  it('renders Student Mode and Parent Management with student cards', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Student Mode');
    expect(fixture.nativeElement.textContent).toContain('Parent Management');
    expect(fixture.nativeElement.textContent).toContain('SONGH2');
    expect(fixture.nativeElement.textContent).toContain('Herbert');
    expect(fixture.nativeElement.textContent).toContain('Linsey');
  });

  it('opens a student PIN dialog and navigates to the student dashboard', async () => {
    const { fixture, http, router } = await createFixture();
    const navigate = vi.spyOn(router, 'navigate').mockResolvedValue(true);

    (fixture.componentInstance as any).selectStudent({ id: 3, nickname: 'Herbert', avatar_key: 'fox', student_login_enabled: true });
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain("Herbert's PIN");
    (fixture.componentInstance as any).studentPin = '1234';
    (fixture.componentInstance as any).loginStudent();
    http.expectOne('/api/household/students/3/login').flush({
      student: { id: 3, nickname: 'Herbert', avatar_key: 'fox', student_login_enabled: true },
    });

    expect(navigate).toHaveBeenCalledWith(['/manage/students', 3]);
  });

  it('shows an error for a wrong student PIN', async () => {
    const { fixture, http } = await createFixture();

    (fixture.componentInstance as any).selectStudent({ id: 3, nickname: 'Herbert', avatar_key: 'fox', student_login_enabled: true });
    (fixture.componentInstance as any).studentPin = '0000';
    (fixture.componentInstance as any).loginStudent();
    http.expectOne('/api/household/students/3/login').flush(
      { detail: 'Invalid student PIN' },
      { status: 403, statusText: 'Forbidden' },
    );
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('That student PIN did not work.');
  });

  it('unlocks parent management and navigates to manage', async () => {
    const { fixture, http, router } = await createFixture();
    const navigateByUrl = vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);

    (fixture.componentInstance as any).parentPin = '1234';
    (fixture.componentInstance as any).unlockParent();
    http.expectOne('/api/household/parent-unlock').flush({
      unlocked: true,
      expires_at: '2026-06-13T12:15:00Z',
    });

    expect(navigateByUrl).toHaveBeenCalledWith('/manage');
  });

  it('changes the parent PIN from the parent management card', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;

    component.toggleParentPinForm();
    component.currentParentPin = '1234';
    component.newParentPin = '5678';
    component.confirmParentPin = '5678';
    component.changeParentPin();

    const request = http.expectOne('/api/household/parent-pin');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ current_pin: '1234', new_pin: '5678' });
    request.flush({ unlocked: true, expires_at: '2026-06-13T12:15:00Z' });
    expect(component.parentPinMessage()).toBe('Parent PIN has been changed.');
  });
});
