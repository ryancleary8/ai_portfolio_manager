"""Market Data Fetching utilities.

Retrieves historical and real-time data from Yahoo Finance and Alpaca.
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_market_data(tickers: List[str], days: int = 60) -> Dict[str, pd.DataFrame]:
    """
    Fetch historical market data for multiple tickers
    
    Args:
        tickers: List of stock symbols
        days: Number of days of historical data
    
    Returns:
        Dictionary mapping ticker -> DataFrame
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    market_data = {}
    
    for ticker in tickers:
        try:
            logger.info(f"📊 Fetching data for {ticker}...")
            
            # Download data from Yahoo Finance
            df = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                progress=False
            )
            
            if df.empty:
                logger.warning(f"⚠️ No data returned for {ticker}")
                continue
            
            # Clean column names
            df.columns = [col.lower() for col in df.columns]
            
            # Reset index to make date a column
            df = df.reset_index()
            
            market_data[ticker] = df
            logger.info(f"✅ Fetched {len(df)} rows for {ticker}")
            
        except Exception as e:
            logger.error(f"❌ Error fetching data for {ticker}: {e}")
            continue
    
    return market_data


def _normalise_ohlcv_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of *df* with normalised column naming conventions."""

    normalised = df.copy()
    normalised.columns = [col.lower() for col in normalised.columns]

    # Harmonise the primary date column name if it exists under different aliases.
    if "date" not in normalised.columns:
        for candidate in ("datetime", "index", "timestamp"):
            if candidate in normalised.columns:
                normalised = normalised.rename(columns={candidate: "date"})
                break

    return normalised


def load_local_historical_data(
    ticker: str,
    *,
    directory: str = "data/historical",
) -> Optional[pd.DataFrame]:
    """Attempt to load historical OHLCV data for *ticker* from CSV files.

    The loader supports two filename conventions:

    * ``{ticker}.csv`` (case-insensitive)
    * ``{ticker}_YYYYMMDD.csv`` — the most recent file is selected automatically.

    Args:
        ticker: Stock symbol to search for.
        directory: Directory containing historical CSV files.

    Returns:
        DataFrame with standardised column names if a file is located, otherwise
        ``None``.
    """

    base_path = Path(directory)
    if not base_path.exists():
        return None

    possible_filenames: Iterable[Path] = (
        base_path / f"{ticker}.csv",
        base_path / f"{ticker.lower()}.csv",
        base_path / f"{ticker.upper()}.csv",
    )

    for candidate in possible_filenames:
        if candidate.exists():
            try:
                df = pd.read_csv(candidate)
                logger.info("✅ Loaded %s data from %s", ticker, candidate)
                return _normalise_ohlcv_columns(df)
            except Exception as exc:  # pragma: no cover - defensive
                logger.error("❌ Error reading %s: %s", candidate, exc)
                return None

    matching_files: List[Path] = []
    for pattern in (f"{ticker}_*.csv", f"{ticker.lower()}_*.csv", f"{ticker.upper()}_*.csv"):
        matching_files.extend(sorted(base_path.glob(pattern)))

    matching_files.sort()
    if matching_files:
        latest_file = matching_files[-1]
        try:
            df = pd.read_csv(latest_file)
            logger.info("✅ Loaded %s data from %s", ticker, latest_file)
            return _normalise_ohlcv_columns(df)
        except Exception as exc:  # pragma: no cover - defensive
            logger.error("❌ Error reading %s: %s", latest_file, exc)

    return None


def get_historical_data(
    ticker: str,
    period: str = "1y",
    *,
    source: str = "auto",
    local_data_dir: Optional[str] = "data/historical",
) -> Optional[pd.DataFrame]:
    """
    Get historical data for a single ticker
    
    Args:
        ticker: Stock symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        DataFrame with OHLCV data
    """
    source_normalised = source.lower()

    if source_normalised not in {"auto", "local", "yfinance"}:
        raise ValueError(
            "source must be one of {'auto', 'local', 'yfinance'}; "
            f"received {source!r}"
        )

    if source_normalised in {"auto", "local"} and local_data_dir is not None:
        local_df = load_local_historical_data(ticker, directory=local_data_dir)
        if local_df is not None:
            return local_df
        if source_normalised == "local":
            logger.warning("⚠️ No local data found for %s in %s", ticker, local_data_dir)
            return None

    if source_normalised in {"auto", "yfinance"}:
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)

            if df.empty:
                logger.warning(f"⚠️ No historical data for {ticker}")
                return None

            df = df.reset_index()
            return _normalise_ohlcv_columns(df)

        except Exception as e:  # pragma: no cover - fallback protection
            logger.error(f"❌ Error getting historical data for {ticker}: {e}")
            return None

    return None


def get_latest_price(ticker: str) -> Optional[float]:
    """Get latest price for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d")
        
        if not data.empty:
            return float(data['Close'].iloc[-1])
        
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting latest price for {ticker}: {e}")
        return None


