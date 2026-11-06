import argparse
import os
import sys
import time

from game.models import Game

# Кроссплатформенное чтение нажатия клавиши
if os.name == "nt":
    import msvcrt

    def get_key() -> str | None:
        if msvcrt.kbhit():
            key = msvcrt.getch()
            try:
                return key.decode("utf-8").lower()
            except UnicodeDecodeError:
                return None
        return None
else:
    import select
    import termios
    import tty

    def get_key() -> str | None:
        dr, _, _ = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1).lower()
        return None


def clear_screen() -> None:
    """Очищает экран терминала через ANSI-последовательность (без моргания)."""
    sys.stdout.write("\033[H")
    sys.stdout.flush()


def show_menu() -> int:
    """Отображает стартовое меню для выбора скорости игры."""
    selected_speed = 10  # Дефолтная скорость

    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 40)
        print("         КОНСОЛЬНАЯ ИГРА 'ЗМЕЙКА'")
        print("=" * 40)
        print("  1. Легкая скорость (fps: 6)")
        print("  2. Нормальная скорость (fps: 10) [Рекомендуется]")
        print("  3. Быстрая скорость (fps: 15)")
        print("  4. Запустить с настройками по умолчанию")
        print("  q. Выход")
        print("-" * 40)
        
        choice = input("Выберите пункт меню (1-4 или q): ").strip().lower()

        if choice == '1':
            return 6
        elif choice == '2':
            return 10
        elif choice == '3':
            return 15
        elif choice == '4':
            return selected_speed
        elif choice == 'q':
            sys.exit(0)
        else:
            print("Неверный выбор! Нажмите Enter и попробуйте снова.")
            input()


def show_game_over_menu(score: int) -> str:
    """Отображает экран Game Over с выбором дальнейших действий."""
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("=" * 40)
        print("               КОНЕЦ ИГРЫ")
        print("=" * 40)
        print(f"       Итоговый счет: {score}")
        print("-" * 40)
        print("  1. Играть еще раз (на той же скорости)")
        print("  2. Вернуться в главное меню")
        print("  3. Выйти из игры")
        print("-" * 40)
        
        choice = input("Выберите действие (1-3): ").strip()

        if choice == '1':
            return 'restart'
        elif choice == '2':
            return 'menu'
        elif choice == '3':
            sys.exit(0)
        else:
            print("Неверный выбор! Нажмите Enter и попробуйте снова.")
            input()


def render(game: Game, is_paused: bool) -> None:
    """Отрисовывает игровое поле в терминале с компенсацией пропорций шрифта."""
    clear_screen()
    
    # Верхняя граница (учитываем удвоение ширины для квадрата ячеек)
    print("#" * ((game.width * 2) + 2))

    for y in range(game.height):
        row = ["#"]
        for x in range(game.width):
            pos = (x, y)
            if pos == game.snake.head():
                row.append("OO")  # Голова змейки (двойной символ для квадрата)
            elif pos in game.snake.body[1:]:
                row.append("oo")  # Тело змейки
            elif pos == game.food:
                row.append("xx")  # Еда
            else:
                row.append("  ")  # Пустая клетка (два пробела)
        row.append("#")
        print("".join(row))

    # Нижняя граница
    print("#" * ((game.width * 2) + 2))
    status = "ПАУЗА (нажмите P для продолжения)" if is_paused else f"Счет: {game.score} | Скорость: {game.speed}"
    print(f"{status} | Управление: W/A/S/D, P - пауза, Q - выход")


def run_game(width: int, height: int, speed: int) -> str:
    """Запускает игровой процесс. Возвращает статус ('restart' или 'menu')."""
    game = Game(width=width, height=height, speed=speed)

    os.system("cls" if os.name == "nt" else "clear")

    current_dir = (1, 0)  # Старт вправо
    is_paused = False     # Состояние паузы

    # Настройка терминала для Linux/macOS, если требуется
    old_settings = None
    if os.name != "nt":
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)

    try:
        while not game.is_over:
            render(game, is_paused)

            # Опрос клавиатуры в течение кадра
            start_time = time.time()
            frame_delay = 1 / game.speed
            
            while time.time() - start_time < frame_delay:
                key = get_key()
                if key:
                    if key == 'w':
                        current_dir = (0, -1)
                    elif key == 's':
                        current_dir = (0, 1)
                    elif key == 'a':
                        current_dir = (-1, 0)
                    elif key == 'd':
                        current_dir = (1, 0)
                    elif key == 'p':
                        is_paused = not is_paused  # Переключение паузы
                    elif key == 'q':
                        game.is_over = True
                        break
                time.sleep(0.01)

            # Если игра не на паузе и не окончена — делаем шаг
            if not game.is_over and not is_paused:
                game.step(current_dir)

    finally:
        if os.name != "nt" and old_settings:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

    # Вызываем интерактивное меню после проигрыша
    return show_game_over_menu(game.score)


def main() -> None:
    """Точка входа в программу с поддержкой аргументов командной строки, меню и рестарта."""
    parser = argparse.ArgumentParser(description="Консольная игра Змейка")
    parser.add_argument("--width", type=int, default=40, help="Ширина поля")
    parser.add_argument("--height", type=int, default=20, help="Высота поля")
    parser.add_argument("--speed", type=int, default=None, help="Начальная скорость (fps)")
    args = parser.parse_args()

    # Если скорость не задана аргументом, открываем стартовое меню
    current_speed = args.speed if args.speed is not None else show_menu()

    while True:
        action = run_game(width=args.width, height=args.height, speed=current_speed)
        
        if action == 'menu':
            current_speed = show_menu()
        elif action == 'restart':
            # Если рестарт, то ничего менять не нужно — переменная current_speed сохраняет текущее значение!
            pass

if __name__ == "__main__":
    main()