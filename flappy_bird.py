import pygame
import sys
from scripts import load_image, Button, print_text, to_main_menu_button, pause_button_func, music, play_again_button
import random
import time
from leaderboard import LeaderBoard
import datetime
import os

clock = pygame.time.Clock()

bird_colour_list = ["red", "yellow", "blue"]
pipe_colour_list = ["green", "red"]
SCREEN_SIZES = [[1024, 768], [800, 600]]
SCREEN_SIZES_LETTERS = ["S", "B"]
kill_event = pygame.event.Event(pygame.KEYUP, key=pygame.K_r)


def pause_logo(if_playing, play_button, pause_button):
    if if_playing:
        return play_button, (135, 5)
    else:
        return pause_button, (135, 5)


def draw_floor(floor_pos, screen, base, pause=False):
    """Движущуяся полоса внизу экрана"""
    if not pause:
        floor_pos -= calc_x(6 * 60 // FPS)
    screen.blit(base, (floor_pos, calc_y(705)))
    screen.blit(base, (floor_pos + calc_x(1024), calc_y(705)))
    if floor_pos <= calc_x(-1024):
        floor_pos = 0
    return floor_pos


counter = 0
FPS = 30
BASEWIDTH, BASEHEIGHT = 1024, 768
width, height = 1024, 768
IF_PLAYING = True
RESTARTINGTICK = 4000
bird_sprite = pygame.sprite.Group()
floor_sprite = pygame.sprite.Group()
pipe_sprites = pygame.sprite.Group()

sound_on = load_image("data/unmute.png", pygame)
sound_off = load_image("data/mute.png", pygame)

pipe_down_skins = {"green": load_image("data/flappy_bird/pipes/green/pipe-down.png", pygame),
                   "red": load_image("data/flappy_bird/pipes/red/pipe-down.png", pygame)}
pipe_up_skins = {"green": load_image("data/flappy_bird/pipes/green/pipe-up.png", pygame),
                 "red": load_image("data/flappy_bird/pipes/red/pipe-up.png", pygame)}

bird_down_skins = {"blue": load_image("data/flappy_bird/bird/blue/bird-midflap.png", pygame),
                   "red": load_image("data/flappy_bird/bird/red/bird-midflap.png", pygame),
                   "yellow": load_image("data/flappy_bird/bird/yellow/bird-midflap.png", pygame)}
bird_up_skins = {"blue": load_image("data/flappy_bird/bird/blue/bird-upflap.png", pygame),
                 "red": load_image("data/flappy_bird/bird/red/bird-upflap.png", pygame),
                 "yellow": load_image("data/flappy_bird/bird/yellow/bird-upflap.png", pygame)}


def calc_x(value: int) -> int:
    """Перерасчет координат по оси X"""
    return int((value / BASEWIDTH) * width)


def calc_y(value: int) -> int:
    """Перерасчет координат по оси Y"""
    return int((value / BASEHEIGHT) * height)


def restart_skins():
    """Случайный выбор скинов труб и птицы"""
    global pipe_up, pipe_down, bird_down, bird_up

    bird_colour = random.choice(bird_colour_list)
    pipe_colour = random.choice(pipe_colour_list)

    bird_down = bird_down_skins[bird_colour]
    bird_up = bird_up_skins[bird_colour]
    pipe_down = pipe_down_skins[pipe_colour]
    pipe_up = pipe_up_skins[pipe_colour]


def resize_flappy():
    """Перерасчет положения кнопок при изменении размера окна"""
    play_again_coordinates = calc_x(270), calc_y(10)
    pause_local_coordinates = calc_x(140), calc_y(10)
    to_main_menu_local_coordinates = calc_x(10), calc_y(10)
    music_button_coordinates = calc_x(10), calc_y(658)
    screen_size_button_coordinates = calc_x(150), calc_y(658)
    return (play_again_coordinates, pause_local_coordinates, to_main_menu_local_coordinates,
            music_button_coordinates, screen_size_button_coordinates)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x=calc_x(1000), y=calc_y(300), place="bottom"):
        super().__init__(pipe_sprites)
        self.gened_next = False
        self.place = place
        if place == "bottom":
            self.image = pipe_down
            self.rect = pipe_down.get_rect()
            self.rect.x = x
            self.rect.y = height - y
        if place == "top":
            self.generated = False
            self.image = pipe_up
            self.rect = pipe_up.get_rect()
            self.rect.x = x
            self.rect.y = height - y - calc_y(200) - 626

    def update(self, arg=None):
        self.rect = self.rect.move(calc_x(-6) / FPS * 60, 0)
        global counter
        if self.rect[0] < 0 or arg == "kill":
            self.kill()
        if calc_x(95) < self.rect[0] < calc_x(105) and self.place == "top":
            counter += 1
        elif self.rect[0] <= calc_x(400) and self.place == "top" and not self.generated:
            self.generated = True
            y = calc_y(random.randint(100, 300))
            Pipe(x=calc_x(1000), y=y, place="bottom")
            Pipe(x=calc_x(1000), y=y, place="top")


