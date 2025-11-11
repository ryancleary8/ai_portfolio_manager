import React from 'react';
import './PositionsTable.css';

function normalizePosition(position) {
  const quantityRaw = Number(position.quantity ?? position.qty ?? position.shares ?? 0);
  const averagePrice = Number(
    position.averagePrice ?? position.avg_price ?? position.avgEntryPrice ?? position.avg_entry_price ?? 0
  );
  const marketPrice = Number(
    position.marketPrice ?? position.current_price ?? position.currentPrice ?? position.market_price ?? 0
  );
  const pnlRaw = Number(
    position.unrealizedPnl ?? position.unrealized_pl ?? position.unrealized_pl ?? position.pnl ?? 0
  );
  const pnlPercentRaw = Number(
    position.unrealizedPnlPercent ?? position.unrealized_plpc ?? position.unrealized_pl_percent ?? position.pnl_percent ?? 0
  );

  const pnlPercent = Number.isFinite(pnlPercentRaw)
    ? Math.abs(pnlPercentRaw) > 1
      ? pnlPercentRaw
      : pnlPercentRaw * 100
    : 0;

  const quantity = Number.isFinite(quantityRaw) ? quantityRaw : 0;
  const avg = averagePrice || marketPrice;
  const last = marketPrice || averagePrice;

  const avgSafe = Number.isFinite(avg) ? avg : 0;
  const lastSafe = Number.isFinite(last) ? last : 0;

  return {
    symbol: position.symbol ?? position.ticker ?? position.asset ?? '—',
    quantity,
    averagePrice: avgSafe,
    marketPrice: lastSafe,
    pnl: Number.isFinite(pnlRaw) ? pnlRaw : 0,
    pnlPercent
  };
}

export default function PositionsTable({ positions }) {
  const normalized = (positions ?? []).map(normalizePosition);

  return (
    <div className="positions-card">
      <div className="positions-card__header">
        <div>
          <h3>Open Positions</h3>
          <p>Live snapshot of managed holdings</p>
        </div>
      </div>
      <div className="positions-table__wrapper">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th className="is-right">Quantity</th>
              <th className="is-right">Avg. Price</th>
              <th className="is-right">Last</th>
              <th className="is-right">Unrealized P&L</th>
              <th className="is-right">Return</th>
            </tr>
          </thead>
          <tbody>
            {normalized.map((position) => (
              <tr key={position.symbol}>
                <td>
                  <span className="ticker-pill">{position.symbol}</span>
                </td>
                <td className="is-right">{position.quantity.toLocaleString()}</td>
                <td className="is-right">${position.averagePrice.toFixed(2)}</td>
                <td className="is-right">${position.marketPrice.toFixed(2)}</td>
                <td className={`is-right ${position.pnl >= 0 ? 'is-positive' : 'is-negative'}`}>
                  {position.pnl >= 0 ? '+' : '-'}${Math.abs(position.pnl).toFixed(2)}
                </td>
                <td className={`is-right ${position.pnlPercent >= 0 ? 'is-positive' : 'is-negative'}`}>
                  {position.pnlPercent >= 0 ? '+' : '-'}
                  {Math.abs(position.pnlPercent).toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
