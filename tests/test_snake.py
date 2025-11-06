import pytest

from game.snake import Snake


@pytest.fixture
def snake():
    return Snake([(2, 2), (1, 2), (0, 2)], (1, 0))


def test_step_without_growth_shortens_tail(snake):
    snake.step(grow=False)
    assert snake.segments() == [(3, 2), (2, 2), (1, 2)]


def test_step_with_growth_extends_length(snake):
    snake.step(grow=True)
    assert snake.segments() == [(3, 2), (2, 2), (1, 2), (0, 2)]


def test_queue_rejects_opposite_direction(snake):
    snake.queue_turn((-1, 0))
    snake.step(False)
    assert snake.direction == (1, 0)


def test_queued_turn_applies_on_next_step(snake):
    snake.queue_turn((0, -1))
    snake.step(False)
    assert snake.direction == (0, -1)
    assert snake.head == (2, 1)


def test_queue_prevents_double_turn(snake):
    snake.queue_turn((0, -1))
    snake.queue_turn((0, 1))
    snake.step(False)
    assert snake.direction == (0, -1)
