from __future__ import annotations

from pathlib import Path

from epistemic_dro.config import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_base_config_loads_and_has_required_sections() -> None:
    config = load_config(ROOT / "configs" / "base.yaml")
    required = (
        "project",
        "data",
        "features",
        "model",
        "uncertainty",
        "optimization",
        "evaluation",
    )
    for section in required:
        assert section in config
    assert config["project"]["name"] == "epistemic-dro"
    assert config["optimization"]["max_weight"] == 0.05
