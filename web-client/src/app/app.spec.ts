import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { Component } from '@angular/core';
import { provideRouter } from '@angular/router';
import { App } from './app';

@Component({ template: '' })
class TestLoginComponent {}

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([{ path: 'login', component: TestLoginComponent }]),
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    TestBed.inject(HttpTestingController).expectOne('/api/auth/me').flush({ account: null });
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render title', async () => {
    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    TestBed.inject(HttpTestingController).expectOne('/api/auth/me').flush({ account: null });
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.textContent).toContain('Kids Exo');
  });

  it('renders current parent and logs out', async () => {
    const fixture = TestBed.createComponent(App);
    const http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
    http.expectOne('/api/auth/me').flush({
      account: {
        id: 1,
        email: 'parent@example.com',
        display_name: 'Parent',
        active: true,
      },
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Parent');
    const logout = Array.from(
      fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>,
    ).find((button) => button.textContent?.includes('Logout')) as HTMLButtonElement;
    logout.click();
    http.expectOne('/api/auth/logout').flush({ account: null });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Login');
  });
});
