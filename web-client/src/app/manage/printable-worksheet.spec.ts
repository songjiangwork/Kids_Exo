import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { PrintableWorksheet } from './printable-worksheet';

describe('PrintableWorksheet', () => {
  it('loads all printable worksheet choices and requests a PDF download', async () => {
    await TestBed.configureTestingModule({
      imports: [PrintableWorksheet],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    const fixture = TestBed.createComponent(PrintableWorksheet);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/printable-worksheets').flush([
      {
        identifier: 'math.mental_multiplication.square_ending_in_5.beginner',
        subject: 'Math',
        category: 'Mental Multiplication',
        title: 'Squares Ending in 5',
      },
      {
        identifier: 'math.mental_multiplication.mixed_practice_100',
        subject: 'Math',
        category: 'Mental Multiplication',
        title: 'Mixed Practice - 100 Questions',
      },
    ]);
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('Printable worksheet');
    expect(fixture.nativeElement.textContent).toContain('Squares Ending in 5');
    expect(fixture.nativeElement.textContent).toContain('Mixed Practice - 100 Questions');

    const component = fixture.componentInstance as any;
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:worksheet');
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    component.seed = 525;
    component.generatePdf();
    const request = http.expectOne('/api/printable-worksheets/pdf');
    expect(request.request.body).toEqual({
      preset_id: 'math.mental_multiplication.square_ending_in_5.beginner',
      seed: 525,
      include_warmup: true,
      page_count: 1,
    });
    request.flush(new Blob(['pdf']), {
      headers: {
        'Content-Disposition': 'attachment; filename="squares-ending-in-5-seed-525.pdf"',
      },
    });
  });

  it('can request a printable worksheet without warm-up', async () => {
    await TestBed.configureTestingModule({
      imports: [PrintableWorksheet],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    const fixture = TestBed.createComponent(PrintableWorksheet);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/printable-worksheets').flush([
      {
        identifier: 'math.mental_multiplication.square_ending_in_5.beginner',
        subject: 'Math',
        category: 'Mental Multiplication',
        title: 'Squares Ending in 5',
      },
    ]);

    const component = fixture.componentInstance as any;
    component.includeWarmup = false;
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:worksheet-without-warmup');
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    component.generatePdf();

    const request = http.expectOne('/api/printable-worksheets/pdf');
    expect(request.request.body).toEqual({
      preset_id: 'math.mental_multiplication.square_ending_in_5.beginner',
      include_warmup: false,
      page_count: 1,
    });
    request.flush(new Blob(['pdf']));
  });

  it('can request a custom printable question count', async () => {
    await TestBed.configureTestingModule({
      imports: [PrintableWorksheet],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();

    const fixture = TestBed.createComponent(PrintableWorksheet);
    fixture.detectChanges();
    const http = TestBed.inject(HttpTestingController);
    http.expectOne('/api/printable-worksheets').flush([
      {
        identifier: 'math.mental_multiplication.square_ending_in_5.beginner',
        subject: 'Math',
        category: 'Mental Multiplication',
        title: 'Squares Ending in 5',
      },
    ]);

    const component = fixture.componentInstance as any;
    component.lengthMode = 'custom';
    component.customQuestionCount = 64;
    vi.spyOn(URL, 'createObjectURL').mockReturnValue('blob:custom-worksheet');
    vi.spyOn(URL, 'revokeObjectURL').mockImplementation(() => undefined);
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
    component.generatePdf();

    const request = http.expectOne('/api/printable-worksheets/pdf');
    expect(request.request.body).toEqual({
      preset_id: 'math.mental_multiplication.square_ending_in_5.beginner',
      include_warmup: true,
      question_count: 64,
    });
    request.flush(new Blob(['pdf']));
  });
});
