import { Component, SimpleChange } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ScratchPad } from './scratch-pad';

@Component({
  imports: [ScratchPad],
  template: '<app-scratch-pad [resetVersion]="resetVersion" />',
})
class HostComponent {
  resetVersion = 0;
}

describe('ScratchPad', () => {
  async function createFixture(): Promise<ComponentFixture<HostComponent>> {
    await TestBed.configureTestingModule({
      imports: [HostComponent],
    }).compileComponents();

    const fixture = TestBed.createComponent(HostComponent);
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();
    return fixture;
  }

  it('keeps typed notes until cleared', async () => {
    const fixture = await createFixture();
    const component = fixture.debugElement.children[0].componentInstance as ScratchPad;
    (component as any).scratchPad.set('42 x 11: 4 + 2 = 6');
    fixture.detectChanges();

    expect((component as any).scratchPad()).toBe('42 x 11: 4 + 2 = 6');

    const clearButton = Array.from(fixture.nativeElement.querySelectorAll('button') as NodeListOf<HTMLButtonElement>).find(
      (button) => button.textContent?.includes('Clear'),
    ) as HTMLButtonElement;
    clearButton.click();
    fixture.detectChanges();

    expect((component as any).scratchPad()).toBe('');
  });

  it('switches between typed notes and drawing mode without losing typed notes', async () => {
    const fixture = await createFixture();
    const component = fixture.debugElement.children[0].componentInstance as ScratchPad;
    (component as any).scratchPad.set('42 x 11: 4 + 2 = 6');
    fixture.detectChanges();

    (component as any).setScratchMode('draw');
    fixture.detectChanges();

    expect(fixture.nativeElement.querySelector('textarea')).toBeNull();
    expect(fixture.nativeElement.querySelector('canvas')).not.toBeNull();

    (component as any).setScratchMode('type');
    fixture.detectChanges();
    await fixture.whenStable();
    fixture.detectChanges();

    expect((component as any).scratchPad()).toBe('42 x 11: 4 + 2 = 6');
  });

  it('records draw-mode scratch strokes and clears them', async () => {
    const fixture = await createFixture();
    const component = fixture.debugElement.children[0].componentInstance as ScratchPad;

    (component as any).setScratchMode('draw');
    fixture.detectChanges();

    const canvas = fixture.nativeElement.querySelector('canvas') as HTMLCanvasElement;
    canvas.getBoundingClientRect = () => ({
      x: 0,
      y: 0,
      top: 0,
      left: 0,
      right: 300,
      bottom: 120,
      width: 300,
      height: 120,
      toJSON: () => ({}),
    });
    canvas.setPointerCapture = () => undefined;
    canvas.releasePointerCapture = () => undefined;
    canvas.hasPointerCapture = () => true;

    canvas.dispatchEvent(new PointerEvent('pointerdown', { clientX: 10, clientY: 10, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent('pointermove', { clientX: 50, clientY: 60, pointerId: 1 }));
    canvas.dispatchEvent(new PointerEvent('pointerup', { clientX: 50, clientY: 60, pointerId: 1 }));
    fixture.detectChanges();

    expect((component as any).drawStrokes().length).toBe(1);
    expect((component as any).drawStrokes()[0].length).toBe(2);

    (component as any).clearScratchPad();
    fixture.detectChanges();

    expect((component as any).drawStrokes().length).toBe(0);
  });

  it('clears scratch work when reset version changes', async () => {
    const fixture = await createFixture();
    const component = fixture.debugElement.children[0].componentInstance as ScratchPad;
    (component as any).scratchPad.set('carry the 1');
    fixture.detectChanges();

    component.resetVersion = 1;
    component.ngOnChanges({ resetVersion: new SimpleChange(0, 1, false) });
    fixture.detectChanges();

    expect((component as any).scratchPad()).toBe('');
  });
});
