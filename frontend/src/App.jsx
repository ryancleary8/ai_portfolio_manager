import React, { useEffect, useMemo, useState } from 'react';
import {
  Activity,
  ArrowUpRight,
  BarChart3,
  Brain,
  DollarSign,
  LineChart,
  ShieldCheck,
  TrendingUp
} from 'lucide-react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from 'recharts';
import StatCard from './components/StatCard.jsx';
import MetricTile from './components/MetricTile.jsx';
import PositionsTable from './components/PositionsTable.jsx';
import TradesTable from './components/TradesTable.jsx';
import SignalGrid from './components/SignalGrid.jsx';
import TabSwitcher from './components/TabSwitcher.jsx';
import { mockPerformance, mockSignals, mockTrades, mockPositions } from './data/mockData.js';
import './styles/AppLayout.css';

const API_BASE_URL = 'http://localhost:8000/api';

const MODEL_OPTIONS = [
  { value: 'tech', label: 'Tech Sector Agent' },
  { value: 'energy', label: 'Energy & Finance Agent' }
];

const formatCurrency = (value) =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value);

const formatPercent = (value, fractionDigits = 1) => `${value >= 0 ? '+' : ''}${value.toFixed(fractionDigits)}%`;

const PerformanceTooltip = ({ active, payload, label }) => {
  if (!active || !payload || payload.length === 0) {
    return null;
  }

  return (
    <div className="chart-tooltip">
      <span className="chart-tooltip__label">{label}</span>
      <span className="chart-tooltip__value">{formatCurrency(payload[0].value)}</span>
    </div>
  );
};

