import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: 'manage',
    loadComponent: () => import('./manage/parent-studio').then((module) => module.ParentStudio),
  },
  {
    path: 'manage/worksheets',
    loadComponent: () =>
      import('./manage/printable-worksheet').then((module) => module.PrintableWorksheet),
  },
  {
    path: 'manage/learners',
    loadComponent: () =>
      import('./manage/learner-management').then((module) => module.LearnerManagement),
  },
  {
    path: 'manage/learners/new',
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/learners/:id/edit',
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/learners/:id',
    loadComponent: () => import('./manage/learner-detail').then((module) => module.LearnerDetail),
  },
  {
    path: 's/:token',
    loadComponent: () => import('./learn/student-practice').then((module) => module.StudentPractice),
  },
  {
    path: 'learn/session/:token',
    loadComponent: () => import('./learn/student-practice').then((module) => module.StudentPractice),
  },
  { path: '', pathMatch: 'full', redirectTo: 'manage' },
  { path: '**', redirectTo: 'manage' },
];
