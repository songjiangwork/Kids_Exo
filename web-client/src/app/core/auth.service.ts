import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';

export interface Account {
  id: number;
  email: string;
  display_name: string;
  active: boolean;
}

export interface AuthState {
  account: Account | null;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  readonly account = signal<Account | null>(null);
  readonly loaded = signal(false);

  constructor(private readonly http: HttpClient) {}

  me(): Observable<AuthState> {
    return this.http.get<AuthState>('/api/auth/me').pipe(
      tap((state) => {
        this.account.set(state.account);
        this.loaded.set(true);
      }),
    );
  }

  login(email: string, password: string): Observable<AuthState> {
    return this.http.post<AuthState>('/api/auth/login', { email, password }).pipe(
      tap((state) => {
        this.account.set(state.account);
        this.loaded.set(true);
      }),
    );
  }

  logout(): Observable<AuthState> {
    return this.http.post<AuthState>('/api/auth/logout', {}).pipe(
      tap(() => {
        this.account.set(null);
        this.loaded.set(true);
      }),
    );
  }
}
