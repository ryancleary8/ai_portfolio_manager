"""Command line utility to train PPO models for the portfolio manager."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import joblib
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.vec_env import DummyVecEnv

from .config_loader import load_training_config
from .data_preparation import TickerDataset, build_datasets
from .envs import SingleStockTradingEnv

LOGGER = logging.getLogger(__name__)


class TrainingProgressCallback(BaseCallback):
    """A simple textual progress bar for PPO training."""

    def __init__(
        self,
        total_timesteps: int,
        model_name: str,
        bar_width: int = 40,
        update_interval: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.total_timesteps = max(total_timesteps, 1)
        self.model_name = model_name
        self.bar_width = max(bar_width, 10)
        computed_interval = max(self.total_timesteps // 100, 1)
        if update_interval is None:
            self.update_interval = computed_interval
        else:
            self.update_interval = max(update_interval, 1)
        self._last_printed: int = 0

    def _on_training_start(self) -> None:
        print(f"\n🚀 Starting training for '{self.model_name}'")
        self._print_progress(0)

    def _on_step(self) -> bool:
        if (
            self.num_timesteps - self._last_printed >= self.update_interval
            or self.num_timesteps >= self.total_timesteps
        ):
            self._last_printed = self.num_timesteps
            self._print_progress(self.num_timesteps)
        return True

    def _on_training_end(self) -> None:
        # Ensure the bar ends on a new line once training is complete.
        self._print_progress(self.total_timesteps, final=True)
        print(f"✅ Finished training for '{self.model_name}'\n")

    def _print_progress(self, current_timesteps: int, *, final: bool = False) -> None:
        progress = min(current_timesteps, self.total_timesteps)
        fraction = progress / self.total_timesteps
        filled = int(self.bar_width * fraction)
        bar = "█" * filled + "-" * (self.bar_width - filled)
        percent = fraction * 100
        end = "\n" if final else "\r"
        print(
            f"[{bar}] {percent:6.2f}% ({progress}/{self.total_timesteps} steps)",
            end=end,
            flush=True,
        )


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )


def create_envs(datasets: Iterable[TickerDataset]) -> DummyVecEnv:
    env_fns = [
        (lambda data: (lambda: SingleStockTradingEnv(data)))(dataset)
        for dataset in datasets
    ]
    return DummyVecEnv(env_fns)


def train_single_model(
    model_name: str,
    model_cfg: Dict[str, Any],
    defaults: Dict[str, Any],
) -> None:
    tickers = model_cfg["tickers"]
    history_period = model_cfg.get("history_period", defaults.get("history_period", "2y"))
    min_history = int(model_cfg.get("min_history", defaults.get("min_history", 200)))
    total_timesteps = int(model_cfg.get("total_timesteps", defaults.get("total_timesteps", 200_000)))
    output_dir = Path(model_cfg.get("output_dir", defaults.get("output_dir", "backend/models")))
    model_filename = model_cfg.get("model_filename", f"{model_name}_model.zip")
    scaler_filename = model_cfg.get("scaler_filename", f"{model_name}_scaler.pkl")

    ppo_params: Dict[str, Any] = dict(defaults.get("ppo_params", {}))
    ppo_params.update(model_cfg.get("ppo_params", {}))

    LOGGER.info("Preparing datasets for model '%s' (%s)...", model_name, ", ".join(tickers))

    datasets, scaler = build_datasets(tickers, period=history_period, min_history=min_history)

    vec_env = create_envs(datasets)

    LOGGER.info("Training PPO agent for '%s' with %s timesteps", model_name, total_timesteps)

    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1 if LOGGER.level <= logging.DEBUG else 0,
        **ppo_params,
    )
    progress_callback = TrainingProgressCallback(
        total_timesteps=total_timesteps,
        model_name=model_name,
    )
    model.learn(total_timesteps=total_timesteps, callback=progress_callback)

    output_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / model_filename
    scaler_path = output_dir / scaler_filename

    LOGGER.info("Saving model to %s", model_path)
    model.save(model_path)

    LOGGER.info("Saving scaler to %s", scaler_path)
    joblib.dump(scaler, scaler_path)


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to a YAML configuration file. Defaults to training_config.yaml.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging output.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> None:
    args = parse_args(argv)
    configure_logging(verbose=args.verbose)

    config = load_training_config(args.config)
    defaults: Dict[str, Any] = config.get("defaults", {})

    for model_name, model_cfg in config["models"].items():
        try:
            train_single_model(model_name, model_cfg, defaults)
        except Exception as exc:  # pragma: no cover - defensive error handling
            LOGGER.exception("Failed to train model '%s': %s", model_name, exc)


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
