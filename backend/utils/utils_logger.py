"""
Trade Logger and Performance Tracker
Logs all trades and tracks portfolio performance metrics
"""

import pandas as pd
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TradeLogger:
    """Logs all trading activity"""
    
    def __init__(self, log_file: str = "data/trades.csv"):
        self.log_file = log_file
        self.trades = []
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Load existing trades
        self._load_trades()
    
    def _load_trades(self):
        """Load trades from CSV file"""
        if os.path.exists(self.log_file):
            try:
                df = pd.read_csv(self.log_file)
                self.trades = df.to_dict('records')
                logger.info(f"✅ Loaded {len(self.trades)} trades from {self.log_file}")
            except Exception as e:
                logger.error(f"❌ Error loading trades: {e}")
                self.trades = []
        else:
            logger.info(f"📝 Creating new trade log: {self.log_file}")
    
    def log_trade(self, trade: Dict):
        """
        Log a new trade
        
        Args:
            trade: Dictionary with trade details
                {timestamp, symbol, action, qty, price, pnl, order_id, ...}
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in trade:
                trade['timestamp'] = datetime.now().isoformat()
            
            # Add to in-memory list
            self.trades.append(trade)
            
            # Append to CSV file
            df = pd.DataFrame([trade])
            
            # Write header if file doesn't exist
            write_header = not os.path.exists(self.log_file)
            
            df.to_csv(
                self.log_file,
                mode='a',
                header=write_header,
                index=False
            )
            
            logger.info(f"✅ Logged trade: {trade['action']} {trade['qty']} {trade['symbol']}")
            
        except Exception as e:
            logger.error(f"❌ Error logging trade: {e}")
    
    def get_recent_trades(self, limit: int = 50) -> List[Dict]:
        """Get most recent trades"""
        return self.trades[-limit:]
    
    def get_today_trades(self) -> List[Dict]:
        """Get trades from today"""
        today = datetime.now().date()
        
        today_trades = [
            t for t in self.trades
            if datetime.fromisoformat(t['timestamp']).date() == today
        ]
        
        return today_trades
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """Get all trades for a specific symbol"""
        return [t for t in self.trades if t['symbol'] == symbol]
    
    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """Get trades within date range"""
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        return [
            t for t in self.trades
            if start <= datetime.fromisoformat(t['timestamp']) <= end
        ]
    
    def get_trade_summary(self) -> Dict:
        """Get summary statistics"""
        if not self.trades:
            return {
                "total_trades": 0,
                "buy_trades": 0,
                "sell_trades": 0,
                "total_pnl": 0,
                "win_rate": 0,
                "avg_pnl": 0
            }
        
        df = pd.DataFrame(self.trades)
        
        # Calculate metrics
        total_trades = len(df)
        buy_trades = len(df[df['action'] == 'BUY'])
        sell_trades = len(df[df['action'] == 'SELL'])
        
        # PnL metrics (only for closed positions)
        pnl_trades = df[df.get('pnl', 0) != 0]
        
        if len(pnl_trades) > 0:
            total_pnl = pnl_trades['pnl'].sum()
            winning_trades = len(pnl_trades[pnl_trades['pnl'] > 0])
            win_rate = (winning_trades / len(pnl_trades)) * 100
            avg_pnl = pnl_trades['pnl'].mean()
        else:
            total_pnl = 0
            win_rate = 0
            avg_pnl = 0
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "total_pnl": float(total_pnl),
            "win_rate": float(win_rate),
            "avg_pnl": float(avg_pnl)
        }


class PerformanceTracker:
    """Tracks portfolio performance over time"""
    
    def __init__(self, perf_file: str = "data/performance.json"):
        self.perf_file = perf_file
        self.equity_history = []
        self.daily_returns = []
        
        # Create data directory
        os.makedirs("data", exist_ok=True)
        
        # Load existing performance data
        self._load_performance()
    
    def _load_performance(self):
        """Load performance history from file"""
        if os.path.exists(self.perf_file):
            try:
                with open(self.perf_file, 'r') as f:
                    data = json.load(f)
                    self.equity_history = data.get('equity_history', [])
                    self.daily_returns = data.get('daily_returns', [])
                
                logger.info(f"✅ Loaded {len(self.equity_history)} data points")
            
            except Exception as e:
                logger.error(f"❌ Error loading performance: {e}")
                self.equity_history = []
                self.daily_returns = []
    
    def _save_performance(self):
        """Save performance history to file"""
        try:
            data = {
                'equity_history': self.equity_history,
                'daily_returns': self.daily_returns,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.perf_file, 'w') as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            logger.error(f"❌ Error saving performance: {e}")
    
    def update(self, portfolio_value: float, signals: List[Dict] = None):
        """
        Update performance with latest portfolio value
        
        Args:
            portfolio_value: Current total portfolio value
            signals: Latest trading signals (optional)
        """
        try:
            timestamp = datetime.now().isoformat()
            
            # Add to equity history
            self.equity_history.append({
                'timestamp': timestamp,
                'value': portfolio_value
            })
            
            # Calculate daily return
            if len(self.equity_history) > 1:
                prev_value = self.equity_history[-2]['value']
                daily_return = (portfolio_value - prev_value) / prev_value
                
                self.daily_returns.append({
                    'timestamp': timestamp,
                    'return': daily_return
                })
            
            # Save to file
            self._save_performance()
            
            logger.info(f"✅ Updated performance: ${portfolio_value:,.2f}")
            
        except Exception as e:
            logger.error(f"❌ Error updating performance: {e}")
    
    def get_equity_curve(self, days: int = 30) -> List[Dict]:
        """Get equity curve for last N days"""
        if not self.equity_history:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_equity = [
            e for e in self.equity_history
            if datetime.fromisoformat(e['timestamp']) >= cutoff_date
        ]
        
        return recent_equity
    
    def get_metrics(self) -> Dict:
        """Calculate performance metrics"""
        if len(self.equity_history) < 2:
            return {
                "total_return": 0,
                "sharpe_ratio": 0,
                "max_drawdown": 0,
                "win_rate": 0,
                "volatility": 0
            }
        
        # Convert to pandas for calculations
        df = pd.DataFrame(self.equity_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Total return
        initial_value = df['value'].iloc[0]
        current_value = df['value'].iloc[-1]
        total_return = ((current_value - initial_value) / initial_value) * 100
        
        # Daily returns
        df['daily_return'] = df['value'].pct_change()
        returns = df['daily_return'].dropna()
        
        # Sharpe ratio (annualized)
        if len(returns) > 0 and returns.std() != 0:
            sharpe_ratio = (returns.mean() / returns.std()) * (252 ** 0.5)
        else:
            sharpe_ratio = 0
        
        # Max drawdown
        running_max = df['value'].expanding().max()
        drawdown = (df['value'] - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Volatility (annualized)
        volatility = returns.std() * (252 ** 0.5) * 100
        
        return {
            "total_return": float(total_return),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "volatility": float(volatility),
            "current_value": float(current_value)
        }
    
    def get_daily_pnl(self) -> float:
        """Get today's P&L"""
        if len(self.equity_history) < 2:
            return 0.0
        
        today = datetime.now().date()
        
        # Find today's and yesterday's values
        today_value = None
        yesterday_value = None
        
        for i in range(len(self.equity_history) - 1, -1, -1):
            entry = self.equity_history[i]
            entry_date = datetime.fromisoformat(entry['timestamp']).date()
            
            if entry_date == today and today_value is None:
                today_value = entry['value']
            elif entry_date < today and yesterday_value is None:
                yesterday_value = entry['value']
                break
        
        if today_value and yesterday_value:
            return today_value - yesterday_value
        
        return 0.0
    
    def generate_report(self) -> Dict:
        """Generate comprehensive performance report"""
        metrics = self.get_metrics()
        equity_curve = self.get_equity_curve(30)
        daily_pnl = self.get_daily_pnl()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "daily_pnl": daily_pnl,
            "equity_curve": equity_curve,
            "data_points": len(self.equity_history)
        }