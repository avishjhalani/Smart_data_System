from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class LoggingMixin:
    def log(self, message: str) -> None:
        print(f"[LOG]: {message}")


@dataclass(frozen=True)
class StatsSummary:
    """
    Container for per-column dataset statistics.

    Includes operator overloading so stats from parallel workers can be merged.
    """

    mean: Dict[str, float]
    median: Dict[str, float]
    std: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return {"mean": self.mean, "median": self.median, "std": self.std}

    def __add__(self, other: "StatsSummary") -> "StatsSummary":
        # Merge dicts from two partial column sets.
        return StatsSummary(
            mean={**self.mean, **other.mean},
            median={**self.median, **other.median},
            std={**self.std, **other.std},
        )


class SaveMixin:
    def save_stats(self, stats, file="data/datasets.json"):
        import json

        # Allow saving StatsSummary objects produced by our concurrent calculations.
        payload = stats.to_dict() if hasattr(stats, "to_dict") else stats

        try:
            with open(file, "r") as f:
                data = json.load(f)
        except:
            data = []

        data.append(payload)

        with open(file, "w") as f:
            json.dump(data, f, indent=4)