export default function App() {
  const [selectedModel, setSelectedModel] = useState('tech');
  const [activeTab, setActiveTab] = useState('performance');
  const [performance, setPerformance] = useState({
    metrics: { ...mockPerformance.metrics },
    equityCurve: [...mockPerformance.equityCurve]
  });
  const [signals, setSignals] = useState(() => (mockSignals[selectedModel] ?? []).map((signal) => ({ ...signal })));
  const [trades, setTrades] = useState([...mockTrades]);
  const [positions, setPositions] = useState([...mockPositions]);
  const [loading, setLoading] = useState(false);
  const [isLive, setIsLive] = useState(false);
  const [dataSource, setDataSource] = useState('mock');

  useEffect(() => {
    let isMounted = true;
    let refreshInterval;

    const fetchDashboardData = async () => {
      if (!isMounted) return;
      setLoading(true);

      try {
        const [performanceRes, signalsRes, tradesRes, positionsRes] = await Promise.all([
          fetch(`${API_BASE_URL}/performance`),
          fetch(`${API_BASE_URL}/signals?model=${selectedModel}`),
          fetch(`${API_BASE_URL}/trades?limit=25`),
          fetch(`${API_BASE_URL}/positions`)
        ]);

        if (!performanceRes.ok || !signalsRes.ok || !tradesRes.ok || !positionsRes.ok) {
          throw new Error('Failed to load data');
        }

        const performanceJson = await performanceRes.json();
        const signalsJson = await signalsRes.json();
        const tradesJson = await tradesRes.json();
        const positionsJson = await positionsRes.json();

        if (!isMounted) return;

        const metrics = {
          ...mockPerformance.metrics,
          ...(performanceJson.metrics ?? {})
        };
        if (performanceJson.last_updated || performanceJson.lastUpdated) {
          metrics.lastUpdated = performanceJson.last_updated ?? performanceJson.lastUpdated;
        }
        const equityCurve =
          performanceJson.equity_curve || performanceJson.equityCurve || mockPerformance.equityCurve;

        setPerformance({ metrics, equityCurve });
        const fallbackSignals = (mockSignals[selectedModel] ?? []).map((signal) => ({ ...signal }));
        setSignals(signalsJson.signals?.length ? signalsJson.signals : fallbackSignals);
        setTrades(tradesJson.trades?.length ? tradesJson.trades : [...mockTrades]);
        setPositions(positionsJson.positions?.length ? positionsJson.positions : [...mockPositions]);
        setDataSource('live');
      } catch (error) {
        if (!isMounted) return;
        setPerformance({
          metrics: { ...mockPerformance.metrics },
          equityCurve: [...mockPerformance.equityCurve]
        });
        const fallbackSignals = (mockSignals[selectedModel] ?? []).map((signal) => ({ ...signal }));
        setSignals(fallbackSignals);
        setTrades([...mockTrades]);
        setPositions([...mockPositions]);
        setDataSource('mock');
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    fetchDashboardData();

    const intervalMs = dataSource === 'live' ? 1000 * 60 * 5 : 1000 * 60 * 15;
    refreshInterval = setInterval(fetchDashboardData, intervalMs);

    return () => {
      isMounted = false;
      clearInterval(refreshInterval);
    };
  }, [selectedModel, dataSource]);

  useEffect(() => {
    const fallbackSignals = mockSignals[selectedModel] ?? [];
    setSignals(fallbackSignals.map((signal) => ({ ...signal })));
  }, [selectedModel]);

  const topStats = useMemo(
    () => [
      {
        title: 'Portfolio Value',
        value: formatCurrency(performance.metrics.portfolioValue || mockPerformance.metrics.portfolioValue),
        delta: performance.metrics.portfolioChange ?? mockPerformance.metrics.portfolioChange,
        deltaLabel: 'vs. 90-day baseline',
        icon: <TrendingUp size={20} />
      },
      {
        title: 'Daily P&L',
        value: formatCurrency(performance.metrics.dailyPnl ?? mockPerformance.metrics.dailyPnl),
        delta: performance.metrics.dailyPnlPercent ?? mockPerformance.metrics.dailyPnlPercent,
        deltaLabel: 'session change',
        icon: <DollarSign size={20} />
      },
      {
        title: 'Open Positions',
        value: performance.metrics.openPositions ?? mockPerformance.metrics.openPositions,
        delta: performance.metrics.openPositionsChange ?? mockPerformance.metrics.openPositionsChange,
        deltaLabel: 'day-over-day',
        icon: <Activity size={20} />
      },
      {
        title: 'Win Rate',
        value: `${(performance.metrics.winRate ?? mockPerformance.metrics.winRate).toFixed(1)}%`,
        delta: performance.metrics.winRateChange ?? mockPerformance.metrics.winRateChange,
        deltaLabel: '30-day rolling',
        icon: <ShieldCheck size={20} />
      }
    ],
    [performance]
  );

  const secondaryStats = useMemo(
    () => [
      {
        label: 'Rolling Sharpe (60d)',
        value: performance.metrics.rollingSharpe?.toFixed(2) ?? mockPerformance.metrics.rollingSharpe.toFixed(2),
        trend: performance.metrics.sharpeRatioChange ?? mockPerformance.metrics.sharpeRatioChange,
        sublabel: 'Risk-adjusted performance'
      },
      {
        label: 'Max Drawdown',
        value: formatPercent(performance.metrics.maxDrawdown ?? mockPerformance.metrics.maxDrawdown),
        trend: performance.metrics.maxDrawdownChange ?? mockPerformance.metrics.maxDrawdownChange,
        sublabel: 'Since inception'
      },
      {
        label: 'Buying Power',
        value: formatCurrency(performance.metrics.buyingPower ?? mockPerformance.metrics.buyingPower),
        trend: null,
        sublabel: 'Available for deployment'
      },
      {
        label: 'AI Confidence',
        value: `${performance.metrics.aiConfidence ?? mockPerformance.metrics.aiConfidence}%`,
        trend: null,
        sublabel: 'Signal agreement across models'
      }
    ],
    [performance]
  );

  const activeSignals = useMemo(() => signals ?? [], [signals]);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <div className="dashboard__title-block">
          <span className="dashboard__eyebrow">Reinforcement Learning Trading System</span>
          <h1>AI Portfolio Manager</h1>
          <p className="dashboard__subtitle">
            Autonomous trading infrastructure orchestrating multi-agent strategies with continuous monitoring.
          </p>
        </div>
        <div className="dashboard__controls">
          <div className={`status-badge ${dataSource === 'live' ? 'is-live' : 'is-mock'}`}>
            <span className="status-dot" />
            {dataSource === 'live' ? 'Live data' : 'Sample data'}
          </div>
          <button type="button" className={`mode-toggle ${isLive ? 'is-active' : ''}`} onClick={() => setIsLive((v) => !v)}>
            <LineChart size={16} />
            {isLive ? 'Live Trading' : 'Paper Trading'}
          </button>
          <div className="model-select">
            <label htmlFor="model">Active Model</label>
            <select id="model" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)}>
              {MODEL_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <section className="stats-grid">
        {topStats.map((stat) => (
          <StatCard key={stat.title} {...stat} />
        ))}
      </section>

      <section className="overview">
        <div className="overview__left">
          <div className="overview__header">
            <div>
              <h2>Portfolio Equity Curve</h2>
              <p>60-day performance trajectory</p>
            </div>
            <TabSwitcher activeTab={activeTab} onChange={setActiveTab} />
          </div>

          <div className="overview__body">
            {activeTab === 'performance' && (
              <div className="chart-card">
                {loading ? (
                  <div className="loading-state">
                    <div className="spinner" />
                    Loading performance data
                  </div>
                ) : (
                  <ResponsiveContainer width="100%" height={320}>
                    <AreaChart data={performance.equityCurve ?? mockPerformance.equityCurve} margin={{ top: 20, right: 12, left: 12, bottom: 0 }}>
                      <defs>
                        <linearGradient id="equityGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8} />
                          <stop offset="95%" stopColor="#38bdf8" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid stroke="rgba(148, 163, 184, 0.08)" vertical={false} />
                      <XAxis dataKey="date" tick={{ fill: 'rgba(148, 163, 184, 0.8)', fontSize: 12 }} axisLine={false} tickLine={false} />
                      <YAxis tickFormatter={(value) => `$${value / 1000}k`} tick={{ fill: 'rgba(148, 163, 184, 0.8)', fontSize: 12 }} axisLine={false} tickLine={false} width={60} />
                      <Tooltip content={<PerformanceTooltip />} cursor={{ stroke: 'rgba(148, 163, 184, 0.35)', strokeDasharray: '4 4' }} />
                      <Area type="monotone" dataKey="value" stroke="#38bdf8" strokeWidth={3} fill="url(#equityGradient)" dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                )}
              </div>
            )}

            {activeTab === 'signals' && <SignalGrid signals={activeSignals} modelName={selectedModel} />}

            {activeTab === 'trades' && <TradesTable trades={trades} />}
          </div>
        </div>

        <aside className="overview__right">
          <div className="metrics-stack">
            <div className="metrics-stack__header">
              <h3>Risk & Efficiency</h3>
              <p>Key ratios driving deployment cadence</p>
            </div>
            <div className="metrics-stack__grid">
              {secondaryStats.map((metric) => (
                <MetricTile key={metric.label} {...metric} />
              ))}
            </div>
          </div>

          <div className="intel-card">
            <div className="intel-card__header">
              <Brain size={20} />
              <h3>Strategy Insights</h3>
            </div>
            <ul>
              <li>
                <ArrowUpRight size={16} />
                Momentum regime detected across 73% of tracked assets.
              </li>
              <li>
                <BarChart3 size={16} />
                Risk desk approved increased allocation for {MODEL_OPTIONS.find((option) => option.value === selectedModel)?.label}.
              </li>
              <li>
                <TrendingUp size={16} />
                Reinforcement agent confidence remains within the 90th percentile band.
              </li>
            </ul>
          </div>
        </aside>
      </section>

      <section className="positions-section">
        <PositionsTable positions={positions} />
      </section>

      {activeTab !== 'trades' && (
        <section className="trades-section">
          <TradesTable trades={trades} />
        </section>
      )}

      <footer className="dashboard__footer">
        <span>
          Last refreshed{' '}
          {new Date(
            performance.metrics.lastUpdated ?? mockPerformance.metrics.lastUpdated
          ).toLocaleString()}
        </span>
        <span className="footer-divider" />
        <span>Connect your FastAPI backend for real-time execution visibility.</span>
      </footer>
    </div>
  );
}