class Border(pygame.sprite.Sprite):
    # строго вертикальный или строго горизонтальный отрезок
    def __init__(self, x1, y1, x2, y2):
        super().__init__(floor_sprite)
        if x1 == x2:  # вертикальная стенка
            self.add(floor_sprite)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.add(floor_sprite)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)

    def set_coordinates(self, x1, y1, x2, y2):
        if x1 == x2:  # вертикальная стенка
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:  # горизонтальная стенка
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Bird(pygame.sprite.Sprite):
    def __init__(self, screen, radius=30, x=100, y=400):
        super().__init__(bird_sprite)
        self.radius = radius
        self.x = x
        self.y = y
        self.last_jump_time = time.time()
        self.jumped = False
        self.image = bird_down
        self.rect = bird_down.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.vy = 3 / FPS * 60
        self.screen = screen
        self.lb = LeaderBoard("flappybird",
                              {"Nick": str, "Playing date": datetime.datetime, "Score": str})

    def update(self, *args):
        if IF_PLAYING:
            self.rect = self.rect.move(0, self.vy)
            self.y += self.vy
            if self.jumped:
                if time.time() - self.last_jump_time > 0.5:
                    self.image = bird_down
                    self.rect = bird_down.get_rect()
                    self.rect.x = self.x
                    self.rect.y = self.y
                    self.jumped = False
                    self.last_jump_time = time.time()

        if args:
            if "kill" in args:
                self.kill()
            if "reset" in args:
                self.x = 100
                self.y = 400
                self.image = bird_down
                self.rect = bird_down.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y
            if IF_PLAYING:
                self.y -= 50
                self.image = bird_up
                self.rect = bird_up.get_rect()
                self.rect.x = self.x
                self.rect.y = self.y
                self.jumped = True

        if pygame.sprite.spritecollideany(self, floor_sprite) or pygame.sprite.spritecollideany(self, pipe_sprites):
            global counter
            if os.name == "posix":
                nick = os.environ.get("USER")
            else:
                nick = os.environ.get("USERNAME")
            self.lb.AddRecord(nick, "datetime('now', '+3 hours')", counter)
            pygame.event.post(kill_event)
            print("Game over")


