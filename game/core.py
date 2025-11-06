"""Core game loop and rendering logic."""

from __future__ import annotations

import sys
import time
from enum import Enum, auto
from pathlib import Path
from typing import Optional, Tuple

import pygame

from .config import Config, DEFAULT_CONFIG
from .food import spawn_food
from .score import load_highscore, save_highscore
from .snake import Snake

Position = Tuple[int, int]


class GameStatus(Enum):
    RUNNING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


def resource_path(relative: str) -> str:
    """Return absolute path to resource, compatible with PyInstaller."""

    if hasattr(sys, "_MEIPASS"):
        base_path = Path(getattr(sys, "_MEIPASS"))  # type: ignore[attr-defined]
    else:
        base_path = Path(__file__).resolve().parent
    return str(base_path / relative)


class SnakeGame:
    """Encapsulates the full game, including loop and rendering."""

    BG_COLOR = (12, 12, 12)
    SNAKE_COLOR = (80, 200, 120)
    HEAD_COLOR = (40, 160, 80)
    FOOD_COLOR = (220, 70, 70)
    GRID_COLOR = (30, 30, 30)
    TEXT_COLOR = (230, 230, 230)

    def __init__(self, config: Config | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        pygame.init()
        self.screen = pygame.display.set_mode((self.config.width, self.config.height))
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 28)

        self.move_accumulator = 0.0
        self.last_time = time.perf_counter()

        initial_body = [
            (self.config.cols // 2 + i, self.config.rows // 2)
            for i in range(1, -2, -1)
        ]
        self.snake = Snake(initial_body, (1, 0))
        self.food: Optional[Position] = None

        self.status = GameStatus.RUNNING
        self.score = 0
        self.highscore = load_highscore()
        self.score_surface: Optional[pygame.Surface] = None
        self.highscore_surface: Optional[pygame.Surface] = None
        self.needs_score_update = True

        self.move_interval = self.config.base_move_interval
        self._spawn_food()

        self.pickup_sound = self._load_sound("pickup.wav")
        self.hit_sound = self._load_sound("hit.wav")

    def _load_sound(self, filename: str) -> Optional[pygame.mixer.Sound]:
        path = Path(resource_path("assets")) / filename
        if not path.exists():
            return None
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error:
            return None
        try:
            return pygame.mixer.Sound(str(path))
        except pygame.error:
            return None

    def _play_sound(self, sound: Optional[pygame.mixer.Sound]) -> None:
        if sound is None:
            return
        try:
            sound.play()
        except pygame.error:
            pass

    def _spawn_food(self) -> None:
        self.food = spawn_food(self.config.cols, self.config.rows, self.snake.segments())

    def reset(self) -> None:
        self.snake.reset()
        self.score = 0
        self.status = GameStatus.RUNNING
        self.move_accumulator = 0.0
        self.move_interval = self.config.base_move_interval
        self._spawn_food()
        self.needs_score_update = True

    def _queue_input(self, direction: Position) -> None:
        self.snake.queue_turn(direction)

    def _handle_keydown(self, key: int) -> None:
        mapping = {
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
        }
        if key in mapping:
            self._queue_input(mapping[key])
        elif key == pygame.K_p:
            if self.status == GameStatus.RUNNING:
                self.status = GameStatus.PAUSED
            elif self.status == GameStatus.PAUSED:
                self.status = GameStatus.RUNNING
        elif key == pygame.K_r:
            self.reset()

    def _update_move_interval(self) -> None:
        levels = self.score // self.config.accel_every
        interval = self.config.base_move_interval * (self.config.accel_factor ** levels)
        self.move_interval = max(self.config.min_move_interval, interval)

    def _tick_snake(self) -> None:
        next_head = self.snake.preview_next_head()
        grow = self.food is not None and next_head == self.food
        new_head = self.snake.step(grow)

        if grow:
            self.score += 1
            self.needs_score_update = True
            self._play_sound(self.pickup_sound)
            self._spawn_food()
            self._update_move_interval()

        if (
            new_head[0] < 0
            or new_head[0] >= self.config.cols
            or new_head[1] < 0
            or new_head[1] >= self.config.rows
            or self.snake.hits_self()
        ):
            self.status = GameStatus.GAME_OVER
            self._play_sound(self.hit_sound)
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)
                self.needs_score_update = True

        if self.food is None:
            self.status = GameStatus.GAME_OVER
            if self.score > self.highscore:
                self.highscore = self.score
                save_highscore(self.highscore)
                self.needs_score_update = True

    def _update(self, dt: float) -> None:
        if self.status != GameStatus.RUNNING:
            return
        self.move_accumulator += dt
        while self.move_accumulator >= self.move_interval:
            self.move_accumulator -= self.move_interval
            self._tick_snake()
            if self.status != GameStatus.RUNNING:
                break

    def _format_score(self) -> None:
        if not self.needs_score_update:
            return
        score_text = f"Score: {self.score}"
        highscore_text = f"Best: {self.highscore}"
        self.score_surface = self.font.render(score_text, True, self.TEXT_COLOR)
        self.highscore_surface = self.font.render(highscore_text, True, self.TEXT_COLOR)
        self.needs_score_update = False

    def _draw_grid(self) -> None:
        for x in range(0, self.config.width, self.config.cell_size):
            pygame.draw.line(self.screen, self.GRID_COLOR, (x, 0), (x, self.config.height))
        for y in range(0, self.config.height, self.config.cell_size):
            pygame.draw.line(self.screen, self.GRID_COLOR, (0, y), (self.config.width, y))

    def _draw(self) -> None:
        self.screen.fill(self.BG_COLOR)
        self._draw_grid()

        cell = self.config.cell_size
        for index, segment in enumerate(self.snake.segments()):
            color = self.HEAD_COLOR if index == 0 else self.SNAKE_COLOR
            rect = pygame.Rect(segment[0] * cell, segment[1] * cell, cell, cell)
            pygame.draw.rect(self.screen, color, rect)

        if self.food:
            food_rect = pygame.Rect(
                self.food[0] * cell,
                self.food[1] * cell,
                cell,
                cell,
            )
            pygame.draw.rect(self.screen, self.FOOD_COLOR, food_rect)

        self._format_score()
        if self.score_surface:
            self.screen.blit(self.score_surface, (10, 10))
        if self.highscore_surface:
            self.screen.blit(self.highscore_surface, (10, 40))

        if self.status == GameStatus.GAME_OVER:
            overlay = self.font.render("Press R to restart", True, self.TEXT_COLOR)
            rect = overlay.get_rect(center=(self.config.width // 2, self.config.height // 2))
            self.screen.blit(overlay, rect)
        elif self.status == GameStatus.PAUSED:
            overlay = self.font.render("Paused", True, self.TEXT_COLOR)
            rect = overlay.get_rect(center=(self.config.width // 2, self.config.height // 2))
            self.screen.blit(overlay, rect)

        pygame.display.flip()

    def process_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
        return True

    def run(self) -> None:
        running = True
        while running:
            running = self.process_events()
            now = time.perf_counter()
            dt = now - self.last_time
            self.last_time = now
            self._update(dt)
            self._draw()
            self.clock.tick(self.config.fps)

        pygame.quit()


def main() -> None:
    SnakeGame().run()


if __name__ == "__main__":
    main()
