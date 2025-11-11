"""Public wrapper for data fetching utilities.

This module exposes the concrete implementations that live in
:mod:`backend.utils.utils_data_fetch`.  The project historically kept the
fully fledged implementations in helper files that were never imported by the
rest of the codebase, leaving these stubs empty and causing import errors at
runtime.  By re-exporting the helper functions here we keep a single source of
truth for the logic while making ``from utils.data_fetch import ...`` work as
expected.
"""

from __future__ import annotations

from .utils_data_fetch import (  # noqa:F401 - re-exported symbols
    fetch_market_data,
    get_historical_data,
    get_latest_bar,
    get_latest_price,
)

__all__ = [
    "fetch_market_data",
    "get_historical_data",
    "get_latest_bar",
    "get_latest_price",
]