def get_latest_bar(tickers: List[str]) -> Dict[str, Dict]:
    """
    Get latest OHLCV bar for multiple tickers
    
    Returns:
        Dictionary mapping ticker -> {open, high, low, close, volume}
    """
    latest_bars = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            data = stock.history(period="1d")
            
            if not data.empty:
                latest = data.iloc[-1]
                latest_bars[ticker] = {
                    'open': float(latest['Open']),
                    'high': float(latest['High']),
                    'low': float(latest['Low']),
                    'close': float(latest['Close']),
                    'volume': float(latest['Volume']),
                    'timestamp': data.index[-1].isoformat()
                }
        
        except Exception as e:
            logger.error(f"❌ Error getting latest bar for {ticker}: {e}")
            continue
    
    return latest_bars


def get_intraday_data(ticker: str, interval: str = "5m") -> Optional[pd.DataFrame]:
    """
    Get intraday data for a ticker
    
    Args:
        ticker: Stock symbol
        interval: Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d)
    
    Returns:
        DataFrame with intraday OHLCV data
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1d", interval=interval)
        
        if df.empty:
            logger.warning(f"⚠️ No intraday data for {ticker}")
            return None
        
        # Clean column names
        df.columns = [col.lower() for col in df.columns]
        df = df.reset_index()
        
        return df
        
    except Exception as e:
        logger.error(f"❌ Error getting intraday data for {ticker}: {e}")
        return None


def save_market_data(data: Dict[str, pd.DataFrame], directory: str = "data/historical"):
    """
    Save market data to CSV files
    
    Args:
        data: Dictionary of ticker -> DataFrame
        directory: Directory to save files
    """
    import os
    
    os.makedirs(directory, exist_ok=True)
    
    for ticker, df in data.items():
        try:
            filename = f"{directory}/{ticker}_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(filename, index=False)
            logger.info(f"💾 Saved {ticker} data to {filename}")
        
        except Exception as e:
            logger.error(f"❌ Error saving data for {ticker}: {e}")


def load_market_data(ticker: str, date: Optional[str] = None, directory: str = "data/historical") -> Optional[pd.DataFrame]:
    """
    Load market data from CSV file
    
    Args:
        ticker: Stock symbol
        date: Date string (YYYYMMDD), defaults to today
        directory: Directory containing CSV files
    
    Returns:
        DataFrame with market data
    """
    import os
    
    if date is None:
        date = datetime.now().strftime('%Y%m%d')
    
    filename = f"{directory}/{ticker}_{date}.csv"
    
    if not os.path.exists(filename):
        logger.warning(f"⚠️ File not found: {filename}")
        return None
    
    try:
        df = pd.read_csv(filename)
        logger.info(f"✅ Loaded {ticker} data from {filename}")
        return df
    
    except Exception as e:
        logger.error(f"❌ Error loading data for {ticker}: {e}")
        return None


def get_market_status() -> Dict:
    """
    Check if market is open
    
    Returns:
        Dictionary with market status info
    """
    from datetime import datetime
    import pytz
    
    # Get current time in ET
    et_tz = pytz.timezone('America/New_York')
    now = datetime.now(et_tz)
    
    # Market hours: 9:30 AM - 4:00 PM ET, Mon-Fri
    is_weekday = now.weekday() < 5  # 0-4 = Mon-Fri
    market_open_time = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = now.replace(hour=16, minute=0, second=0, microsecond=0)
    
    is_market_hours = market_open_time <= now <= market_close_time
    is_open = is_weekday and is_market_hours
    
    return {
        "is_open": is_open,
        "is_weekday": is_weekday,
        "is_market_hours": is_market_hours,
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
        "next_open": get_next_market_open(now),
        "next_close": get_next_market_close(now)
    }


def get_next_market_open(current_time: datetime) -> str:
    """Calculate next market open time"""
    et_tz = pytz.timezone('America/New_York')
    
    # Start with current day at 9:30 AM
    next_open = current_time.replace(hour=9, minute=30, second=0, microsecond=0)
    
    # If already past market open today, move to next day
    if current_time >= next_open:
        next_open += timedelta(days=1)
    
    # Skip weekends
    while next_open.weekday() >= 5:
        next_open += timedelta(days=1)
    
    return next_open.strftime("%Y-%m-%d %H:%M:%S %Z")


def get_next_market_close(current_time: datetime) -> str:
    """Calculate next market close time"""
    et_tz = pytz.timezone('America/New_York')
    
    # Start with current day at 4:00 PM
    next_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)
    
    # If already past market close or it's weekend, move to next day
    if current_time >= next_close or current_time.weekday() >= 5:
        next_close += timedelta(days=1)
    
    # Skip weekends
    while next_close.weekday() >= 5:
        next_close += timedelta(days=1)
    
    return next_close.strftime("%Y-%m-%d %H:%M:%S %Z")