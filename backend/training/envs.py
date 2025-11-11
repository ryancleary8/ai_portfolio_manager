"""Custom Gymnasium environments used for PPO training."""

from __future__ import annotations

from typing import Tuple

import numpy as np
from gymnasium import Env, spaces

from .data_preparation import TickerDataset


class SingleStockTradingEnv(Env):
    """A simple trading environment for a single equity.

    The agent can choose to hold, buy, or sell at every step.  Rewards are the
    percentage change in portfolio value driven by the position that was held
    between time ``t`` and ``t+1``.  The goal is to encourage the model to learn
    directional trades on the provided history.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, dataset: TickerDataset, max_position: float = 1.0):
        super().__init__()
        self.dataset = dataset
        self.max_position = max_position

        obs_dim = dataset.observation_dim + 2  # add position + cash fraction
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )
        # 0 = hold, 1 = fully long, 2 = flat
        self.action_space = spaces.Discrete(3)

        self.reset()

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        super().reset(seed=seed)
        self.current_step = 0
        self.position = 0.0
        self.cash = 1.0  # portfolio is normalised to 1.0
        observation = self._get_observation()
        return observation, {}

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        if not self.action_space.contains(action):
            raise ValueError(f"Invalid action {action}")

        price = self.dataset.prices[self.current_step]
        next_step = self.current_step + 1
        terminal = next_step >= len(self.dataset.prices) - 1

        # Translate discrete action into position management
        if action == 1:  # long
            self.position = self.max_position
        elif action == 2:  # exit to cash
            self.position = 0.0
        # action == 0 keeps existing position

        next_price = self.dataset.prices[next_step]
        price_change = (next_price - price) / price if price != 0 else 0.0

        reward = self.position * price_change
        # Update portfolio cash approximation
        self.cash = np.clip(self.cash + reward, 0.0, 10.0)

        self.current_step = next_step
        observation = self._get_observation()

        return observation, float(reward), terminal, False, {
            "price": price,
            "next_price": next_price,
            "position": self.position,
            "portfolio_value": self.cash,
        }

    def _get_observation(self) -> np.ndarray:
        features = self.dataset.features[self.current_step]
        obs = np.concatenate(
            [features, np.array([self.position, self.cash], dtype=np.float32)]
        )
        return obs.astype(np.float32)

    def render(self):  # pragma: no cover - gymnasium API requirement
        return {
            "step": self.current_step,
            "position": self.position,
            "portfolio_value": self.cash,
        }


__all__ = ["SingleStockTradingEnv"]
