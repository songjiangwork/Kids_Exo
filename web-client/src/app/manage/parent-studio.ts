import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { of, switchMap } from 'rxjs';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import {
  Assignment,
  AssignmentCreateRequest,
  Learner,
  OnlineCatalog,
  PracticeApi,
} from '../core/practice-api';
import { AssignmentForm } from './assignment-form';

@Component({
  selector: 'app-parent-studio',
  imports: [
    AssignmentForm,
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatFormFieldModule,
    MatIconModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    RouterLink,
  ],
  templateUrl: './parent-studio.html',
  styleUrl: './parent-studio.scss',
})
export class ParentStudio implements OnInit {
  protected readonly catalog = signal<OnlineCatalog | null>(null);
  protected readonly loading = signal(true);
  protected readonly saving = signal(false);
  protected readonly error = signal('');
  protected readonly createdAssignment = signal<Assignment | null>(null);
  protected readonly learners = signal<Learner[]>([]);

  protected nickname = 'Alex';
  protected learnerId: number | null = null;

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.api.catalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.api.learners().subscribe({
          next: (learners) => {
            this.learners.set(learners);
            if (learners.length > 0) {
              const latestLearner = learners[learners.length - 1];
              this.learnerId = latestLearner.id;
              this.nickname = latestLearner.nickname;
            }
            this.loading.set(false);
          },
          error: () => {
            this.error.set('Could not load learners.');
            this.loading.set(false);
          },
        });
      },
      error: () => {
        this.error.set('Could not load practice choices. Is the API running?');
        this.loading.set(false);
      },
    });
  }

  protected assignHomework(request: AssignmentCreateRequest): void {
    if (!this.nickname.trim()) {
      this.error.set('Choose a learner or enter a new learner name.');
      return;
    }
    this.error.set('');
    this.saving.set(true);
    this.createdAssignment.set(null);
    const learner = this.learnerId === null
      ? this.api.createLearner(this.nickname.trim())
      : of({ id: this.learnerId, nickname: this.nickname, active: true });
    learner.pipe(
      switchMap((savedLearner) => {
        this.learnerId = savedLearner.id;
        if (!this.learners().some((entry) => entry.id === savedLearner.id)) {
          this.learners.update((entries) => [...entries, savedLearner]);
        }
        return this.api.createAssignment(savedLearner.id, {
          ...request,
          source_type: 'parent_assigned',
          created_by_role: 'parent',
        });
      }),
    ).subscribe({
      next: (assignment) => {
        this.createdAssignment.set(assignment);
        this.saving.set(false);
      },
      error: () => {
        this.error.set('Could not assign this homework.');
        this.saving.set(false);
      },
    });
  }

  protected selectLearner(learnerId: number | null): void {
    this.learnerId = learnerId;
    this.createdAssignment.set(null);
    if (learnerId === null) {
      this.nickname = '';
      return;
    }
    const learner = this.learners().find((entry) => entry.id === learnerId);
    this.nickname = learner?.nickname ?? '';
  }
}
