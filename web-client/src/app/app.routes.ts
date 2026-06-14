import { Routes } from '@angular/router';
import { parentAuthGuard, parentUnlockGuard, studentOrParentAccessGuard } from './core/auth.guard';

export const routes: Routes = [
  {
    path: 'login',
    loadComponent: () => import('./login/login-page').then((module) => module.LoginPage),
  },
  {
    path: 'home',
    canActivate: [parentAuthGuard],
    loadComponent: () => import('./home/household-entry-page').then((module) => module.HouseholdEntryPage),
  },
  {
    path: 'manage',
    canActivate: [parentAuthGuard, parentUnlockGuard],
    loadComponent: () => import('./manage/parent-studio').then((module) => module.ParentStudio),
  },
  {
    path: 'manage/worksheets',
    canActivate: [parentAuthGuard, parentUnlockGuard],
    loadComponent: () =>
      import('./manage/printable-worksheet').then((module) => module.PrintableWorksheet),
  },
  {
    path: 'manage/students',
    canActivate: [parentAuthGuard, parentUnlockGuard],
    loadComponent: () =>
      import('./manage/learner-management').then((module) => module.LearnerManagement),
  },
  {
    path: 'manage/students/new',
    canActivate: [parentAuthGuard, parentUnlockGuard],
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/students/:id/edit',
    canActivate: [parentAuthGuard, parentUnlockGuard],
    loadComponent: () => import('./manage/learner-form').then((module) => module.LearnerForm),
  },
  {
    path: 'manage/students/:id',
    canActivate: [parentAuthGuard, studentOrParentAccessGuard],
    loadComponent: () => import('./manage/learner-detail').then((module) => module.LearnerDetail),
  },
  { path: 'manage/learners', pathMatch: 'full', redirectTo: 'manage/students' },
  { path: 'manage/learners/new', pathMatch: 'full', redirectTo: 'manage/students/new' },
  { path: 'manage/learners/:id/edit', redirectTo: 'manage/students/:id/edit' },
  { path: 'manage/learners/:id', redirectTo: 'manage/students/:id' },
  {
    path: 's/:token',
    loadComponent: () => import('./learn/student-practice').then((module) => module.StudentPractice),
  },
  {
    path: 'learn/session/:token',
    loadComponent: () => import('./learn/student-practice').then((module) => module.StudentPractice),
  },
  { path: '', pathMatch: 'full', redirectTo: 'home' },
  { path: '**', redirectTo: 'home' },
];