def flappy_bird(music_on_imported, size_counter=1):
    """Запуск игры Flappy bird"""
    global bird_sprite, floor_sprite, pipe_sprites, IF_PLAYING, RESTARTINGTICK, counter
    global width, height
    restart_skins()

    btns_top_coords = (0, 260), (0, 130)
    btns_floor_coords = [(0, 120), (650, 768)]

    close_button = load_image("data/close_button.png", pygame)
    pause_button = load_image("data/pause_button.png", pygame)
    play_button = load_image("data/play_button.png", pygame)
    restart_button = load_image("data/restart_button.png", pygame)

    music_on = sound_on, (30, 683), True
    if music_on_imported[2] != music_on[2]:
        music_on = music(music_on, pygame, sound_on, sound_off)

    bird_sprite = pygame.sprite.Group()
    floor_sprite = pygame.sprite.Group()
    pipe_sprites = pygame.sprite.Group()

    width, height = SCREEN_SIZES[size_counter % 2]

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Сборник игр: Flappy bird")
    background = pygame.transform.scale(load_image('data/flappy_bird/background.png', pygame), (width, height))
    base = pygame.transform.scale(load_image('data/flappy_bird/base.png', pygame), (calc_x(1024), calc_y(70)))

    floor_x_pos = 0
    Bird(screen)

    # Границы экрана, соприкасаясь с которыми, Bird умирает
    x5, y5 = calc_x(5), calc_y(5)

    b1 = Border(x5, y5, width - x5, y5)
    b2 = Border(calc_x(70), height - calc_y(70), width - calc_x(70), height - calc_y(70))
    b3 = Border(x5, y5, x5, height - y5)
    b4 = Border(width - x5, y5, width - x5, height - y5)

    # Кнопки
    to_main_menu_local = to_main_menu_button(screen, pygame)
    pause_local = pause_button_func(screen, pygame)
    music_button = Button(100, 100, screen, pygame)
    play_again_btn = play_again_button(screen, pygame)
    screen_size_button = Button(100, 100, screen, pygame)

    # Счетчик очков (пройденных труб)
    counter = 0

    # Генерация трубы. Далее она сама генерирует следующую
    y = calc_y(random.randint(100, 300))
    Pipe(y=y, place="bottom")
    Pipe(y=y, place="top")

    # Пересчет координат кнопок под размер экрана
    play_again_coordinates, pause_local_coordinates, to_main_menu_local_coordinates, music_button_coordinates, screen_size_button_coordinates = resize_flappy()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not (btns_floor_coords[0][0] < event.pos[0] < btns_floor_coords[0][1] and btns_floor_coords[1][0] <
                        event.pos[1] < btns_floor_coords[1][1]) \
                        and not (
                        btns_top_coords[0][0] < event.pos[0] < btns_top_coords[0][1] and btns_top_coords[1][0] <
                        event.pos[1] < btns_top_coords[1][1]):
                    if IF_PLAYING and RESTARTINGTICK >= 4000:
                        bird_sprite.update(event)
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                play_again_coordinates, pause_local_coordinates, to_main_menu_local_coordinates, music_button_coordinates, screen_size_button_coordinates = resize_flappy()
                background = pygame.transform.scale(background, (width, height))

                b1.set_coordinates(x5, y5, width - x5, y5)
                b2.set_coordinates(calc_x(70), height - calc_y(70), width - calc_x(70), height - calc_y(70))
                b3.set_coordinates(x5, y5, x5, height - y5)
                b4.set_coordinates(width - x5, y5, width - x5, height - y5)
            elif pygame.key.get_pressed()[pygame.K_r] or event == kill_event:
                # Перезапуск игры
                RESTARTINGTICK = 0
                IF_PLAYING = True
                restart_skins()
                pipe_sprites.update("kill")
                bird_sprite.update("reset")
                y = calc_y(random.randint(100, 300))
                Pipe(y=y, place="bottom")
                Pipe(y=y, place="top")
                counter = 0

        pygame.display.update()
        screen.blit(background, (0, 0))
        bird_sprite.draw(screen)
        pipe_sprites.draw(screen)

        # Отрисовка кнопок
        if to_main_menu_local.draw(to_main_menu_local_coordinates, image=close_button, font_size=70, cmd="close"):
            bird_sprite.update("kill")
            return music_on, size_counter

        if pause_local.draw(pause_local_coordinates, image=pause_button if IF_PLAYING else play_button, font_size=70,
                            cmd="pause"):
            IF_PLAYING = not IF_PLAYING

        if play_again_btn.draw(play_again_coordinates, image=restart_button, font_size=70, cmd="again"):
            pygame.event.post(kill_event)

        if RESTARTINGTICK < 4000:
            print_text(f"{int(3999 - RESTARTINGTICK) // 1000}", width // 2, height // 2, screen=screen, pygame=pygame,
                       font_size=100)
        else:
            if IF_PLAYING:
                bird_sprite.update()
                pipe_sprites.update()
                floor_x_pos = draw_floor(floor_x_pos, screen, base)  # перемещение пола
            else:
                floor_x_pos = draw_floor(floor_x_pos, screen, base, pause=True)
        print_text("0" if counter < 0 else str(counter), calc_x(450), calc_y(50), screen=screen, pygame=pygame,
                   font_size=calc_y(100))

        a = music_button.draw(music_button_coordinates, image=music_on[0], action=music, font_size=calc_y(70),
                              args=(music_on, pygame, sound_on, sound_off))
        if a:
            # Если была нажата кнопка звука, обновляем его состояние
            music_on = a

        sz_s = screen_size_button.draw(screen_size_button_coordinates, SCREEN_SIZES_LETTERS[size_counter % 2],
                                       action=pygame.display.set_mode,
                                       args=(SCREEN_SIZES[size_counter % 2],))
        if sz_s:
            size_counter += 1
            width, height = SCREEN_SIZES[size_counter % 2]
            screen = pygame.display.set_mode((width, height))
            background = pygame.transform.scale(background, (width, height))
            base = pygame.transform.scale(base, (calc_x(1024), calc_y(70)))
            play_again_coordinates, pause_local_coordinates, to_main_menu_local_coordinates, music_button_coordinates, screen_size_button_coordinates = resize_flappy()
            b1.set_coordinates(x5, y5, width - x5, y5)
            b2.set_coordinates(calc_x(70), height - calc_y(70), width - calc_x(70), height - calc_y(70))
            b3.set_coordinates(x5, y5, x5, height - y5)
            b4.set_coordinates(width - x5, y5, width - x5, height - y5)

        a = clock.tick(FPS)
        RESTARTINGTICK += a if RESTARTINGTICK < 4000 else 0


if __name__ == '__main__':
    pygame.init()
    flappy_bird((sound_on, (30, 683)), 1)
