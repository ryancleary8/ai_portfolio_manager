import React from 'react';
import './SignalGrid.css';

function normalizeSignal(signal) {
  const confidenceRaw = Number(signal.confidence ?? signal.score ?? signal.signal_strength ?? 0);
  const positionSizeRaw = Number(signal.positionSize ?? signal.weight ?? signal.position_size ?? 0);

  const confidence = confidenceRaw > 1 ? confidenceRaw / 100 : confidenceRaw;
  const positionSize = positionSizeRaw > 1 ? positionSizeRaw / 100 : positionSizeRaw;

  return {
    symbol: signal.symbol ?? signal.ticker ?? '—',
    action: (signal.action ?? signal.side ?? 'HOLD').toUpperCase(),
    confidence,
    positionSize,
    thesis: signal.thesis ?? signal.reason ?? signal.notes ?? 'Signal details unavailable.'
  };
}

export default function SignalGrid({ signals, modelName }) {
  const headings = {
    tech: 'Tech Sector Agent',
    energy: 'Energy & Finance Agent'
  };

  const normalized = (signals ?? []).map(normalizeSignal);

  return (
    <div className="signals-card">
      <div className="signals-card__header">
        <div>
          <h3>AI Signals</h3>
          <p>{headings[modelName] || 'AI Trading Agent'} strategic directives</p>
        </div>
      </div>
      <div className="signals-grid">
        {normalized.map((signal) => (
          <article key={signal.symbol} className={`signal-card signal-${signal.action.toLowerCase()}`}>
            <header>
              <span className="signal-card__ticker">{signal.symbol}</span>
              <span className="signal-card__action">{signal.action}</span>
            </header>
            <div className="signal-card__meta">
              <span>
                Confidence
                <strong>{Math.round(signal.confidence * 100)}%</strong>
              </span>
              <span>
                Position size
                <strong>{Math.round(signal.positionSize * 100)}%</strong>
              </span>
            </div>
            <p className="signal-card__thesis">{signal.thesis}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
