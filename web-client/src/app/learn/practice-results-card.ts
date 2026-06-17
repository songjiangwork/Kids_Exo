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

  protected hintText(feedbackCode?: string | null): string {
    switch (feedbackCode) {
      case 'case_mismatch':
        return 'Check capitalization.';
      case 'missing_or_wrong_accents':
        return 'Check the accent marks.';
      case 'hyphen_mismatch':
        return 'Check the hyphen.';
      case 'apostrophe_mismatch':
        return 'Check the apostrophe.';
      case 'special_character_mismatch':
        return 'Check the special characters.';
      case 'spelling_mismatch':
        return 'Check the spelling.';
      default:
        return '';
    }
  }

  private formatSeconds(seconds: number): string {
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }
}
