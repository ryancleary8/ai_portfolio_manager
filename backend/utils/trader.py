"""
Alpaca Trading Integration
Handles order execution, position management, and portfolio tracking
"""

import os
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional
import logging

try:
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
    from alpaca.trading.enums import OrderSide, TimeInForce
    ALPACA_AVAILABLE = True
except ImportError:
    ALPACA_AVAILABLE = False
    logging.warning("⚠️ alpaca-py not installed. Running in simulation mode.")

logger = logging.getLogger(__name__)


class AlpacaTrader:
    """Alpaca API wrapper for automated trading"""
    
    def __init__(self):
        self.api_key = os.getenv("APCA_API_KEY_ID")
        self.api_secret = os.getenv("APCA_API_SECRET_KEY")
        self.paper = os.getenv("APCA_PAPER", "true").lower() == "true"
        self.client = None
        self.connected = False
        
    def connect(self):
        """Connect to Alpaca API"""
        try:
            if not ALPACA_AVAILABLE:
                logger.warning("⚠️ Alpaca not available - using simulation mode")
                self.connected = False
                return False
            
            if not self.api_key or not self.api_secret:
                logger.warning("⚠️ Alpaca credentials not found - using simulation mode")
                self.connected = False
                return False
            
            self.client = TradingClient(
                api_key=self.api_key,
                secret_key=self.api_secret,
                paper=self.paper
            )
            
            # Test connection
            account = self.client.get_account()
            self.connected = True
            
            logger.info(f"✅ Connected to Alpaca ({'Paper' if self.paper else 'Live'} Trading)")
            logger.info(f"💰 Account Equity: ${float(account.equity):,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to Alpaca: {e}")
            self.connected = False
            return False
    
    def get_portfolio_summary(self) -> Dict:
        """Get current portfolio overview"""
        if not self.connected or not self.client:
            return self._get_mock_portfolio()
        
        try:
            account = self.client.get_account()
            positions = self.client.get_all_positions()
            
            # Calculate day P&L
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            day_pnl = equity - last_equity
            day_pnl_pct = (day_pnl / last_equity * 100) if last_equity > 0 else 0
            
            # Calculate total P&L
            initial_cash = 100000.0  # Starting capital
            total_pnl = equity - initial_cash
            total_pnl_pct = (total_pnl / initial_cash * 100)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "balance": float(account.cash),
                "equity": equity,
                "buying_power": float(account.buying_power),
                "day_pnl": day_pnl,
                "day_pnl_percent": day_pnl_pct,
                "total_pnl": total_pnl,
                "total_pnl_percent": total_pnl_pct,
                "position_count": len(positions),
                "positions": [self._format_position(p) for p in positions]
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting portfolio: {e}")
            return self._get_mock_portfolio()
    
    def get_positions(self) -> List[Dict]:
        """Get all open positions"""
        if not self.connected or not self.client:
            return []
        
        try:
            positions = self.client.get_all_positions()
            return [self._format_position(p) for p in positions]
        except Exception as e:
            logger.error(f"❌ Error getting positions: {e}")
            return []
    
    def _format_position(self, position) -> Dict:
        """Format position data"""
        current_price = float(position.current_price)
        avg_price = float(position.avg_entry_price)
        qty = float(position.qty)
        
        pnl = (current_price - avg_price) * qty
        pnl_pct = ((current_price - avg_price) / avg_price * 100) if avg_price > 0 else 0
        
        return {
            "symbol": position.symbol,
            "qty": qty,
            "avg_price": avg_price,
            "current_price": current_price,
            "market_value": float(position.market_value),
            "pnl": pnl,
            "pnl_percent": pnl_pct,
            "side": position.side
        }
    
    def execute_trade(self, ticker: str, action: str, position_size: float) -> Optional[Dict]:
        """
        Execute trade based on RL model signal
        
        Args:
            ticker: Stock symbol
            action: "BUY" or "SELL"
            position_size: Fraction of portfolio (0-1)
        """
        if not self.connected or not self.client:
            logger.info(f"🔧 Simulation: {action} {ticker} (size: {position_size:.2%})")
            return self._simulate_trade(ticker, action, position_size)
        
        try:
            account = self.client.get_account()
            equity = float(account.equity)
            
            # Calculate quantity based on position size
            if action == "BUY":
                # Get current price
                try:
                    bars = self.client.get_latest_bar(ticker)
                    current_price = float(bars.c)
                except:
                    logger.error(f"❌ Could not get price for {ticker}")
                    return None
                
                # Calculate shares to buy
                dollar_amount = equity * position_size
                qty = int(dollar_amount / current_price)
                
                if qty < 1:
                    logger.warning(f"⚠️ Quantity too small for {ticker}")
                    return None
                
                # Place buy order
                order_data = MarketOrderRequest(
                    symbol=ticker,
                    qty=qty,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.client.submit_order(order_data)
                
                logger.info(f"✅ BUY order placed: {qty} shares of {ticker}")
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": ticker,
                    "action": "BUY",
                    "qty": qty,
                    "price": current_price,
                    "order_id": str(order.id),
                    "status": order.status
                }
            
            elif action == "SELL":
                # Get current position
                try:
                    position = self.client.get_position(ticker)
                    current_qty = float(position.qty)
                    current_price = float(position.current_price)
                except:
                    logger.warning(f"⚠️ No position found for {ticker}")
                    return None
                
                # Calculate shares to sell
                qty = int(current_qty * position_size)
                
                if qty < 1:
                    logger.warning(f"⚠️ Quantity too small for {ticker}")
                    return None
                
                # Place sell order
                order_data = MarketOrderRequest(
                    symbol=ticker,
                    qty=qty,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY
                )
                
                order = self.client.submit_order(order_data)
                
                logger.info(f"✅ SELL order placed: {qty} shares of {ticker}")
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "symbol": ticker,
                    "action": "SELL",
                    "qty": qty,
                    "price": current_price,
                    "order_id": str(order.id),
                    "status": order.status
                }
        
        except Exception as e:
            logger.error(f"❌ Error executing trade for {ticker}: {e}")
            return None
    
    def execute_manual_trade(self, ticker: str, action: str, quantity: int) -> Dict:
        """Execute manual trade with specific quantity"""
        if not self.connected or not self.client:
            return self._simulate_trade(ticker, action, 0.1)
        
        try:
            order_data = MarketOrderRequest(
                symbol=ticker,
                qty=quantity,
                side=OrderSide.BUY if action == "BUY" else OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.client.submit_order(order_data)
            
            return {
                "timestamp": datetime.now().isoformat(),
                "symbol": ticker,
                "action": action,
                "qty": quantity,
                "order_id": str(order.id),
                "status": order.status,
                "manual": True
            }
        
        except Exception as e:
            logger.error(f"❌ Error executing manual trade: {e}")
            raise
    
    def get_portfolio_value(self) -> float:
        """Get current portfolio value"""
        if not self.connected or not self.client:
            return 100000.0  # Mock value
        
        try:
            account = self.client.get_account()
            return float(account.equity)
        except Exception as e:
            logger.error(f"❌ Error getting portfolio value: {e}")
            return 0.0
    
    def _get_mock_portfolio(self) -> Dict:
        """Return mock portfolio for testing"""
        return {
            "timestamp": datetime.now().isoformat(),
            "balance": 50000.0,
            "equity": 105000.0,
            "buying_power": 45000.0,
            "day_pnl": 1200.0,
            "day_pnl_percent": 1.15,
            "total_pnl": 5000.0,
            "total_pnl_percent": 5.0,
            "position_count": 5,
            "positions": []
        }
    
    def _simulate_trade(self, ticker: str, action: str, position_size: float) -> Dict:
        """Simulate trade for testing"""
        return {
            "timestamp": datetime.now().isoformat(),
            "symbol": ticker,
            "action": action,
            "qty": int(100 * position_size),
            "price": 100.0,
            "simulated": True
        }


def prepare_observation(data: Dict, scaler=None) -> np.ndarray:
    """
    Prepare observation vector for RL model
    
    Features expected by model:
    - Close, Open, High, Low, Volume
    - SMA_20, SMA_50, EMA_12, EMA_26
    - RSI, MACD, MACD_signal, MACD_hist
    - BB_upper, BB_middle, BB_lower
    - Returns
    """
    try:
        # Extract features in correct order
        features = [
            data.get('close', 0),
            data.get('open', 0),
            data.get('high', 0),
            data.get('low', 0),
            data.get('volume', 0),
            data.get('sma_20', 0),
            data.get('sma_50', 0),
            data.get('ema_12', 0),
            data.get('ema_26', 0),
            data.get('rsi', 50),
            data.get('macd', 0),
            data.get('macd_signal', 0),
            data.get('macd_hist', 0),
            data.get('bb_upper', 0),
            data.get('bb_middle', 0),
            data.get('bb_lower', 0),
            data.get('returns', 0)
        ]
        
        obs = np.array(features, dtype=np.float32).reshape(1, -1)
        
        # Normalize if scaler available
        if scaler is not None:
            obs = scaler.transform(obs)
        
        return obs
        
    except Exception as e:
        logger.error(f"❌ Error preparing observation: {e}")
        return np.zeros((1, 17), dtype=np.float32)