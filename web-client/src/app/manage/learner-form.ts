import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { PracticeApi } from '../core/practice-api';

@Component({
  selector: 'app-learner-form',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatCheckboxModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './learner-form.html',
  styleUrl: './learner-form.scss',
})
export class LearnerForm implements OnInit {
  protected readonly loading = signal(false);
  protected readonly saving = signal(false);
  protected readonly error = signal('');
  protected learnerId: number | null = null;
  protected nickname = '';
  protected active = true;

  constructor(
    private readonly api: PracticeApi,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    const rawId = this.route.snapshot.paramMap.get('id');
    this.learnerId = rawId === null ? null : Number(rawId);
    if (this.learnerId === null) {
      return;
    }
    this.loading.set(true);
    this.api.learner(this.learnerId).subscribe({
      next: (learner) => {
        this.nickname = learner.nickname;
        this.active = learner.active;
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load this learner.');
        this.loading.set(false);
      },
    });
  }

  protected save(): void {
    const nickname = this.nickname.trim();
    if (!nickname) {
      this.error.set('Learner nickname is required.');
      return;
    }
    this.error.set('');
    this.saving.set(true);
    const request = this.learnerId === null
      ? this.api.createLearner(nickname)
      : this.api.updateLearner({ id: this.learnerId, nickname, active: this.active });
    request.subscribe({
      next: () => this.router.navigate(['/manage/learners']),
      error: () => {
        this.error.set('Could not save this learner.');
        this.saving.set(false);
      },
    });
  }
}
