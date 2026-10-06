import sys
from random import choice, randint

import pygame as pg

# Константы для размеров поля и сетки.
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
DEFAULT_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения.
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Базовые цвета.
COLOR_BLACK = (0, 0, 0)
COLOR_CYAN = (93, 216, 228)
COLOR_RED = (255, 0, 0)
COLOR_ORANGE = (255, 165, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_GREEN = (0, 255, 0)

# Семантические цвета.
BOARD_BACKGROUND_COLOR = COLOR_BLACK
BORDER_COLOR = COLOR_CYAN
APPLE_COLOR = COLOR_RED
BAD_FOOD_COLOR = COLOR_ORANGE
STONE_COLOR = COLOR_GRAY
SNAKE_COLOR = COLOR_GREEN

# Скорость движения змейки.
SPEED = 10

# Словарь поворотов.
TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}

# Настройка игрового окна.
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=DEFAULT_POSITION, body_color=None):
        self.position = position
        self.body_color = body_color

    @staticmethod
    def draw_cell(surface, position, fill_color, border_color=BORDER_COLOR,
                  border_width=1):
        """Отрисовывает одну ячейку: заливка + рамка."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, fill_color, rect)
        pg.draw.rect(surface, border_color, rect, border_width)

    @staticmethod
    def erase_cell(surface, position):
        """Стирает ячейку, заливая её цветом фона."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(surface, BOARD_BACKGROUND_COLOR, rect)

    @staticmethod
    def get_random_free_position(occupied_positions):
        """Возвращает случайную свободную позицию на сетке.

        occupied_positions — set из занятых координат (x, y).
        Если свободных клеток нет, возвращает None.
        """
        max_attempts = GRID_WIDTH * GRID_HEIGHT * 2
        for _ in range(max_attempts):
            x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
            y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            pos = (x, y)
            if pos not in occupied_positions:
                return pos
        return None

    def draw(self, surface):
        """Отрисовывает объект на поверхности.

        Должен быть переопределён в дочерних классах.
        """
        raise NotImplementedError(
            f'Метод draw() не реализован в классе '
            f"'{self.__class__.__name__}'. Обязательно переопределите "
            f'его в наследнике.'
        )


