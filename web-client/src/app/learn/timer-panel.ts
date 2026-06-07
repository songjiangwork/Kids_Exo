import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-timer-panel',
  imports: [MatButtonModule],
  templateUrl: './timer-panel.html',
  styleUrl: './timer-panel.scss',
})
export class TimerPanel {
  @Input() elapsedSeconds = 0;
  @Input() paused = false;
  @Input() updating = false;
  @Input() complete = false;
  @Output() readonly pauseTimer = new EventEmitter<void>();
  @Output() readonly resumeTimer = new EventEmitter<void>();

  protected timerText(): string {
    const minutes = Math.floor(this.elapsedSeconds / 60);
    return `${minutes}:${String(this.elapsedSeconds % 60).padStart(2, '0')}`;
  }
}
