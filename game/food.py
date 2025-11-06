"""Food spawning utilities."""

from __future__ import annotations

import random
from typing import Iterable, Optional, Tuple

Position = Tuple[int, int]


def spawn_food(cols: int, rows: int, snake_cells: Iterable[Position]) -> Optional[Position]:
    """Return a random free cell or ``None`` if the board is full."""

    occupied = set(snake_cells)
    free_cells = [
        (x, y)
        for x in range(cols)
        for y in range(rows)
        if (x, y) not in occupied
    ]
    if not free_cells:
        return None
    return random.choice(free_cells)
