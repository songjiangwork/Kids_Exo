import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { ActivatedRoute, convertToParamMap, provideRouter } from '@angular/router';
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

  it('resets a student PIN from the edit form', async () => {
    await TestBed.configureTestingModule({
      imports: [LearnerForm],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([{ path: 'manage/students', component: EmptyRoute }]),
        {
          provide: ActivatedRoute,
          useValue: { snapshot: { paramMap: convertToParamMap({ id: '3' }) } },
        },
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(LearnerForm);
    fixture.detectChanges();

    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/learners/3').flush({ id: 3, nickname: 'Mia', active: true });

    const component = fixture.componentInstance as any;
    component.studentPin = '5678';
    component.studentPinConfirm = '5678';
    component.resetStudentPin();

    const request = http.expectOne('/api/learners/3/student-pin');
    expect(request.request.method).toBe('POST');
    expect(request.request.body).toEqual({ pin: '5678' });
    request.flush(null);
    expect(component.pinMessage()).toBe('Student PIN has been reset.');
  });
});
