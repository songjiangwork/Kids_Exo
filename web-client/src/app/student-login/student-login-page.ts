import { Component, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { PracticeApi } from '../core/practice-api';

@Component({
  selector: 'app-student-login-page',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    RouterLink,
  ],
  templateUrl: './student-login-page.html',
  styleUrl: './student-login-page.scss',
})
export class StudentLoginPage {
  protected householdCode = '';
  protected studentCode = '';
  protected pin = '';
  protected readonly saving = signal(false);
  protected readonly error = signal('');

  constructor(
    private readonly api: PracticeApi,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  protected login(): void {
    if (
      this.householdCode.trim() === ''
      || this.studentCode.trim() === ''
      || this.pin.trim() === ''
    ) {
      this.error.set('Enter your household code, student code, and PIN.');
      return;
    }
    this.saving.set(true);
    this.error.set('');
    this.api.directStudentLogin(
      this.householdCode.trim(),
      this.studentCode.trim(),
      this.pin.trim(),
    ).subscribe({
      next: (response) => {
        this.saving.set(false);
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl');
        void this.router.navigateByUrl(returnUrl ?? response.redirect_to);
      },
      error: () => {
        this.saving.set(false);
        this.error.set('Household code, student code, or PIN is incorrect.');
      },
    });
  }
}
