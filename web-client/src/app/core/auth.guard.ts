import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { catchError, map, of } from 'rxjs';
import { PracticeApi } from './practice-api';
import { AuthService } from './auth.service';

export const parentAuthGuard: CanActivateFn = (_route, state) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const redirectToLogin = (): UrlTree => router.createUrlTree(['/login'], {
    queryParams: { returnUrl: state.url },
  });

  if (auth.account() !== null) {
    return true;
  }

  return auth.me().pipe(
    map((authState) => authState.account !== null ? true : redirectToLogin()),
    catchError(() => of(redirectToLogin())),
  );
};

export const parentUnlockGuard: CanActivateFn = (_route, state) => {
  const api = inject(PracticeApi);
  const router = inject(Router);
  return api.parentUnlockStatus().pipe(
    map((status) => status.unlocked ? true : router.createUrlTree(['/home'], {
      queryParams: { returnUrl: state.url },
    })),
    catchError(() => of(router.createUrlTree(['/home'], {
      queryParams: { returnUrl: state.url },
    }))),
  );
};

export const studentOrParentAccessGuard: CanActivateFn = (route, state) => {
  const api = inject(PracticeApi);
  const auth = inject(AuthService);
  const router = inject(Router);
  const studentId = Number(route.paramMap.get('id'));
  return api.learner(studentId).pipe(
    map(() => true),
    catchError(() => auth.me().pipe(
      map((authState) => authState.account !== null
        ? router.createUrlTree(['/home'], { queryParams: { returnUrl: state.url } })
        : router.createUrlTree(['/student-login'], { queryParams: { returnUrl: state.url } })),
      catchError(() => of(router.createUrlTree(['/student-login'], {
        queryParams: { returnUrl: state.url },
      }))),
    )),
  );
};
