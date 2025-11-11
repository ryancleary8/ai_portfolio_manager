export const mockPerformance = {
  metrics: {
    portfolioValue: 247832.5,
    portfolioChange: 12.3,
    dailyPnl: 3421.0,
    dailyPnlPercent: 1.45,
    openPositions: 10,
    openPositionsChange: 1.2,
    winRate: 67.8,
    winRateChange: -0.6,
    sharpeRatio: 1.84,
    sharpeRatioChange: 0.12,
    maxDrawdown: -5.2,
    maxDrawdownChange: 0.4,
    buyingPower: 54821.0,
    rollingSharpe: 1.84,
    aiConfidence: 78,
    lastUpdated: '2025-11-10T15:45:00Z'
  },
  equityCurve: [
    { date: 'Sep', value: 185000 },
    { date: 'Oct', value: 198200 },
    { date: 'Nov', value: 205600 },
    { date: 'Dec', value: 212450 },
    { date: 'Jan', value: 221320 },
    { date: 'Feb', value: 229880 },
    { date: 'Mar', value: 236540 },
    { date: 'Apr', value: 239400 },
    { date: 'May', value: 243200 },
    { date: 'Jun', value: 247832 }
  ]
};

export const mockSignals = {
  tech: [
    {
      symbol: 'AAPL',
      action: 'BUY',
      confidence: 0.82,
      thesis: 'Earnings momentum following services beat',
      positionSize: 0.14
    },
    {
      symbol: 'MSFT',
      action: 'HOLD',
      confidence: 0.64,
      thesis: 'Azure growth stabilizing, await breakout',
      positionSize: 0.1
    },
    {
      symbol: 'NVDA',
      action: 'BUY',
      confidence: 0.79,
      thesis: 'Data center demand remains elevated',
      positionSize: 0.18
    },
    {
      symbol: 'GOOGL',
      action: 'BUY',
      confidence: 0.7,
      thesis: 'Search volumes accelerating week-over-week',
      positionSize: 0.12
    },
    {
      symbol: 'TSLA',
      action: 'SELL',
      confidence: 0.68,
      thesis: 'Delivery softness and margin pressure',
      positionSize: 0.08
    }
  ],
  energy: [
    {
      symbol: 'XOM',
      action: 'BUY',
      confidence: 0.77,
      thesis: 'Crude spreads tightening into winter demand',
      positionSize: 0.16
    },
    {
      symbol: 'CVX',
      action: 'HOLD',
      confidence: 0.58,
      thesis: 'Awaiting confirmation of trend reversal',
      positionSize: 0.09
    },
    {
      symbol: 'JPM',
      action: 'SELL',
      confidence: 0.66,
      thesis: 'Net interest margin compression risk',
      positionSize: 0.11
    },
    {
      symbol: 'BAC',
      action: 'HOLD',
      confidence: 0.55,
      thesis: 'Limited catalysts in current rate regime',
      positionSize: 0.08
    }
  ]
};

export const mockTrades = [
  {
    id: 'TRD-10567',
    timestamp: '2025-11-10T14:35:00Z',
    symbol: 'AAPL',
    side: 'BUY',
    quantity: 25,
    price: 182.34,
    pnl: 0,
    model: 'Tech Sector Agent'
  },
  {
    id: 'TRD-10566',
    timestamp: '2025-11-10T13:02:00Z',
    symbol: 'NVDA',
    side: 'SELL',
    quantity: 10,
    price: 488.65,
    pnl: 325.4,
    model: 'Tech Sector Agent'
  },
  {
    id: 'TRD-10565',
    timestamp: '2025-11-09T20:15:00Z',
    symbol: 'XOM',
    side: 'BUY',
    quantity: 40,
    price: 119.24,
    pnl: 0,
    model: 'Energy & Finance Agent'
  },
  {
    id: 'TRD-10564',
    timestamp: '2025-11-09T16:48:00Z',
    symbol: 'MSFT',
    side: 'BUY',
    quantity: 15,
    price: 414.91,
    pnl: 0,
    model: 'Tech Sector Agent'
  },
  {
    id: 'TRD-10563',
    timestamp: '2025-11-09T15:12:00Z',
    symbol: 'JPM',
    side: 'SELL',
    quantity: 20,
    price: 224.35,
    pnl: -112.8,
    model: 'Energy & Finance Agent'
  }
];

export const mockPositions = [
  {
    symbol: 'AAPL',
    quantity: 80,
    averagePrice: 176.25,
    marketPrice: 182.34,
    unrealizedPnl: 487.2,
    unrealizedPnlPercent: 3.12
  },
  {
    symbol: 'MSFT',
    quantity: 45,
    averagePrice: 406.1,
    marketPrice: 414.91,
    unrealizedPnl: 396.45,
    unrealizedPnlPercent: 2.02
  },
  {
    symbol: 'NVDA',
    quantity: 35,
    averagePrice: 472.8,
    marketPrice: 488.65,
    unrealizedPnl: 554.25,
    unrealizedPnlPercent: 3.34
  },
  {
    symbol: 'GOOGL',
    quantity: 30,
    averagePrice: 138.45,
    marketPrice: 141.12,
    unrealizedPnl: 80.1,
    unrealizedPnlPercent: 1.93
  },
  {
    symbol: 'TSLA',
    quantity: 20,
    averagePrice: 242.8,
    marketPrice: 236.44,
    unrealizedPnl: -127.2,
    unrealizedPnlPercent: -2.62
  }
];
