import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { AuthService } from '../core/auth.service';

@Component({
  selector: 'app-login-page',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './login-page.html',
  styleUrl: './login-page.scss',
})
export class LoginPage {
  protected email = '';
  protected password = '';
  protected readonly saving = signal(false);
  protected readonly error = signal('');

  constructor(
    private readonly auth: AuthService,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  protected login(): void {
    if (!this.email.trim() || !this.password) {
      this.error.set('Enter your email and password.');
      return;
    }
    this.saving.set(true);
    this.error.set('');
    this.auth.login(this.email.trim(), this.password).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') ?? '/manage';
        void this.router.navigateByUrl(returnUrl);
      },
      error: () => {
        this.saving.set(false);
        this.error.set('Email or password is incorrect.');
      },
    });
  }
}
