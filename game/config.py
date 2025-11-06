"""Configuration for the Snake game."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Immutable configuration values for the game."""

    cell_size: int = 20
    rows: int = 30
    cols: int = 30
    base_move_interval: float = 0.12
    min_move_interval: float = 0.045
    accel_every: int = 5
    accel_factor: float = 0.92
    fps: int = 60

    @property
    def width(self) -> int:
        return self.cols * self.cell_size

    @property
    def height(self) -> int:
        return self.rows * self.cell_size


DEFAULT_CONFIG = Config()