class Apple(GameObject):
    """Класс, описывающий яблоко (правильную еду)."""

    def __init__(self, occupied_positions=None, body_color=APPLE_COLOR):
        """Инициализирует яблоко: задаёт цвет и случайную позицию.

        :param occupied_positions: set занятых координат для проверки.
        :param body_color: цвет объекта в формате RGB.
        """
        super().__init__(body_color=body_color)
        self.position = None
        if occupied_positions is not None:
            self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions):
        """Устанавливает случайную позицию яблока, избегая занятых клеток."""
        new_pos = GameObject.get_random_free_position(occupied_positions)
        if new_pos is not None:
            self.position = new_pos

    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле."""
        if self.position is None:
            return
        GameObject.draw_cell(surface, self.position, self.body_color)


class BadFood(Apple):
    """Класс, описывающий неправильную еду (уменьшает длину змейки)."""

    def __init__(self, occupied_positions=None, body_color=BAD_FOOD_COLOR):
        """Инициализирует объект, передавая другой цвет в родительский класс.

        :param occupied_positions: set занятых координат для проверки.
        :param body_color: цвет объекта в формате RGB.
        """
        super().__init__(
            occupied_positions=occupied_positions, body_color=body_color
        )


class Stone(Apple):
    """Класс, описывающий препятствие (камень)."""

    def __init__(self, occupied_positions=None, body_color=STONE_COLOR):
        """Инициализирует камень, передавая другой цвет в родительский класс.

        :param occupied_positions: set занятых координат для проверки.
        :param body_color: цвет объекта в формате RGB.
        """
        super().__init__(
            occupied_positions=occupied_positions, body_color=body_color
        )


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self, position=DEFAULT_POSITION, body_color=SNAKE_COLOR):
        """Инициализирует змейку с заданными позицией и цветом.

        :param position: начальная позиция головы змейки.
        :param body_color: цвет змейки в формате RGB.
        """
        super().__init__(position=position, body_color=body_color)
        self.reset()

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змейки при запросе нового."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки согласно текущему направлению."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.to_erase.append(self.positions.pop())

    def reduce_length(self):
        """Уменьшает длину змейки на один сегмент."""
        if self.length > 1:
            self.length -= 1
            self.to_erase.append(self.positions.pop())

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.to_erase = []

    def get_occupied_positions(self):
        """Возвращает set всех занятых змеёй позиций."""
        return set(self.positions)

    def draw(self, surface):
        """Отрисовывает голову змейки и стирает удалённые сегменты."""
        for pos in self.to_erase:
            GameObject.erase_cell(surface, pos)
        self.to_erase.clear()
        GameObject.draw_cell(
            surface, self.get_head_position(), self.body_color
        )


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для управления змейкой."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                sys.exit()
            if event.key in TURNS:
                new_direction, opposite = TURNS[event.key]
                if snake.direction != opposite:
                    snake.next_direction = new_direction


def get_occupied(snake, *objects):
    """Возвращает set всех занятых позиций на поле."""
    occupied = snake.get_occupied_positions()
    for obj in objects:
        if obj is not None and obj.position is not None:
            occupied.add(obj.position)
    return occupied


def init_game():
    """Создаёт игровые объекты и расставляет их на поле."""
    snake = Snake()
    occupied = snake.get_occupied_positions()
    apple = Apple(occupied_positions=occupied)
    occupied.add(apple.position)
    bad_food = BadFood(occupied_positions=occupied)
    occupied.add(bad_food.position)
    stone = Stone(occupied_positions=occupied)
    return snake, apple, bad_food, stone


def reposition_objects(snake, apple, bad_food, stone):
    """Перегенерирует позиции всех объектов после сброса змейки."""
    occupied = snake.get_occupied_positions()
    apple.randomize_position(occupied)
    occupied.add(apple.position)
    bad_food.randomize_position(occupied)
    occupied.add(bad_food.position)
    stone.randomize_position(occupied)


def maybe_move_bad_food(bad_food, occupied):
    """С вероятностью 1/5 перемещает плохую еду на новую позицию."""
    if randint(1, 5) == 1:
        old_pos = bad_food.position
        bad_food.randomize_position(occupied)
        if bad_food.position != old_pos:
            GameObject.erase_cell(screen, old_pos)


def maybe_move_stone(stone, occupied):
    """С вероятностью 1/7 перемещает камень на новую позицию."""
    if randint(1, 7) == 1:
        old_pos = stone.position
        stone.randomize_position(occupied)
        if stone.position != old_pos:
            GameObject.erase_cell(screen, old_pos)


def handle_collisions(snake, apple, bad_food, stone):
    """Проверяет столкновения и обновляет состояние.

    Возвращает True, если нужен сброс змейки.
    """
    head = snake.get_head_position()

    if head == stone.position:
        return True

    if head == apple.position:
        snake.length += 1
        occupied = get_occupied(snake, apple, bad_food, stone)
        apple.randomize_position(occupied)
        occupied = get_occupied(snake, apple, bad_food, stone)
        maybe_move_bad_food(bad_food, occupied)
        occupied = get_occupied(snake, apple, bad_food, stone)
        maybe_move_stone(stone, occupied)
        return False

    if head == bad_food.position:
        if snake.length > 1:
            snake.reduce_length()
            occupied = get_occupied(snake, apple, bad_food, stone)
            bad_food.randomize_position(occupied)
            return False
        return True

    if head in snake.positions[1:]:
        return True

    return False


def full_redraw(snake, apple, bad_food, stone):
    """Полная перерисовка экрана после сброса."""
    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw(screen)
    apple.draw(screen)
    bad_food.draw(screen)
    stone.draw(screen)
    pg.display.update()


def draw_frame(snake, apple, bad_food, stone):
    """Инкрементальная отрисовка: голова, хвост, еда, камень."""
    snake.draw(screen)
    apple.draw(screen)
    bad_food.draw(screen)
    stone.draw(screen)
    pg.display.update()


def main():
    """Основная функция игры."""
    pg.init()

    snake, apple, bad_food, stone = init_game()
    full_redraw(snake, apple, bad_food, stone)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if handle_collisions(snake, apple, bad_food, stone):
            snake.reset()
            reposition_objects(snake, apple, bad_food, stone)
            full_redraw(snake, apple, bad_food, stone)
            continue

        draw_frame(snake, apple, bad_food, stone)


if __name__ == '__main__':
    main()
