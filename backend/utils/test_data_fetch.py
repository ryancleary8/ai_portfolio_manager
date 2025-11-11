"""Tests for data fetch helpers."""

import pandas as pd

from backend.utils.data_fetch import _normalise_ohlcv_columns


def test_normalise_columns_handles_close_variants():
    """Columns like ``Close*`` should be mapped to the canonical ``close``."""

    df = pd.DataFrame(
        {
            "Date": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Close*": [100.0, 101.0],
            "Open": [99.0, 100.5],
            "High": [102.0, 103.0],
            "Low": [98.5, 99.5],
            "Volume": [1_000_000, 1_200_000],
        }
    )

    normalised = _normalise_ohlcv_columns(df)

    assert "close" in normalised.columns
    pd.testing.assert_series_equal(normalised["close"], pd.Series([100.0, 101.0], name="close"))


def test_normalise_columns_prefers_existing_close_over_adjusted_close():
    """When both close and adjusted close exist we retain the close price."""

    df = pd.DataFrame(
        {
            "DATE": pd.date_range("2024-01-01", periods=2, freq="D"),
            "Close": [150.0, 151.5],
            "Adj Close": [149.5, 151.0],
            "Volume": [900_000, 850_000],
        }
    )

    normalised = _normalise_ohlcv_columns(df)

    assert "close" in normalised.columns
    pd.testing.assert_series_equal(normalised["close"], pd.Series([150.0, 151.5], name="close"))
    assert "adj_close" in normalised.columns
