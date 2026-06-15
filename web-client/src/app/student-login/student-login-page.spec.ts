import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { vi } from 'vitest';
import { StudentLoginPage } from './student-login-page';

describe('StudentLoginPage', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [StudentLoginPage],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(StudentLoginPage);
    fixture.detectChanges();
    return {
      fixture,
      http: TestBed.inject(HttpTestingController),
      router: TestBed.inject(Router),
    };
  }

  it('renders direct student login fields', async () => {
    const { fixture } = await createFixture();

    expect(fixture.nativeElement.textContent).toContain('Student Login');
    expect(fixture.nativeElement.textContent).toContain('Household Code');
    expect(fixture.nativeElement.textContent).toContain('Student Code');
    expect(fixture.nativeElement.textContent).toContain('PIN');
  });

  it('requires all fields before logging in', async () => {
    const { fixture, http } = await createFixture();

    (fixture.componentInstance as any).login();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Enter your household code, student code, and PIN.');
    http.expectNone('/api/student-direct-auth/login');
  });

  it('navigates to the student dashboard after successful login', async () => {
    const { fixture, http, router } = await createFixture();
    const navigateByUrl = vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);
    const component = fixture.componentInstance as any;
    component.householdCode = 'songhome';
    component.studentCode = 'h';
    component.pin = '1234';

    component.login();

    const request = http.expectOne('/api/student-direct-auth/login');
    expect(request.request.body).toEqual({
      household_code: 'songhome',
      student_code: 'h',
      pin: '1234',
    });
    request.flush({
      student: { id: 3, nickname: 'Herbert', avatar_key: 'fox', student_login_enabled: true, student_code: 'H' },
      redirect_to: '/manage/students/3',
    });

    expect(navigateByUrl).toHaveBeenCalledWith('/manage/students/3');
  });

  it('shows a generic error after failed login', async () => {
    const { fixture, http } = await createFixture();
    const component = fixture.componentInstance as any;
    component.householdCode = 'BAD';
    component.studentCode = 'H';
    component.pin = '0000';

    component.login();
    http.expectOne('/api/student-direct-auth/login').flush(
      { detail: 'Household code, student code, or PIN is incorrect.' },
      { status: 403, statusText: 'Forbidden' },
    );
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Household code, student code, or PIN is incorrect.');
  });
});
