import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle, Play, Pause } from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function AIPortfolioManager() {
  const [portfolio, setPortfolio] = useState(null);
  const [trades, setTrades] = useState([]);
  const [signals, setSignals] = useState([]);
  const [equityCurve, setEquityCurve] = useState([]);
  const [selectedModel, setSelectedModel] = useState('tech');
  const [isLive, setIsLive] = useState(false);
  const [loading, setLoading] = useState(true);

  // Mock data for demonstration
  useEffect(() => {
    loadMockData();
    const interval = setInterval(loadMockData, 5000);
    return () => clearInterval(interval);
  }, [selectedModel]);

  const loadMockData = () => {
    // Mock Portfolio Data
    setPortfolio({
      balance: 98750.50,
      equity: 101250.75,
      dayPnL: 1250.75,
      dayPnLPercent: 1.25,
      totalPnL: 11250.75,
      totalPnLPercent: 12.5,
      buyingPower: 45000.00,
      positions: [
        { symbol: 'AAPL', qty: 50, avgPrice: 178.50, currentPrice: 182.25, pnl: 187.50, pnlPercent: 2.1 },
        { symbol: 'MSFT', qty: 30, avgPrice: 412.30, currentPrice: 418.75, pnl: 193.50, pnlPercent: 1.56 },
        { symbol: 'NVDA', qty: 40, avgPrice: 495.20, currentPrice: 502.80, pnl: 304.00, pnlPercent: 1.53 },
        { symbol: 'GOOGL', qty: 25, avgPrice: 141.60, currentPrice: 143.90, pnl: 57.50, pnlPercent: 1.62 },
        { symbol: 'TSLA', qty: 20, avgPrice: 242.15, currentPrice: 238.90, pnl: -65.00, pnlPercent: -1.34 }
      ]
    });

    // Mock Trades
    setTrades([
      { timestamp: '2025-11-10 09:30:15', symbol: 'AAPL', action: 'BUY', qty: 10, price: 182.25, pnl: 0, model: 'tech' },
      { timestamp: '2025-11-09 09:30:42', symbol: 'NVDA', action: 'SELL', qty: 5, price: 498.60, pnl: 145.20, model: 'tech' },
      { timestamp: '2025-11-09 09:31:05', symbol: 'XOM', action: 'BUY', qty: 30, price: 118.45, pnl: 0, model: 'energy' },
      { timestamp: '2025-11-08 09:30:28', symbol: 'MSFT', action: 'BUY', qty: 15, price: 415.20, pnl: 0, model: 'tech' },
      { timestamp: '2025-11-08 09:32:10', symbol: 'JPM', action: 'SELL', qty: 20, price: 224.80, pnl: -85.40, model: 'energy' }
    ]);

    // Mock Signals
    const techSignals = [
      { symbol: 'AAPL', action: 'BUY', confidence: 0.82, positionSize: 0.15, prediction: 'Bullish momentum' },
      { symbol: 'MSFT', action: 'HOLD', confidence: 0.65, positionSize: 0.10, prediction: 'Sideways consolidation' },
      { symbol: 'NVDA', action: 'BUY', confidence: 0.78, positionSize: 0.20, prediction: 'Strong uptrend' },
      { symbol: 'GOOGL', action: 'HOLD', confidence: 0.58, positionSize: 0.08, prediction: 'Neutral signals' },
      { symbol: 'TSLA', action: 'SELL', confidence: 0.71, positionSize: 0.12, prediction: 'Bearish divergence' }
    ];

    const energySignals = [
      { symbol: 'XOM', action: 'BUY', confidence: 0.75, positionSize: 0.18, prediction: 'Oil price support' },
      { symbol: 'CVX', action: 'HOLD', confidence: 0.62, positionSize: 0.10, prediction: 'Range-bound' },
      { symbol: 'JPM', action: 'SELL', confidence: 0.68, positionSize: 0.15, prediction: 'Profit taking' },
      { symbol: 'BAC', action: 'HOLD', confidence: 0.55, positionSize: 0.08, prediction: 'Waiting for breakout' }
    ];

    setSignals(selectedModel === 'tech' ? techSignals : energySignals);

    // Mock Equity Curve
    setEquityCurve([
      { date: '11/04', value: 95000 },
      { date: '11/05', value: 96200 },
      { date: '11/06', value: 95800 },
      { date: '11/07', value: 97500 },
      { date: '11/08', value: 98200 },
      { date: '11/09', value: 99800 },
      { date: '11/10', value: 101250 }
    ]);

    setLoading(false);
  };

  const COLORS = ['#10b981', '#3b82f6', '#8b5cf6', '#f59e0b', '#ef4444'];

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading AI Portfolio Manager...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
              🤖 AI Portfolio Manager
            </h1>
            <p className="text-slate-400 mt-1">Reinforcement Learning Trading System</p>
          </div>
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsLive(!isLive)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold transition-all ${
                isLive 
                  ? 'bg-red-500 hover:bg-red-600' 
                  : 'bg-emerald-500 hover:bg-emerald-600'
              }`}
            >
              {isLive ? <Pause size={18} /> : <Play size={18} />}
              {isLive ? 'Live Trading' : 'Paper Trading'}
            </button>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-slate-700 border border-slate-600 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-cyan-500"
            >
              <option value="tech">Tech Sector Model</option>
              <option value="energy">Energy/Finance Model</option>
            </select>
          </div>
        </div>
      </div>

      {/* Portfolio Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <DollarSign className="text-cyan-400" size={24} />
            <span className="text-slate-400 text-sm">Total Equity</span>
          </div>
          <div className="text-3xl font-bold">${portfolio.equity.toLocaleString()}</div>
          <div className={`text-sm mt-1 ${portfolio.totalPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {portfolio.totalPnL >= 0 ? '+' : ''}{portfolio.totalPnLPercent}% All Time
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            {portfolio.dayPnL >= 0 ? (
              <TrendingUp className="text-emerald-400" size={24} />
            ) : (
              <TrendingDown className="text-red-400" size={24} />
            )}
            <span className="text-slate-400 text-sm">Day P&L</span>
          </div>
          <div className={`text-3xl font-bold ${portfolio.dayPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {portfolio.dayPnL >= 0 ? '+' : ''}${portfolio.dayPnL.toLocaleString()}
          </div>
          <div className={`text-sm mt-1 ${portfolio.dayPnL >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {portfolio.dayPnL >= 0 ? '+' : ''}{portfolio.dayPnLPercent}%
          </div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <Activity className="text-purple-400" size={24} />
            <span className="text-slate-400 text-sm">Open Positions</span>
          </div>
          <div className="text-3xl font-bold">{portfolio.positions.length}</div>
          <div className="text-sm mt-1 text-slate-400">Active trades</div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="text-amber-400" size={24} />
            <span className="text-slate-400 text-sm">Buying Power</span>
          </div>
          <div className="text-3xl font-bold">${portfolio.buyingPower.toLocaleString()}</div>
          <div className="text-sm mt-1 text-slate-400">Available cash</div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        {/* Equity Curve */}
        <div className="lg:col-span-2 bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <h3 className="text-xl font-semibold mb-4">Portfolio Equity Curve</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={equityCurve}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#94a3b8' }}
              />
              <Line 
                type="monotone" 
                dataKey="value" 
                stroke="#10b981" 
                strokeWidth={3}
                dot={{ fill: '#10b981', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Position Distribution */}
        <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
          <h3 className="text-xl font-semibold mb-4">Position Distribution</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={portfolio.positions}
                dataKey="qty"
                nameKey="symbol"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ symbol, percent }) => `${symbol} ${(percent * 100).toFixed(0)}%`}
              >
                {portfolio.positions.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Signals Panel */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">
          🧠 AI Signals - {selectedModel === 'tech' ? 'Tech Sector' : 'Energy/Finance Sector'}
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {signals.map((signal, idx) => (
            <div 
              key={idx}
              className="bg-slate-900/50 border border-slate-700 rounded-lg p-4 hover:border-cyan-500/50 transition-all"
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-lg font-bold">{signal.symbol}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  signal.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' :
                  signal.action === 'SELL' ? 'bg-red-500/20 text-red-400' :
                  'bg-slate-500/20 text-slate-400'
                }`}>
                  {signal.action}
                </span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Confidence:</span>
                  <span className="font-semibold">{(signal.confidence * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Position Size:</span>
                  <span className="font-semibold">{(signal.positionSize * 100).toFixed(0)}%</span>
                </div>
                <div className="mt-2 pt-2 border-t border-slate-700">
                  <span className="text-xs text-slate-400">{signal.prediction}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Open Positions */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6 mb-6">
        <h3 className="text-xl font-semibold mb-4">Open Positions</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Symbol</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">Qty</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">Avg Price</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">Current</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">P&L</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">P&L %</th>
              </tr>
            </thead>
            <tbody>
              {portfolio.positions.map((pos, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 font-bold">{pos.symbol}</td>
                  <td className="py-3 px-4 text-right">{pos.qty}</td>
                  <td className="py-3 px-4 text-right">${pos.avgPrice.toFixed(2)}</td>
                  <td className="py-3 px-4 text-right">${pos.currentPrice.toFixed(2)}</td>
                  <td className={`py-3 px-4 text-right font-semibold ${pos.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {pos.pnl >= 0 ? '+' : ''}${pos.pnl.toFixed(2)}
                  </td>
                  <td className={`py-3 px-4 text-right font-semibold ${pos.pnlPercent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {pos.pnlPercent >= 0 ? '+' : ''}{pos.pnlPercent.toFixed(2)}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Trade Log */}
      <div className="bg-slate-800/50 backdrop-blur border border-slate-700 rounded-xl p-6">
        <h3 className="text-xl font-semibold mb-4">Recent Trades</h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Timestamp</th>
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Symbol</th>
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Action</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">Qty</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">Price</th>
                <th className="text-right py-3 px-4 text-slate-400 font-semibold">P&L</th>
                <th className="text-left py-3 px-4 text-slate-400 font-semibold">Model</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, idx) => (
                <tr key={idx} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 text-slate-300">{trade.timestamp}</td>
                  <td className="py-3 px-4 font-bold">{trade.symbol}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${
                      trade.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' :
                      'bg-red-500/20 text-red-400'
                    }`}>
                      {trade.action}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right">{trade.qty}</td>
                  <td className="py-3 px-4 text-right">${trade.price.toFixed(2)}</td>
                  <td className={`py-3 px-4 text-right font-semibold ${
                    trade.pnl === 0 ? 'text-slate-400' :
                    trade.pnl > 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {trade.pnl === 0 ? '-' : `${trade.pnl >= 0 ? '+' : ''}$${trade.pnl.toFixed(2)}`}
                  </td>
                  <td className="py-3 px-4 text-slate-400">{trade.model}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 text-center text-slate-500 text-sm">
        <p>⚠️ This is a demo dashboard. Connect to your FastAPI backend for live data.</p>
        <p className="mt-1">Last updated: {new Date().toLocaleString()}</p>
      </div>
    </div>
  );
}