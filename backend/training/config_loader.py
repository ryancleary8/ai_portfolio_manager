"""Configuration loader for RL model training."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

DEFAULT_CONFIG_PATH = Path(__file__).with_name("training_config.yaml")


class TrainingConfigError(RuntimeError):
    """Raised when the training configuration file is invalid."""


def load_training_config(config_path: Optional[str | Path] = None) -> Dict[str, Any]:
    """Load the YAML configuration that describes each model to train.

    Args:
        config_path: Optional path to a YAML file.  When omitted the default
            ``training_config.yaml`` that ships with the repository is used.

    Returns:
        Parsed configuration as a dictionary.

    Raises:
        TrainingConfigError: If the configuration cannot be loaded or is
            missing required sections.
    """

    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not path.exists():
        raise TrainingConfigError(
            f"Training configuration file not found: {path}."
        )

    try:
        with path.open("r", encoding="utf-8") as handle:
            config = yaml.safe_load(handle) or {}
    except yaml.YAMLError as exc:  # pragma: no cover - defensive programming
        raise TrainingConfigError(f"Invalid YAML configuration: {exc}") from exc

    if "models" not in config or not isinstance(config["models"], dict):
        raise TrainingConfigError(
            "Training configuration must include a 'models' mapping."
        )

    for model_name, model_cfg in config["models"].items():
        if "tickers" not in model_cfg:
            raise TrainingConfigError(
                f"Model '{model_name}' must define a non-empty list of tickers."
            )
        if not model_cfg["tickers"]:
            raise TrainingConfigError(
                f"Model '{model_name}' must list at least one ticker to train on."
            )

    return config


__all__ = ["load_training_config", "TrainingConfigError", "DEFAULT_CONFIG_PATH"]
