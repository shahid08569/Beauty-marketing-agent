import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ai-generate-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      type="button"
      [disabled]="isLoading || disabled"
      (click)="onClick.emit($event)"
      class="ai-gen-btn"
      [class.loading]="isLoading"
    >
      <span *ngIf="isLoading" class="spinner"></span>
      <span class="btn-text">
        <ng-content></ng-content>
      </span>
    </button>
  `,
  styles: [`
    .ai-gen-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      width: 100%;
      padding: 0.75rem 1.25rem;
      border-radius: 0.75rem;
      font-size: 0.875rem;
      font-weight: 600;
      border: 1px solid transparent;
      cursor: pointer;
      background-color: var(--accent);
      color: var(--accent-contrast);
      box-shadow: var(--shadow-sm);
      transition: background-color 0.15s ease, opacity 0.15s ease, transform 0.05s ease;

      &:hover:not(:disabled) {
        background-color: var(--accent-hover);
      }

      &:active:not(:disabled) {
        transform: scale(0.99);
      }

      &:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.35);
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .spinner {
      width: 1rem;
      height: 1rem;
      border: 2px solid var(--accent-contrast);
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  `]
})
export class AiGenerateButtonComponent {
  @Input() isLoading = false;
  @Input() disabled = false;
  @Output() onClick = new EventEmitter<MouseEvent>();
}
