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
    path: 'learn/session/:token',
    loadComponent: () => import('./learn/student-practice').then((module) => module.StudentPractice),
  },
  { path: '', pathMatch: 'full', redirectTo: 'manage' },
  { path: '**', redirectTo: 'manage' },
];
