import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import {
  LearnerMistakeEntry,
  LearnerSkillBreakdown,
  SessionSummary,
} from '../core/practice-api';

export interface LearnerSummaryCard {
  label: string;
  value: string;
  note: string;
}

@Component({
  selector: 'app-learner-overview-panel',
  imports: [MatButtonModule, MatCardModule, RouterLink],
  templateUrl: './learner-overview-panel.html',
  styleUrl: './learner-overview-panel.scss',
})
export class LearnerOverviewPanel {
  @Input() summaryCards: LearnerSummaryCard[] = [];
  @Input() recentSessions: SessionSummary[] = [];
  @Input() weakestSkills: LearnerSkillBreakdown[] = [];
  @Input() topMistakes: LearnerMistakeEntry[] = [];
  @Input() creatingPracticePlugin: string | null = null;

  @Output() createPracticeFromPlugin = new EventEmitter<string>();
  @Output() reviewResults = new EventEmitter<SessionSummary>();

  protected formatPercent(ratio: number): string {
    return `${Math.round(ratio * 100)}%`;
  }

  protected formatTime(seconds: number | null): string {
    if (seconds === null) {
      return 'No time yet';
    }
    const minutes = Math.floor(seconds / 60);
    return `${minutes}:${String(seconds % 60).padStart(2, '0')}`;
  }

  protected formatAnswer(value: unknown): string {
    if (value === null || value === undefined) {
      return 'No answer';
    }
    return String(value);
  }

  protected canReview(session: SessionSummary): boolean {
    return session.status === 'completed';
  }

  protected isCreating(pluginId: string): boolean {
    return this.creatingPracticePlugin === pluginId;
  }
}
