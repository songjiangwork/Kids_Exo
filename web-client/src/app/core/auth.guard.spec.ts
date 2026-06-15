import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { CanActivateFn, GuardResult, Router, UrlTree, convertToParamMap, provideRouter } from '@angular/router';
import { firstValueFrom, isObservable, of, throwError } from 'rxjs';
import { vi } from 'vitest';
import { routes } from '../app.routes';
import { AuthService } from './auth.service';
import { parentAuthGuard, parentUnlockGuard, studentOrParentAccessGuard } from './auth.guard';
import { PracticeApi } from './practice-api';

describe('parentAuthGuard', () => {
  function createAuthMock(account: ReturnType<typeof signal>, me = vi.fn()) {
    return {
      account,
      me,
    };
  }

  async function resolveGuardResult(
    guard: CanActivateFn,
    url = '/manage',
    route = {},
  ): Promise<GuardResult> {
    const result = TestBed.runInInjectionContext(() =>
      guard(route as Parameters<CanActivateFn>[0], { url } as Parameters<CanActivateFn>[1]),
    );
    return isObservable(result) ? firstValueFrom(result) : result;
  }

  beforeEach(() => {
    TestBed.resetTestingModule();
  });

  it('allows parent routes when an account is already loaded', async () => {
    const me = vi.fn();
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: createAuthMock(
            signal({
              id: 1,
              email: 'parent@example.com',
              display_name: 'Parent',
              active: true,
            }),
            me,
          ),
        },
      ],
    });

    await expect(resolveGuardResult(parentAuthGuard)).resolves.toBe(true);
    expect(me).not.toHaveBeenCalled();
  });

  it('redirects anonymous parents to login with a return URL', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: createAuthMock(signal(null), vi.fn(() => of({ account: null }))),
        },
      ],
    });
    const router = TestBed.inject(Router);

    const result = await resolveGuardResult(parentAuthGuard, '/manage/students');

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/login?returnUrl=%2Fmanage%2Fstudents');
  });

  it('requires parent unlock for parent management routes', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: PracticeApi,
          useValue: { parentUnlockStatus: vi.fn(() => of({ unlocked: false })) },
        },
      ],
    });
    const router = TestBed.inject(Router);

    const result = await resolveGuardResult(parentUnlockGuard, '/manage/students');

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/home?returnUrl=%2Fmanage%2Fstudents');
  });

  it('allows parent management routes when parent unlock is active', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: PracticeApi,
          useValue: { parentUnlockStatus: vi.fn(() => of({ unlocked: true })) },
        },
      ],
    });

    await expect(resolveGuardResult(parentUnlockGuard, '/manage/students')).resolves.toBe(true);
  });

  it('redirects old learner management routes to student routes', () => {
    const learnerRedirect = routes.find((route) => route.path === 'manage/learners');
    const learnerDetailRedirect = routes.find((route) => route.path === 'manage/learners/:id');

    expect(learnerRedirect?.redirectTo).toBe('manage/students');
    expect(learnerDetailRedirect?.redirectTo).toBe('manage/students/:id');
  });

  it('redirects to login when the session check fails', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: AuthService,
          useValue: createAuthMock(signal(null), vi.fn(() => throwError(() => new Error('401')))),
        },
      ],
    });
    const router = TestBed.inject(Router);

    const result = await resolveGuardResult(parentAuthGuard, '/manage');

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/login?returnUrl=%2Fmanage');
  });

  it('keeps student token routes public', () => {
    const studentRoutes = routes.filter((route) => route.path?.startsWith('s/') || route.path?.startsWith('learn/session/'));

    expect(studentRoutes).toHaveLength(2);
    expect(studentRoutes.every((route) => route.canActivate === undefined)).toBe(true);
  });

  it('keeps student dashboard route available to direct student sessions', () => {
    const studentDetail = routes.find((route) => route.path === 'manage/students/:id');

    expect(studentDetail?.canActivate).toEqual([studentOrParentAccessGuard]);
  });

  it('redirects anonymous student dashboard failures to direct student login', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: PracticeApi,
          useValue: { learner: vi.fn(() => throwError(() => new Error('403'))) },
        },
        {
          provide: AuthService,
          useValue: createAuthMock(signal(null), vi.fn(() => of({ account: null }))),
        },
      ],
    });
    const router = TestBed.inject(Router);

    const result = await resolveGuardResult(
      studentOrParentAccessGuard,
      '/manage/students/3',
      { paramMap: convertToParamMap({ id: '3' }) },
    );

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/student-login?returnUrl=%2Fmanage%2Fstudents%2F3');
  });

  it('redirects parent household student access failures to home', async () => {
    TestBed.configureTestingModule({
      providers: [
        provideRouter([]),
        {
          provide: PracticeApi,
          useValue: { learner: vi.fn(() => throwError(() => new Error('403'))) },
        },
        {
          provide: AuthService,
          useValue: createAuthMock(
            signal(null),
            vi.fn(() => of({
              account: {
                id: 1,
                email: 'parent@example.com',
                display_name: 'Parent',
                active: true,
              },
            })),
          ),
        },
      ],
    });
    const router = TestBed.inject(Router);

    const result = await resolveGuardResult(
      studentOrParentAccessGuard,
      '/manage/students/3',
      { paramMap: convertToParamMap({ id: '3' }) },
    );

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/home?returnUrl=%2Fmanage%2Fstudents%2F3');
  });
});
