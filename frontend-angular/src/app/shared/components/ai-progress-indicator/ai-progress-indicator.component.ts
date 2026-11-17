import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ai-progress-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="progress-card">
      <div class="progress-header">
        <div class="status-left">
          <span class="ai-pulse-dot"></span>
          <span class="status-title">{{ stageTitle }}</span>
        </div>
        <span class="percentage-badge">{{ progress }}%</span>
      </div>
      <p class="status-detail">{{ detailText }}</p>
      <div class="track">
        <div class="fill" [style.width.%]="progress"></div>
      </div>
    </div>
  `,
  styles: [`
    .progress-card {
      background-color: var(--surface);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 1rem;
      box-shadow: var(--shadow-sm);
    }

    .progress-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.5rem;
    }

    .status-left {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .ai-pulse-dot {
      width: 0.5rem;
      height: 0.5rem;
      border-radius: 50%;
      background-color: var(--accent);
      animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .status-title {
      font-size: 0.8125rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .percentage-badge {
      font-family: monospace;
      font-size: 0.75rem;
      font-weight: 700;
      color: var(--accent);
      background-color: var(--surface-alt);
      border: 1px solid var(--border);
      padding: 0.125rem 0.5rem;
      border-radius: 0.25rem;
    }

    .status-detail {
      font-size: 0.75rem;
      color: var(--text-secondary);
      margin: 0 0 0.625rem 0;
    }

    .track {
      width: 100%;
      height: 0.375rem;
      background-color: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 9999px;
      overflow: hidden;
    }

    .fill {
      height: 100%;
      background-color: var(--accent);
      transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.15); }
    }
  `]
})
export class AiProgressIndicatorComponent {
  @Input() progress = 0;
  @Input() stageTitle = 'Stage: Market Intelligence & Analysis';
  @Input() detailText = 'Synthesizing creative angles...';
}
