"""Command line utility to train PPO models for the portfolio manager."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Any, Dict, Iterable

import joblib
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

from .config_loader import load_training_config
from .data_preparation import TickerDataset, build_datasets
from .envs import SingleStockTradingEnv

LOGGER = logging.getLogger(__name__)


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

    model = PPO("MlpPolicy", vec_env, verbose=1 if LOGGER.level <= logging.DEBUG else 0, **ppo_params)
    model.learn(total_timesteps=total_timesteps)

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
