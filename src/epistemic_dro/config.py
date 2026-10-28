"""Configuration loading.

The YAML file is deliberately plain: the frozen experiment card, not the YAML,
is the authoritative record once a confirmatory run begins.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

__all__ = ["load_config"]


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML configuration file.

    Args:
        path: Path to a YAML file.

    Returns:
        The parsed mapping.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file does not contain a mapping.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError(f"config must be a mapping, got {type(config).__name__}")
    return config
