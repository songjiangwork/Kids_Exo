import { Routes } from '@angular/router';
import { parentAuthGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./login/login-page').then((module) => module.LoginPage),
  },
  {
    path: 'manage',
    canActivate: [parentAuthGuard],
    loadComponent: () => import('./manage/parent-studio').then((module) => module.ParentStudio),
  },
  {
    path: 'manage/worksheets',
    canActivate: [parentAuthGuard],
    loadComponent: () =>
      import('./manage/printable-worksheet').then((module) => module.PrintableWorksheet),
  },
  {
    path: 'manage/learners',
    canActivate: [parentAuthGuard],
    loadComponent: () =>
      import('./manage/learner-management').then((module) => module.LearnerManagement),
  },
  {
    path: 'manage/learners/new',
    canActivate: [parentAuthGuard],
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/learners/:id/edit',
    canActivate: [parentAuthGuard],
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/learners/:id',
    canActivate: [parentAuthGuard],
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
