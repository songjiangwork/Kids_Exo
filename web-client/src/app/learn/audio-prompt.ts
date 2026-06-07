import { Component, EventEmitter, Input, Output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-audio-prompt',
  imports: [MatButtonModule],
  templateUrl: './audio-prompt.html',
  styleUrl: './audio-prompt.scss',
})
export class AudioPrompt {
  @Input() audioUrl: string | null | undefined;
  @Input() speechText: string | null | undefined;
  @Output() readonly playAudio = new EventEmitter<void>();

  protected hasAudio(): boolean {
    return Boolean(this.audioUrl || this.speechText);
  }
}
