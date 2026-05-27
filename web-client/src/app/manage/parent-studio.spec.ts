import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { ParentStudio } from './parent-studio';

describe('ParentStudio', () => {
  it('loads the online catalog and presents session controls', async () => {
    await TestBed.configureTestingModule({
      imports: [ParentStudio],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
        provideRouter([]),
      ],
    }).compileComponents();

    const fixture = TestBed.createComponent(ParentStudio);
    fixture.detectChanges();
    TestBed.inject(HttpTestingController).expectOne('/api/practice-plugins').flush({
      default_locale: 'en-CA',
      question_counts: [10, 20, 30],
      feedback_modes: ['immediate', 'deferred'],
      show_timer_configurable: true,
      plugins: [{
        plugin: 'multiply_by_11',
        title: 'Multiply by 11',
        description: 'Practise multiplying by 11.',
        subject: 'Math',
        category: 'Mental Multiplication',
        default_locale: 'en-CA',
        locale_coverage: [],
        settings: [],
      }],
    });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Create a practice session');
    expect(fixture.nativeElement.textContent).toContain('Multiply by 11');
    expect(fixture.nativeElement.textContent).toContain('Start practice');
  });
});
