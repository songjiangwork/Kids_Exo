import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Learner, PracticeApi } from '../core/practice-api';

@Component({
  selector: 'app-learner-management',
  imports: [
    MatButtonModule,
    MatCardModule,
    MatProgressSpinnerModule,
    RouterLink,
  ],
  templateUrl: './learner-management.html',
  styleUrl: './learner-management.scss',
})
export class LearnerManagement implements OnInit {
  protected readonly learners = signal<Learner[]>([]);
  protected readonly loading = signal(true);
  protected readonly deleting = signal(false);
  protected readonly error = signal('');

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.loadLearners();
  }

  protected deleteLearner(learner: Learner): void {
    const confirmed = window.confirm(`Delete learner "${learner.nickname}"? This also removes their practice history.`);
    if (!confirmed) {
      return;
    }
    this.error.set('');
    this.deleting.set(true);
    this.api.deleteLearner(learner.id).subscribe({
      next: () => {
        this.learners.update((entries) => entries.filter((entry) => entry.id !== learner.id));
        this.deleting.set(false);
      },
      error: () => {
        this.error.set('Could not delete this learner.');
        this.deleting.set(false);
      },
    });
  }

  private loadLearners(): void {
    this.api.learners().subscribe({
      next: (learners) => {
        this.learners.set(learners);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load learners.');
        this.loading.set(false);
      },
    });
  }
}
