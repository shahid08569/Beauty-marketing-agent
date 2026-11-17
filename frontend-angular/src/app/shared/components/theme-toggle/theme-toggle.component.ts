import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ThemeService } from '../../../core/theme/theme.service';

@Component({
  selector: 'app-theme-toggle',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      type="button"
      (click)="themeService.toggleTheme()"
      class="theme-toggle-btn"
      [attr.aria-label]="'Switch to ' + (themeService.currentTheme() === 'light' ? 'dark' : 'light') + ' mode'"
    >
      <svg *ngIf="themeService.currentTheme() === 'light'" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
      </svg>
      <svg *ngIf="themeService.currentTheme() === 'dark'" class="icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 9H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
      </svg>
      <span class="mode-text">{{ themeService.currentTheme() === 'light' ? 'Dark' : 'Light' }}</span>
    </button>
  `,
  styles: [`
    .theme-toggle-btn {
      display: inline-flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.375rem 0.625rem;
      border-radius: 0.5rem;
      background-color: var(--surface);
      border: 1px solid var(--border);
      color: var(--text-secondary);
      font-size: 0.75rem;
      font-weight: 600;
      cursor: pointer;
      box-shadow: var(--shadow-sm);
      transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;

      &:hover {
        background-color: var(--surface-alt);
        color: var(--text-primary);
        border-color: var(--text-secondary);
      }
    }

    .icon {
      width: 0.875rem;
      height: 0.875rem;
    }
  `]
})
export class ThemeToggleComponent {
  readonly themeService = inject(ThemeService);
}
