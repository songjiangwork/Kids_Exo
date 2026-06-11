import { Component, OnInit, computed, signal } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { AuthService } from './core/auth.service';

@Component({
  selector: 'app-root',
  imports: [MatButtonModule, MatToolbarModule, RouterLink, RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly account = computed(() => this.auth.account());
  protected readonly loggingOut = signal(false);

  constructor(
    private readonly auth: AuthService,
    private readonly router: Router,
  ) {}

  ngOnInit(): void {
    this.auth.me().subscribe({ error: () => this.auth.loaded.set(true) });
  }

  protected logout(): void {
    this.loggingOut.set(true);
    this.auth.logout().subscribe({
      next: () => {
        this.loggingOut.set(false);
        void this.router.navigate(['/login']);
      },
      error: () => {
        this.loggingOut.set(false);
        this.auth.account.set(null);
        void this.router.navigate(['/login']);
      },
    });
  }
}
