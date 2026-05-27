import { Component, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { HttpResponse } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { PrintableWorksheetChoice, PracticeApi } from '../core/practice-api';

@Component({
  selector: 'app-printable-worksheet',
  imports: [
    FormsModule,
    MatButtonModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatProgressSpinnerModule,
    MatSelectModule,
    RouterLink,
  ],
  templateUrl: './printable-worksheet.html',
  styleUrl: './printable-worksheet.scss',
})
export class PrintableWorksheet implements OnInit {
  protected readonly choices = signal<PrintableWorksheetChoice[]>([]);
  protected readonly loading = signal(true);
  protected readonly generating = signal(false);
  protected readonly error = signal('');
  protected selectedPresetId = '';
  protected seed: number | null = null;

  protected readonly selectedChoice = computed(() =>
    this.choices().find((choice) => choice.identifier === this.selectedPresetId),
  );

  constructor(private readonly api: PracticeApi) {}

  ngOnInit(): void {
    this.api.printableWorksheets().subscribe({
      next: (choices) => {
        this.choices.set(choices);
        this.selectedPresetId = choices[0]?.identifier ?? '';
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load printable worksheet choices.');
        this.loading.set(false);
      },
    });
  }

  protected generatePdf(): void {
    if (!this.selectedPresetId) {
      return;
    }
    this.error.set('');
    this.generating.set(true);
    this.api.downloadPrintablePdf(this.selectedPresetId, this.seed).subscribe({
      next: (response) => {
        this.download(response);
        this.generating.set(false);
      },
      error: () => {
        this.error.set('Could not generate this PDF worksheet.');
        this.generating.set(false);
      },
    });
  }

  private download(response: HttpResponse<Blob>): void {
    const disposition = response.headers.get('Content-Disposition') ?? '';
    const filename = disposition.match(/filename="([^"]+)"/)?.[1] ?? 'worksheet.pdf';
    const url = URL.createObjectURL(response.body ?? new Blob());
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.click();
    URL.revokeObjectURL(url);
  }
}
