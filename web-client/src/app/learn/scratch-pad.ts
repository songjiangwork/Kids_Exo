import { Component, ElementRef, Input, OnChanges, SimpleChanges, ViewChild, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';

type ScratchMode = 'type' | 'draw';

interface DrawPoint {
  x: number;
  y: number;
}

@Component({
  selector: 'app-scratch-pad',
  imports: [
    FormsModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  templateUrl: './scratch-pad.html',
  styleUrl: './scratch-pad.scss',
})
export class ScratchPad implements OnChanges {
  @Input() resetVersion = 0;
  @ViewChild('scratchCanvas') private scratchCanvas?: ElementRef<HTMLCanvasElement>;

  protected readonly scratchPad = signal('');
  protected readonly scratchMode = signal<ScratchMode>('type');
  protected readonly drawStrokes = signal<DrawPoint[][]>([]);

  private activeStroke: DrawPoint[] | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['resetVersion'] && !changes['resetVersion'].firstChange) {
      this.clearAllScratchWork();
    }
  }

  protected clearScratchPad(): void {
    if (this.scratchMode() === 'draw') {
      this.drawStrokes.set([]);
      this.activeStroke = null;
      this.redrawScratchCanvas();
      return;
    }
    this.scratchPad.set('');
  }

  protected setScratchMode(mode: ScratchMode): void {
    this.scratchMode.set(mode);
    if (mode === 'draw') {
      queueMicrotask(() => this.redrawScratchCanvas());
    }
  }

  protected hasScratchContent(): boolean {
    return this.scratchMode() === 'draw'
      ? this.drawStrokes().length > 0
      : this.scratchPad().length > 0;
  }

  protected startDrawing(event: PointerEvent): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    canvas.setPointerCapture(event.pointerId);
    this.activeStroke = [this.canvasPoint(event, canvas)];
    this.drawStrokes.update((strokes) => [...strokes, this.activeStroke ?? []]);
    this.redrawScratchCanvas();
  }

  protected continueDrawing(event: PointerEvent): void {
    if (!this.activeStroke) {
      return;
    }
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    this.activeStroke.push(this.canvasPoint(event, canvas));
    this.redrawScratchCanvas();
  }

  protected stopDrawing(event: PointerEvent): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (canvas?.hasPointerCapture(event.pointerId)) {
      canvas.releasePointerCapture(event.pointerId);
    }
    this.activeStroke = null;
  }

  private clearAllScratchWork(): void {
    this.scratchPad.set('');
    this.drawStrokes.set([]);
    this.activeStroke = null;
    this.redrawScratchCanvas();
  }

  private canvasPoint(event: PointerEvent, canvas: HTMLCanvasElement): DrawPoint {
    const rect = canvas.getBoundingClientRect();
    return {
      x: ((event.clientX - rect.left) / rect.width) * canvas.width,
      y: ((event.clientY - rect.top) / rect.height) * canvas.height,
    };
  }

  private redrawScratchCanvas(): void {
    const canvas = this.scratchCanvas?.nativeElement;
    if (!canvas) {
      return;
    }
    const context = canvas.getContext('2d');
    if (!context) {
      return;
    }
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.lineCap = 'round';
    context.lineJoin = 'round';
    context.lineWidth = 5;
    context.strokeStyle = '#1f3431';
    for (const stroke of this.drawStrokes()) {
      if (stroke.length === 0) {
        continue;
      }
      context.beginPath();
      context.moveTo(stroke[0].x, stroke[0].y);
      for (const point of stroke.slice(1)) {
        context.lineTo(point.x, point.y);
      }
      context.stroke();
    }
  }
}
