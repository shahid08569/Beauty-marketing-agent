import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="iw-card" [class.hoverable]="hoverable">
      <div *ngIf="title" class="card-header">
        <h3 class="card-title">{{ title }}</h3>
        <ng-content select="[card-header-action]"></ng-content>
      </div>
      <div class="card-body">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  styles: [`
    .iw-card {
      background-color: var(--surface);
      border: 1px solid var(--border);
      border-radius: 1rem;
      padding: 1.5rem;
      box-shadow: var(--shadow-sm);
      transition: border-color 0.15s ease, box-shadow 0.15s ease;
    }

    .hoverable:hover {
      box-shadow: var(--shadow-md);
      border-color: var(--border);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-bottom: 0.75rem;
      margin-bottom: 1rem;
      border-bottom: 1px solid var(--border);
    }

    .card-title {
      margin: 0;
      font-size: 1rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .card-body {
      color: var(--text-primary);
    }
  `]
})
export class CardComponent {
  @Input() title?: string;
  @Input() hoverable = false;
}
