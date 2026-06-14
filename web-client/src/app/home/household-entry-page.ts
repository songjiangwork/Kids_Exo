import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { HouseholdStudent, PracticeApi } from '../core/practice-api';

@Component({
  selector: 'app-household-entry-page',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
  ],
  templateUrl: './household-entry-page.html',
  styleUrl: './household-entry-page.scss',
})
export class HouseholdEntryPage implements OnInit {
  protected readonly students = signal<HouseholdStudent[]>([]);
  protected readonly selectedStudent = signal<HouseholdStudent | null>(null);
  protected readonly loading = signal(true);
  protected readonly studentSaving = signal(false);
  protected readonly parentSaving = signal(false);
  protected readonly parentPinChanging = signal(false);
  protected readonly showParentPinForm = signal(false);
  protected readonly error = signal('');
  protected readonly studentError = signal('');
  protected readonly parentError = signal('');
  protected readonly parentPinError = signal('');
  protected readonly parentPinMessage = signal('');
  protected studentPin = '';
  protected parentPin = '';
  protected currentParentPin = '';
  protected newParentPin = '';
  protected confirmParentPin = '';

  constructor(
    private readonly api: PracticeApi,
    private readonly route: ActivatedRoute,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.api.householdStudents().subscribe({
      next: (response) => {
        this.students.set(response.students);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load household students.');
        this.loading.set(false);
      },
    });
  }

  protected selectStudent(student: HouseholdStudent): void {
    this.selectedStudent.set(student);
    this.studentPin = '';
    this.studentError.set('');
  }

  protected loginStudent(): void {
    const student = this.selectedStudent();
    if (student === null || this.studentPin.trim() === '') {
      this.studentError.set('Enter the student PIN.');
      return;
    }
    this.studentSaving.set(true);
    this.studentError.set('');
    this.api.studentLogin(student.id, this.studentPin.trim()).subscribe({
      next: (response) => {
        this.studentSaving.set(false);
        void this.router.navigate(['/manage/students', response.student.id]);
      },
      error: () => {
        this.studentSaving.set(false);
        this.studentError.set('That student PIN did not work.');
      },
    });
  }

  protected unlockParent(): void {
    if (this.parentPin.trim() === '') {
      this.parentError.set('Enter the parent PIN.');
      return;
    }
    this.parentSaving.set(true);
    this.parentError.set('');
    this.api.unlockParent(this.parentPin.trim()).subscribe({
      next: () => {
        this.parentSaving.set(false);
        void this.router.navigateByUrl(this.route.snapshot.queryParamMap.get('returnUrl') ?? '/manage');
      },
      error: () => {
        this.parentSaving.set(false);
        this.parentError.set('That parent PIN did not work.');
      },
    });
  }

  protected toggleParentPinForm(): void {
    this.showParentPinForm.update((visible) => !visible);
    this.parentPinError.set('');
    this.parentPinMessage.set('');
  }

  protected changeParentPin(): void {
    const currentPin = this.currentParentPin.trim();
    const newPin = this.newParentPin.trim();
    if (currentPin === '') {
      this.parentPinMessage.set('');
      this.parentPinError.set('Enter the current parent PIN.');
      return;
    }
    if (!/^\d{4,12}$/.test(newPin)) {
      this.parentPinMessage.set('');
      this.parentPinError.set('New PIN must be 4 to 12 digits.');
      return;
    }
    if (newPin !== this.confirmParentPin.trim()) {
      this.parentPinMessage.set('');
      this.parentPinError.set('PIN confirmation does not match.');
      return;
    }
    this.parentPinChanging.set(true);
    this.parentPinError.set('');
    this.parentPinMessage.set('');
    this.api.changeParentPin(currentPin, newPin).subscribe({
      next: () => {
        this.currentParentPin = '';
        this.newParentPin = '';
        this.confirmParentPin = '';
        this.parentPinChanging.set(false);
        this.parentPinMessage.set('Parent PIN has been changed.');
      },
      error: () => {
        this.parentPinChanging.set(false);
        this.parentPinError.set('Could not change the parent PIN.');
      },
    });
  }

  protected avatarLabel(student: HouseholdStudent): string {
    const labels: Record<string, string> = {
      fox: 'Fox',
      panda: 'Panda',
      owl: 'Owl',
      bear: 'Bear',
      cat: 'Cat',
      dog: 'Dog',
    };
    return labels[student.avatar_key] ?? 'Student';
  }
}
