import React from 'react';
import './MetricTile.css';

export default function MetricTile({ label, value, sublabel, trend }) {
  const isPositive = typeof trend === 'number' ? trend >= 0 : String(trend).startsWith('+');
  const formattedTrend =
    trend === undefined || trend === null
      ? null
      : typeof trend === 'number'
      ? `${trend >= 0 ? '+' : ''}${trend.toFixed(1)}%`
      : trend;

  return (
    <div className="metric-tile">
      <span className="metric-tile__label">{label}</span>
      <div className="metric-tile__value-row">
        <span className="metric-tile__value">{value}</span>
        {formattedTrend && (
          <span className={`metric-tile__trend ${isPositive ? 'is-positive' : 'is-negative'}`}>
            {formattedTrend}
          </span>
        )}
      </div>
      {sublabel && <span className="metric-tile__sublabel">{sublabel}</span>}
    </div>
  );
}
