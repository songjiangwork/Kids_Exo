import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { LearnerForm } from './learner-form';

@Component({ template: '' })
class EmptyRoute {}

describe('LearnerForm', () => {
  it('creates a learner from the shared form', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerForm],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([{ path: 'manage/learners', component: EmptyRoute }]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerForm);
    fixture.detectChanges();
    const component = fixture.componentInstance as any;
    component.nickname = 'Mia';
    component.save();

    const http = TestBed.inject(HttpTestingController);
    const request = http.expectOne('/api/learners');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ nickname: 'Mia' });
    request.flush({ id: 3, nickname: 'Mia', active: true });
  });
});
