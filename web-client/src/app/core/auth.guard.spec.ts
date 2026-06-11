import { signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { CanActivateFn, GuardResult, Router, UrlTree, provideRouter } from '@angular/router';
import { firstValueFrom, isObservable, of, throwError } from 'rxjs';
import { vi } from 'vitest';
import { routes } from '../app.routes';
import { AuthService } from './auth.service';
import { parentAuthGuard } from './auth.guard';

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
  ): Promise<GuardResult> {
    const result = TestBed.runInInjectionContext(() =>
      guard({} as Parameters<CanActivateFn>[0], { url } as Parameters<CanActivateFn>[1]),
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

    const result = await resolveGuardResult(parentAuthGuard, '/manage/learners');

    expect(result).toBeInstanceOf(UrlTree);
    expect(router.serializeUrl(result as UrlTree)).toBe('/login?returnUrl=%2Fmanage%2Flearners');
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
});
