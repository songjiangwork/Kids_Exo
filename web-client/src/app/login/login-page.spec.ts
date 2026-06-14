import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter, Router } from '@angular/router';
import { vi } from 'vitest';
import { LoginPage } from './login-page';

describe('LoginPage', () => {
  async function createFixture() {
    await TestBed.configureTestingModule({
      imports: [LoginPage],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LoginPage);
    fixture.detectChanges();
    return {
      fixture,
      http: TestBed.inject(HttpTestingController),
      router: TestBed.inject(Router),
    };
  }

  it('validates required login fields', async () => {
    const { fixture } = await createFixture();

    (fixture.componentInstance as any).login();
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Enter your email and password.');
  });

  it('logs in and navigates to household home by default', async () => {
    const { fixture, http, router } = await createFixture();
    const navigateByUrl = vi.spyOn(router, 'navigateByUrl').mockResolvedValue(true);

    (fixture.componentInstance as any).email = 'parent@example.com';
    (fixture.componentInstance as any).password = 'secret password';
    (fixture.componentInstance as any).login();

    const request = http.expectOne('/api/auth/login');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({
      email: 'parent@example.com',
      password: 'secret password',
    });
    request.flush({
      account: {
        id: 1,
        email: 'parent@example.com',
        display_name: 'Parent',
        active: true,
      },
    });

    expect(navigateByUrl).toHaveBeenCalledWith('/home');
  });

  it('shows a friendly error for failed login', async () => {
    const { fixture, http } = await createFixture();

    (fixture.componentInstance as any).email = 'parent@example.com';
    (fixture.componentInstance as any).password = 'wrong password';
    (fixture.componentInstance as any).login();
    http.expectOne('/api/auth/login').flush(
      { detail: 'Invalid email or password' },
      { status: 401, statusText: 'Unauthorized' },
    );
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Email or password is incorrect.');
  });
});
