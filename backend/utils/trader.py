"""Public wrapper for the Alpaca trader utilities.

The actual implementation of :class:`AlpacaTrader` and helper routines live in
:mod:`backend.utils.utils_trader`.  This module re-exports them so that the rest
of the codebase can simply import from ``utils.trader``.
"""

from __future__ import annotations

from .utils_trader import (  # noqa:F401 - re-exported symbols
    AlpacaTrader,
    prepare_observation,
)

__all__ = ["AlpacaTrader", "prepare_observation"]
