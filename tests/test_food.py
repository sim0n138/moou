import random

import pytest

from game.food import spawn_food


def test_food_not_on_snake(monkeypatch):
    cols, rows = 5, 5
    snake_cells = {(2, 2), (2, 3), (2, 4)}

    def fake_choice(seq):
        assert all(cell not in snake_cells for cell in seq)
        return seq[0]

    monkeypatch.setattr(random, "choice", fake_choice)
    food = spawn_food(cols, rows, snake_cells)
    assert food not in snake_cells


def test_food_none_when_full():
    cols, rows = 2, 2
    snake_cells = {(x, y) for x in range(cols) for y in range(rows)}
    assert spawn_food(cols, rows, snake_cells) is None
