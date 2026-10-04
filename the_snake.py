from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока (правильная еда)
APPLE_COLOR = (255, 0, 0)

# Цвет оранжевый (неправильная еда)
BAD_FOOD_COLOR = (255, 165, 0)

# Цвет камня (препятствие)
STONE_COLOR = (128, 128, 128)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("Змейка")

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов."""

    def __init__(self, position=None, body_color=None):
        if position is None:
            position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.position = position
        self.body_color = body_color

    def draw(self, surface):
        """
        Отрисовывает объект на поверхности.
        Должен быть переопределён в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс, описывающий яблоко (правильную еду)."""

    def __init__(self):
        """Инициализирует яблоко: задаёт цвет и случайную позицию."""
        super().__init__(body_color=APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайную позицию яблока в пределах игрового поля."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class BadFood(GameObject):
    """Класс, описывающий неправильную еду (уменьшает длину змейки)."""

    def __init__(self):
        """
        Инициализирует объект.
        :param position: кортеж (x, y) — позиция объекта. Если не задана, ставится в центр.
        :param body_color: цвет объекта в формате RGB.
        """
        super().__init__(body_color=BAD_FOOD_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """
        Устанавливает случайную позицию неправильной еды в пределах поля игры.
        """
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает неправильную еду на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Stone(GameObject):
    """Класс, описывающий препятствие (камень)."""

    def __init__(self):
        """Инициализирует камень: задаёт цвет и случайную позицию."""
        super().__init__(body_color=STONE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Устанавливает случайную позицию камня в пределах игрового поля."""
        x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (x, y)

    def draw(self, surface):
        """Отрисовывает камень на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, self.body_color, rect)
        pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        """Инициализирует змейку"""
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        super().__init__(position=start_pos, body_color=SNAKE_COLOR)

        self.length = 1
        self.positions = [start_pos]
        self.direction = RIGHT
        self.next_direction = None
        # Позиция последнего сегмента для затирания следа
        self.last = None

    def get_head_position(self):
        """Возвращает позицию головы змейки."""
        return self.positions[0]

    def update_direction(self):
        """Обновляет направление движения змейки, если было запрошено новое."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки согласно текущему направлению."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учётом прохождения сквозь стены
        new_head_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_head_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_head_x, new_head_y)

        # Сохраняем последнюю позицию для затирания
        self.last = self.positions[-1]

        # Вставляем новую голову в начало списка
        self.positions.insert(0, new_head)

        # Если длина не увеличилась, удаляем хвост
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        self.length = 1
        start_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [start_pos]
        # Случайное начальное направление
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self, surface):
        """Отрисовывает змейку и стирает её след."""
        # Сначала стираем след (если он есть)
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, BOARD_BACKGROUND_COLOR, last_rect)

        # Отрисовываем все сегменты
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, self.body_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def handle_keys(snake):
    """Обрабатывает нажатия клавиш для изменения направления змейки."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and snake.direction != DOWN:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN and snake.direction != UP:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                snake.next_direction = RIGHT


def main():
    # Инициализация PyGame:
    """Основная функция игры."""
    pygame.init()

    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    bad_food = BadFood()
    stone = Stone()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()
        # Тут опишите основную логику игры.
        # Проверка столкновения с камнем
        if head == stone.position:
            snake.reset()
            # При сбросе можно перегенерировать объекты
            apple.randomize_position()
            bad_food.randomize_position()
            stone.randomize_position()
            continue

        # Проверка, съела ли змейка яблоко
        if head == apple.position:
            snake.length += 1
            apple.randomize_position()
            # Иногда генерируем новую плохую еду или камень
            if randint(1, 5) == 1:
                bad_food.randomize_position()
            if randint(1, 7) == 1:
                stone.randomize_position()

        # Проверка, съела ли змейка неправильную еду
        elif head == bad_food.position:
            if snake.length > 1:
                snake.length -= 1
                # Удаляем последний сегмент из списка позиций
                snake.positions.pop()
            else:
                # Если длина 1 и съели плохую еду — сбрасываем игру
                snake.reset()
                apple.randomize_position()
                bad_food.randomize_position()
                stone.randomize_position()
                continue
            bad_food.randomize_position()

        # Проверка на столкновение змейки с самой собой
        if head in snake.positions[1:]:
            snake.reset()
            apple.randomize_position()
            bad_food.randomize_position()
            stone.randomize_position()
            continue

        # Отрисовка
        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw(screen)
        apple.draw(screen)
        bad_food.draw(screen)
        stone.draw(screen)

        pygame.display.update()


if __name__ == "__main__":
    main()
