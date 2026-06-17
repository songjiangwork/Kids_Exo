import { Component, Input } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { RouterLink } from '@angular/router';
import { PracticeResults } from '../core/practice-api';

@Component({
  selector: 'app-practice-results-card',
  imports: [MatButtonModule, MatCardModule, RouterLink],
  templateUrl: './practice-results-card.html',
  styleUrl: './practice-results-card.scss',
})
export class PracticeResultsCard {
  @Input({ required: true }) results!: PracticeResults;
  @Input() showTimer = false;
  @Input() backUrl = '/home';
  @Input() backLabel = 'Back to Home';

  protected resultTimeText(): string {
    return this.formatSeconds(this.results.elapsed_seconds ?? 0);
  }

  private formatSeconds(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }
}
