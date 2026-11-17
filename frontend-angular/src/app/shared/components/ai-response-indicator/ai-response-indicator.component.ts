import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ai-response-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ai-indicator-box">
      <div class="indicator-header">
        <div class="indicator-title">
          <span class="ai-status-pulse"></span>
          <span>AI Model Intelligence:</span>
        </div>
        <span class="ai-badge">{{ modelName }}</span>
      </div>
      <div class="indicator-meta">
        <span class="meta-label">Narrative Angle:</span>
        <span class="meta-value">{{ narrativeAngle }}</span>
      </div>
    </div>
  `,
  styles: [`
    .ai-indicator-box {
      background-color: var(--surface-alt);
      border: 1px solid var(--border);
      border-radius: 0.75rem;
      padding: 0.75rem 1rem;
      font-size: 0.75rem;
    }

    .indicator-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 0.375rem;
    }

    .indicator-title {
      display: flex;
      align-items: center;
      gap: 0.375rem;
      font-weight: 700;
      color: var(--text-primary);
    }

    .ai-status-pulse {
      width: 0.5rem;
      height: 0.5rem;
      border-radius: 50%;
      background-color: var(--accent);
      animation: pulse 1.5s infinite;
    }

    .ai-badge {
      background-color: var(--surface);
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 0.125rem 0.5rem;
      border-radius: 0.25rem;
      font-weight: 600;
      font-size: 0.6875rem;
    }

    .indicator-meta {
      display: flex;
      align-items: center;
      gap: 0.375rem;
      color: var(--text-secondary);
      font-size: 0.6875rem;
    }

    .meta-label {
      font-weight: 600;
    }

    .meta-value {
      color: var(--text-primary);
      font-weight: 500;
    }

    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(1.15); }
    }
  `]
})
export class AiResponseIndicatorComponent {
  @Input() modelName = 'Auto-Smart Neural Engine';
  @Input() narrativeAngle = 'High Conversion Direct Angle';
}
