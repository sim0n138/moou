# Snake — Pygame 2D Game

Полностью рабочая реализация классической игры «Змейка» на Python 3.11+ с использованием Pygame. В проект включены игровая логика, конфигурация параметров, автотесты, линтинг и сборка исполняемого файла под Windows.

## Основные особенности
- Стабильные 60 FPS и отделённый таймер логики движения змейки.
- Плавное управление стрелками или WASD, очередь поворотов и запрет разворота на 180°.
- Динамическое ускорение каждые `accel_every` очков (по умолчанию на 8%, но не быстрее `min_move_interval`).
- Сохранение рекорда в `%APPDATA%/Snake/` (Windows) или `~/.snake/` (macOS/Linux).
- Пауза (`P`), рестарт (`R`), обработка поражений при столкновениях, безопасная работа ассетов при упаковке.
- PyInstaller-сборка `.exe`, CI на GitHub Actions (ruff + pytest).

## Требования
- Python 3.11 или новее (Windows/macOS/Linux).
- Виртуальное окружение (рекомендовано).
- Системные зависимости Pygame (SDL) — устанавливаются автоматически на Windows; на Linux могут потребоваться дополнительные пакеты (`sudo apt install libsdl2-dev libfreetype6-dev`, и т. п.).

## Установка зависимостей
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# или
.venv\\Scripts\\activate  # Windows PowerShell

pip install -r requirements.txt
```

## Запуск из исходников
```bash
python main.py
```

### Управление
- Стрелки или WASD — движение.
- `P` — пауза / продолжить.
- `R` — рестарт после поражения или в любой момент.

## Настройки
Все параметры вынесены в [`game/config.py`](game/config.py). Значения по умолчанию:

```python
Config(
    cell_size=20,
    rows=30,
    cols=30,
    base_move_interval=0.12,
    min_move_interval=0.045,
    accel_every=5,
    accel_factor=0.92,
    fps=60,
)
```

Изменяя эти параметры, можно подстроить размер поля, скорость, шаг ускорения и целевой FPS.

## Тесты и линтинг
```bash
pytest
ruff check .
```

На GitHub Actions настроен workflow `.github/workflows/ci.yml`, который повторяет эти шаги в Python 3.11.

## Сборка Windows `.exe`
1. Убедитесь, что активировано виртуальное окружение и зависимости установлены.
2. Выполните команду:
   ```bash
   pyinstaller --onefile --windowed --name Snake --add-data "game/assets:assets" main.py
   ```
   - Каталог `game/assets` будет добавлен в сборку и доступен по относительному пути через helper `resource_path()`.
   - По окончании получите `dist/Snake.exe`. Проверьте SHA256-сумму перед отправкой пользователям.
3. Если нужны дополнительные файлы (шрифты, звуки) — добавьте их в `game/assets` и повторите сборку с флагом `--add-data`.

> Альтернатива: [cx_Freeze](https://github.com/marcelotduarte/cx_Freeze) также подходит для упаковки, но в этом проекте официально поддерживается PyInstaller.

## Тестирование
- Юнит-тесты (`tests/test_snake.py`, `tests/test_food.py`) закрывают логику роста змейки, очередь поворотов, запрет разворотов и генерацию еды.
- Дополнительные заметки:
  - Проверяйте корректность работы рекордов при разных правах доступа.
  - При сборке `.exe` убедитесь, что ассеты доступны (используйте helper `resource_path`).

## Траблшутинг
- **Пустое окно/нет текста** — убедитесь, что доступен системный шрифт, либо положите TTF-файл в `game/assets` и загрузите через `resource_path()`.
- **Медленный рендер сетки** — отключите отрисовку сетки в `SnakeGame._draw_grid()` (или закомментируйте вызов).
- **Проблемы со звуком** — SDL может не инициализировать аудио на отдельных системах; инициализация обёрнута в `try/except`, можно полностью отключить звук, удалив WAV-файлы.
- **Размытое изображение на Windows** — включите режим совместимости DPI для исполняемого файла.
- **Антивирус ругается на `.exe`** — подпишите файл или добавьте исключение; приложите SHA256 для проверки целостности.

## Структура проекта
```
project-root/
├── main.py
├── requirements.txt
├── README.md
├── game/
│   ├── __init__.py
│   ├── config.py
│   ├── core.py
│   ├── snake.py
│   ├── food.py
│   ├── score.py
│   └── assets/
│       └── README.txt
├── tests/
│   ├── test_food.py
│   └── test_snake.py
└── .github/
    └── workflows/
        └── ci.yml
```

## Команды
| Цель | Windows | macOS/Linux |
| ---- | ------- | ----------- |
| Установка зависимостей | `python -m venv .venv && .venv\\Scripts\\activate && pip install -r requirements.txt` | `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt` |
| Запуск игры | `python main.py` | `python main.py` |
| Тесты | `pytest` | `pytest` |
| Линтинг | `ruff check .` | `ruff check .` |
| Сборка `.exe` | `pyinstaller --onefile --windowed --name Snake --add-data "game/assets:assets" main.py` | — |

---

### Краткие инструкции
- **Запуск из исходников:** активируйте окружение и выполните `python main.py`.
- **Сборка `.exe`:** `pyinstaller --onefile --windowed --name Snake --add-data "game/assets:assets" main.py` (после установки зависимостей).
