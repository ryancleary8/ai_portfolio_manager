import React from 'react';
import './TradesTable.css';

function formatDate(value) {
  if (!value) return '—';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function normalizeTrade(trade) {
  const side = trade.side ?? trade.action ?? trade.type ?? 'HOLD';
  const quantity = Number(trade.quantity ?? trade.qty ?? trade.shares ?? 0);
  const priceRaw = Number(trade.price ?? trade.fill_price ?? trade.filled_avg_price ?? 0);
  const pnl = Number(trade.pnl ?? trade.profit ?? trade.realized_pl ?? 0);
  const id = trade.id ?? trade.trade_id ?? trade.order_id ?? `${trade.symbol}-${trade.timestamp}`;

  const normalizedSide = side.toUpperCase();

  return {
    id,
    timestamp: trade.timestamp ?? trade.filled_at ?? trade.created_at ?? null,
    symbol: trade.symbol ?? trade.ticker ?? '—',
    side: normalizedSide,
    quantity: Number.isFinite(quantity) ? quantity : 0,
    price: Number.isFinite(priceRaw) ? priceRaw : 0,
    pnl: Number.isFinite(pnl) ? pnl : 0,
    model: trade.model ?? trade.strategy ?? 'AI Agent'
  };
}

export default function TradesTable({ trades }) {
  const normalized = (trades ?? []).map(normalizeTrade);

  return (
    <div className="trades-card">
      <div className="trades-card__header">
        <div>
          <h3>Trade History</h3>
          <p>Executed orders from the reinforcement learning agent</p>
        </div>
      </div>
      <div className="trades-table__wrapper">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Ticker</th>
              <th>Side</th>
              <th className="is-right">Quantity</th>
              <th className="is-right">Fill Price</th>
              <th className="is-right">P&L</th>
              <th>Strategy</th>
            </tr>
          </thead>
          <tbody>
            {normalized.map((trade) => (
              <tr key={trade.id}>
                <td>{formatDate(trade.timestamp)}</td>
                <td>
                  <span className="ticker-pill">{trade.symbol}</span>
                </td>
                <td>
                  <span
                    className={`trade-side ${
                      trade.side === 'BUY' ? 'is-buy' : trade.side === 'SELL' ? 'is-sell' : 'is-hold'
                    }`}
                  >
                    {trade.side}
                  </span>
                </td>
                <td className="is-right">{trade.quantity.toLocaleString()}</td>
                <td className="is-right">${trade.price.toFixed(2)}</td>
                <td className={`is-right ${trade.pnl >= 0 ? 'is-positive' : 'is-negative'}`}>
                  {trade.pnl === 0 ? '—' : `${trade.pnl >= 0 ? '+' : '-'}$${Math.abs(trade.pnl).toFixed(2)}`}
                </td>
                <td>{trade.model}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
