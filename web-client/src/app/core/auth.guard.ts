import { inject } from '@angular/core';
import { CanActivateFn, Router, UrlTree } from '@angular/router';
import { catchError, map, of } from 'rxjs';
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
