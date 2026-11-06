from game.models import Game, Snake


def test_snake_move() -> None:
    """Проверка корректности перемещения змейки."""
    snake = Snake((5, 5), (1, 0))
    snake.move(1, 0)
    assert snake.head() == (6, 5)
    assert len(snake.body) == 2


def test_snake_grow() -> None:
    """Проверка роста змейки при поедании еды."""
    snake = Snake((5, 5), (1, 0))
    snake.grow()
    snake.move(1, 0)
    assert len(snake.body) == 2


def test_snake_self_collision() -> None:
    """Проверка столкновения змейки с самой собой."""
    snake = Snake((5, 5), (1, 0))
    # Искусственно делаем длинную змейку, которая сворачивает на себя
    snake.body = [(5, 5), (5, 6), (6, 6), (6, 5)]
    assert snake.collides_self() is True


def test_game_wall_collision() -> None:
    """Проверка столкновения со стеной (конец игры)."""
    game = Game(width=10, height=10)
    # Перемещаем голову змейки прямо к левой стене и делаем шаг за границу
    game.snake.body = [(0, 5)]
    game.step((-1, 0))
    assert game.is_over is True


def test_food_spawn() -> None:
    """Проверка, что еда появляется внутри границ поля."""
    game = Game(width=10, height=10)
    fx, fy = game.food
    assert 0 <= fx < 10
    assert 0 <= fy < 10