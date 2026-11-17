import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ButtonVariant = 'primary' | 'secondary' | 'subtle';

@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type"
      [disabled]="disabled"
      (click)="onClick.emit($event)"
      [class]="'btn btn-' + variant"
      [class.btn-sm]="size === 'sm'"
      [class.btn-md]="size === 'md'"
      [class.btn-lg]="size === 'lg'"
    >
      <ng-content></ng-content>
    </button>
  `,
  styles: [`
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      border-radius: 0.625rem;
      font-weight: 600;
      cursor: pointer;
      font-family: inherit;
      transition: background-color 0.15s ease, border-color 0.15s ease, color 0.15s ease, transform 0.05s ease;

      &:disabled {
        opacity: 0.55;
        cursor: not-allowed;
      }

      &:active:not(:disabled) {
        transform: scale(0.99);
      }
    }

    .btn-sm {
      padding: 0.375rem 0.75rem;
      font-size: 0.75rem;
    }

    .btn-md {
      padding: 0.5rem 1rem;
      font-size: 0.8125rem;
    }

    .btn-lg {
      padding: 0.75rem 1.25rem;
      font-size: 0.875rem;
    }

    /* Primary Button: Uses Accent */
    .btn-primary {
      background-color: var(--accent);
      color: var(--accent-contrast);
      border: 1px solid transparent;
      box-shadow: var(--shadow-sm);

      &:hover:not(:disabled) {
        background-color: var(--accent-hover);
      }

      &:focus-visible {
        outline: none;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.35);
      }
    }

    /* Secondary Button: Outlined with --border, NO accent fill */
    .btn-secondary {
      background-color: var(--surface);
      color: var(--text-primary);
      border: 1px solid var(--border);
      box-shadow: var(--shadow-sm);

      &:hover:not(:disabled) {
        background-color: var(--surface-alt);
        border-color: var(--text-secondary);
      }

      &:focus-visible {
        outline: none;
        border-color: var(--text-primary);
      }
    }

    /* Subtle Button: Minimal ghost action */
    .btn-subtle {
      background-color: transparent;
      color: var(--text-secondary);
      border: 1px solid transparent;

      &:hover:not(:disabled) {
        background-color: var(--surface-alt);
        color: var(--text-primary);
      }
    }
  `]
})
export class ButtonComponent {
  @Input() variant: ButtonVariant = 'secondary';
  @Input() size: 'sm' | 'md' | 'lg' = 'md';
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
  @Input() disabled = false;
  @Output() onClick = new EventEmitter<MouseEvent>();
}
