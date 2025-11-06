"""Snake entity and movement logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

Vector = Tuple[int, int]
Position = Tuple[int, int]


OPPOSITES: dict[Vector, Vector] = {
    (1, 0): (-1, 0),
    (-1, 0): (1, 0),
    (0, 1): (0, -1),
    (0, -1): (0, 1),
}


@dataclass
class Snake:
    """Represents the snake and encapsulates its movement rules."""

    initial_body: Iterable[Position]
    initial_direction: Vector
    body: List[Position] = field(init=False)
    direction: Vector = field(init=False)
    pending_turn: Optional[Vector] = field(default=None, init=False)

    def __post_init__(self) -> None:
        initial = list(self.initial_body)
        if not initial:
            raise ValueError("Snake body cannot be empty")
        object.__setattr__(self, "initial_body", tuple(initial))
        self.body = list(initial)
        self.direction = self.initial_direction

    @property
    def head(self) -> Position:
        return self.body[0]

    def occupies(self, cell: Position) -> bool:
        return cell in self.body

    def reset(self) -> None:
        self.body = list(self.initial_body)
        self.direction = self.initial_direction
        self.pending_turn = None

    def queue_turn(self, new_direction: Vector) -> None:
        if new_direction == self.direction:
            return
        if new_direction not in OPPOSITES:
            return
        if OPPOSITES[self.direction] == new_direction:
            return
        if self.pending_turn is not None and self.pending_turn == new_direction:
            return
        if self.pending_turn is not None and OPPOSITES[self.pending_turn] == new_direction:
            return
        self.pending_turn = new_direction

    def preview_next_head(self) -> Position:
        direction = self.pending_turn or self.direction
        dx, dy = direction
        head_x, head_y = self.head
        return (head_x + dx, head_y + dy)

    def step(self, grow: bool) -> Position:
        if self.pending_turn is not None:
            self.direction = self.pending_turn
            self.pending_turn = None

        dx, dy = self.direction
        head_x, head_y = self.head
        new_head = (head_x + dx, head_y + dy)

        self.body.insert(0, new_head)
        if not grow:
            self.body.pop()
        return new_head

    def hits_self(self) -> bool:
        return self.head in self.body[1:]

    def segments(self) -> List[Position]:
        return list(self.body)
