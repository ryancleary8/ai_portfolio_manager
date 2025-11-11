"""Helpers for preparing market data for reinforcement learning training."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from backend.utils.data_fetch import get_historical_data
from backend.utils.indicators import (
    add_bollinger_bands,
    add_ema,
    add_macd,
    add_returns,
    add_rsi,
    add_sma,
)

FEATURE_COLUMNS: Sequence[str] = (
    "close",
    "open",
    "high",
    "low",
    "volume",
    "sma_20",
    "sma_50",
    "ema_12",
    "ema_26",
    "rsi",
    "macd",
    "macd_signal",
    "macd_hist",
    "bb_upper",
    "bb_middle",
    "bb_lower",
    "returns",
)


@dataclass
class TickerDataset:
    """Container holding the features and prices for a single ticker."""

    ticker: str
    features: np.ndarray
    prices: np.ndarray
    dates: pd.Series

    @property
    def observation_dim(self) -> int:
        return self.features.shape[1]


def download_ticker_history(
    ticker: str,
    *,
    period: str,
    source: str = "auto",
    local_data_dir: Optional[str] = "data/historical",
) -> Optional[pd.DataFrame]:
    """Download historical OHLCV data for a ticker."""

    raw_df = get_historical_data(
        ticker,
        period=period,
        source=source,
        local_data_dir=local_data_dir,
    )
    if raw_df is None or raw_df.empty:
        return None

    return raw_df


def build_feature_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Return a feature rich dataframe suitable for RL training."""

    enriched_df = df.copy()
    enriched_df = enriched_df.sort_values("date") if "date" in enriched_df.columns else enriched_df

    enriched_df = add_sma(enriched_df, [20, 50])
    enriched_df = add_ema(enriched_df, [12, 26])
    enriched_df = add_rsi(enriched_df, 14)
    enriched_df = add_macd(enriched_df)
    enriched_df = add_bollinger_bands(enriched_df, 20, 2)
    enriched_df = add_returns(enriched_df)

    enriched_df = enriched_df.dropna().reset_index(drop=True)
    return enriched_df


def build_datasets(
    tickers: Iterable[str],
    *,
    period: str,
    min_history: int = 100,
    source: str = "auto",
    local_data_dir: Optional[str] = "data/historical",
) -> Tuple[List[TickerDataset], StandardScaler]:
    """Download market data and return scaled datasets for each ticker."""

    datasets: List[TickerDataset] = []
    all_features: List[np.ndarray] = []

    for ticker in tickers:
        df = download_ticker_history(
            ticker,
            period=period,
            source=source,
            local_data_dir=local_data_dir,
        )
        if df is None:
            continue

        enriched = build_feature_frame(df)
        if len(enriched) < min_history:
            continue

        feature_matrix = enriched.loc[:, FEATURE_COLUMNS].astype("float32").values
        price_vector = enriched["close"].astype("float32").values

        datasets.append(
            TickerDataset(
                ticker=ticker,
                features=feature_matrix,
                prices=price_vector,
                dates=enriched.get("date", pd.Series(range(len(enriched))))
            )
        )
        all_features.append(feature_matrix)

    if not datasets:
        raise ValueError("No datasets could be constructed from the provided tickers.")

    scaler = StandardScaler()
    stacked = np.vstack(all_features)
    scaler.fit(stacked)

    for dataset in datasets:
        dataset.features = scaler.transform(dataset.features).astype("float32")

    return datasets, scaler


__all__ = [
    "TickerDataset",
    "FEATURE_COLUMNS",
    "build_datasets",
    "build_feature_frame",
    "download_ticker_history",
]
