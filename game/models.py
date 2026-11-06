import random


class Snake:
    """Класс, описывающий змейку, ее движение, рост и столкновения."""

    def __init__(self, start_pos: tuple[int, int], direction: tuple[int, int]) -> None:
        # Тело змейки — список координат сегментов [(x, y), ...]
        self.body: list[tuple[int, int]] = [start_pos]
        self.direction: tuple[int, int] = direction
        self._grow_pending: bool = False

    def head(self) -> tuple[int, int]:
        """Возвращает координаты головы змейки."""
        return self.body[0]

    def move(self, dx: int, dy: int) -> None:
        """Перемещает змейку в новом направлении."""
        self.direction = (dx, dy)
        hx, hy = self.head()
        new_head = (hx + dx, hy + dy)
        
        # Добавляем новую голову в начало списка
        self.body.insert(0, new_head)
        
        # Если не нужно расти, удаляем последний элемент (хвост)
        if self._grow_pending:
            self._grow_pending = False
        else:
            self.body.pop()

    def grow(self) -> None:
        """Отмечает, что на следующем шаге змейка должна вырасти."""
        self._grow_pending = True

    def collides_self(self) -> bool:
        """Проверяет, врезалась ли голова змейки в собственный хвост."""
        return self.head() in self.body[1:]


class Game:
    """Класс, управляющий игровым процессом, едой, счетом и состоянием игры."""

    def __init__(self, width: int, height: int, speed: int = 10) -> None:
        self.width: int = width
        self.height: int = height
        self.speed: int = speed
        self.score: int = 0
        self.is_over: bool = False

        # Стартовая позиция змейки по центру поля
        start_x = width // 2
        start_y = height // 2
        self.snake: Snake = Snake((start_x, start_y), (1, 0))
        
        self.food: tuple[int, int] = (0, 0)
        self.spawn_food()

    def spawn_food(self) -> None:
        """Генерирует еду в случайной свободной от змейки клетке."""
        while True:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            if (fx, fy) not in self.snake.body:
                self.food = (fx, fy)
                break

    def step(self, direction: tuple[int, int]) -> None:
        """Выполняет один шаг игры."""
        if self.is_over:
            return

        dx, dy = direction
        
        # Защита от разворота на 180 градусов за один шаг
        curr_dx, curr_dy = self.snake.direction
        if (dx == -curr_dx and dy == 0) or (dy == -curr_dy and dx == 0):
            dx, dy = curr_dx, curr_dy

        self.snake.move(dx, dy)
        hx, hy = self.snake.head()

        # Проверка столкновения со стенами
        if not (0 <= hx < self.width and 0 <= hy < self.height):
            self.is_over = True
            return

        # Проверка столкновения с собой
        if self.snake.collides_self():
            self.is_over = True
            return

        # Проверка поедания еды
        if self.snake.head() == self.food:
            self.snake.grow()
            self.score += 1
            # Скорость постоянная, убрано искусственное замедление
            self.spawn_food()