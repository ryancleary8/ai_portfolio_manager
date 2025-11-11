"""
Technical Indicators Calculator
Computes SMA, EMA, RSI, MACD, Bollinger Bands, and other indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


def calculate_indicators(df: pd.DataFrame) -> Dict:
    """
    Calculate all technical indicators needed for RL model
    
    Args:
        df: DataFrame with OHLCV data
    
    Returns:
        Dictionary with latest indicator values
    """
    try:
        # Make a copy to avoid modifying original
        data = df.copy()
        
        # Ensure we have required columns
        required_cols = ['close', 'open', 'high', 'low', 'volume']
        for col in required_cols:
            if col not in data.columns:
                logger.error(f"❌ Missing required column: {col}")
                return {}
        
        # Calculate all indicators
        data = add_sma(data, [20, 50])
        data = add_ema(data, [12, 26])
        data = add_rsi(data, 14)
        data = add_macd(data)
        data = add_bollinger_bands(data, 20, 2)
        data = add_returns(data)
        
        # Get latest row
        latest = data.iloc[-1]
        
        # Build observation dictionary
        observation = {
            'close': float(latest['close']),
            'open': float(latest['open']),
            'high': float(latest['high']),
            'low': float(latest['low']),
            'volume': float(latest['volume']),
            'sma_20': float(latest.get('sma_20', latest['close'])),
            'sma_50': float(latest.get('sma_50', latest['close'])),
            'ema_12': float(latest.get('ema_12', latest['close'])),
            'ema_26': float(latest.get('ema_26', latest['close'])),
            'rsi': float(latest.get('rsi', 50)),
            'macd': float(latest.get('macd', 0)),
            'macd_signal': float(latest.get('macd_signal', 0)),
            'macd_hist': float(latest.get('macd_hist', 0)),
            'bb_upper': float(latest.get('bb_upper', latest['close'])),
            'bb_middle': float(latest.get('bb_middle', latest['close'])),
            'bb_lower': float(latest.get('bb_lower', latest['close'])),
            'returns': float(latest.get('returns', 0))
        }
        
        return observation
        
    except Exception as e:
        logger.error(f"❌ Error calculating indicators: {e}")
        return {}


def add_sma(df: pd.DataFrame, periods: list) -> pd.DataFrame:
    """Add Simple Moving Average"""
    for period in periods:
        df[f'sma_{period}'] = df['close'].rolling(window=period).mean()
    return df


def add_ema(df: pd.DataFrame, periods: list) -> pd.DataFrame:
    """Add Exponential Moving Average"""
    for period in periods:
        df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    return df


def add_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add Relative Strength Index
    
    RSI = 100 - (100 / (1 + RS))
    RS = Average Gain / Average Loss
    """
    delta = df['close'].diff()
    
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Fill NaN with neutral value
    df['rsi'].fillna(50, inplace=True)
    
    return df


def add_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Add Moving Average Convergence Divergence
    
    MACD = EMA(fast) - EMA(slow)
    Signal = EMA(MACD, signal_period)
    Histogram = MACD - Signal
    """
    ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['close'].ewm(span=slow, adjust=False).mean()
    
    df['macd'] = ema_fast - ema_slow
    df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
    df['macd_hist'] = df['macd'] - df['macd_signal']
    
    # Fill NaN with 0
    df['macd'].fillna(0, inplace=True)
    df['macd_signal'].fillna(0, inplace=True)
    df['macd_hist'].fillna(0, inplace=True)
    
    return df


def add_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2) -> pd.DataFrame:
    """
    Add Bollinger Bands
    
    Upper Band = SMA + (std_dev × σ)
    Middle Band = SMA
    Lower Band = SMA - (std_dev × σ)
    """
    df['bb_middle'] = df['close'].rolling(window=period).mean()
    bb_std = df['close'].rolling(window=period).std()
    
    df['bb_upper'] = df['bb_middle'] + (std_dev * bb_std)
    df['bb_lower'] = df['bb_middle'] - (std_dev * bb_std)
    
    # Fill NaN with current price
    df['bb_middle'].fillna(df['close'], inplace=True)
    df['bb_upper'].fillna(df['close'], inplace=True)
    df['bb_lower'].fillna(df['close'], inplace=True)
    
    return df


def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Add daily returns"""
    df['returns'] = df['close'].pct_change()
    df['returns'].fillna(0, inplace=True)
    return df


def add_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add Average True Range (volatility indicator)
    
    TR = max[(high - low), abs(high - prev_close), abs(low - prev_close)]
    ATR = EMA(TR, period)
    """
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = true_range.ewm(span=period, adjust=False).mean()
    
    df['atr'].fillna(0, inplace=True)
    
    return df


def add_stochastic_oscillator(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Add Stochastic Oscillator
    
    %K = (Close - Low(period)) / (High(period) - Low(period)) × 100
    %D = SMA(%K, 3)
    """
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()
    
    df['stoch_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
    
    df['stoch_k'].fillna(50, inplace=True)
    df['stoch_d'].fillna(50, inplace=True)
    
    return df


def add_obv(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add On-Balance Volume
    
    OBV increases/decreases by volume based on price direction
    """
    obv = [0]
    
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['close'].iloc[i-1]:
            obv.append(obv[-1] + df['volume'].iloc[i])
        elif df['close'].iloc[i] < df['close'].iloc[i-1]:
            obv.append(obv[-1] - df['volume'].iloc[i])
        else:
            obv.append(obv[-1])
    
    df['obv'] = obv
    
    return df


def add_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add Volume Weighted Average Price (intraday only)
    
    VWAP = Σ(Price × Volume) / Σ(Volume)
    """
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    df['vwap'] = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    df['vwap'].fillna(df['close'], inplace=True)
    
    return df


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
    """
    Calculate Sharpe Ratio
    
    Sharpe = (Mean Return - Risk Free Rate) / Std Dev of Returns
    """
    if len(returns) < 2:
        return 0.0
    
    excess_returns = returns - (risk_free_rate / 252)  # Daily risk-free rate
    
    if excess_returns.std() == 0:
        return 0.0
    
    sharpe = excess_returns.mean() / excess_returns.std()
    
    # Annualize
    sharpe_annual = sharpe * np.sqrt(252)
    
    return float(sharpe_annual)


def calculate_max_drawdown(equity_curve: pd.Series) -> float:
    """
    Calculate Maximum Drawdown
    
    Max Drawdown = (Trough Value - Peak Value) / Peak Value
    """
    if len(equity_curve) < 2:
        return 0.0
    
    running_max = equity_curve.expanding().max()
    drawdown = (equity_curve - running_max) / running_max
    
    max_dd = drawdown.min()
    
    return float(max_dd * 100)  # Return as percentage


def calculate_win_rate(trades: pd.DataFrame) -> float:
    """Calculate percentage of winning trades"""
    if len(trades) == 0:
        return 0.0
    
    winning_trades = len(trades[trades['pnl'] > 0])
    total_trades = len(trades)
    
    return (winning_trades / total_trades) * 100


def calculate_profit_factor(trades: pd.DataFrame) -> float:
    """
    Calculate Profit Factor
    
    Profit Factor = Gross Profit / Gross Loss
    """
    if len(trades) == 0:
        return 0.0
    
    gross_profit = trades[trades['pnl'] > 0]['pnl'].sum()
    gross_loss = abs(trades[trades['pnl'] < 0]['pnl'].sum())
    
    if gross_loss == 0:
        return float('inf') if gross_profit > 0 else 0.0
    
    return gross_profit / gross_loss