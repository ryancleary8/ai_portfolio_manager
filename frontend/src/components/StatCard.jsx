import React from 'react';
import './StatCard.css';

export default function StatCard({ title, value, delta, deltaLabel, icon }) {
  const isPositive = typeof delta === 'number' ? delta >= 0 : String(delta).startsWith('+');
  const formattedDelta =
    typeof delta === 'number' ? `${delta >= 0 ? '+' : ''}${delta.toFixed(2)}%` : delta;

  return (
    <div className="stat-card">
      <div className="stat-card__header">
        <span className="stat-card__title">{title}</span>
        {icon && <span className="stat-card__icon">{icon}</span>}
      </div>
      <div className="stat-card__value">{value}</div>
      {delta !== undefined && (
        <div className={`stat-card__delta ${isPositive ? 'is-positive' : 'is-negative'}`}>
          <span className="stat-card__delta-value">{formattedDelta}</span>
          {deltaLabel && <span className="stat-card__delta-label">{deltaLabel}</span>}
        </div>
      )}
    </div>
  );
}
