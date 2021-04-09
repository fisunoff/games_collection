import pygame
import sys
from scripts import load_image, Button, music
import flappy_bird
import minesweeper
import leaderboard

FPS = 50
BASEWIDTH, BASEHEIGHT = 1024, 768
size = width, height = 1024, 768
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Сборник игр: главное меню")
clock = pygame.time.Clock()

sound_on = load_image("data/unmute.png", pygame)
sound_off = load_image("data/mute.png", pygame)
music_on = (sound_on, (30, 683), True)

SCREEN_SIZES = [[1024, 768], [800, 600]]
SCREEN_SIZES_LETTERS = ["S", "B"]


def resize_main():
    """Перерасчет положения кнопок при изменении размера окна"""
    start_flappy_bird_coordinates = (200 / BASEWIDTH) * width, (200 / BASEWIDTH) * width
    start_minesweeper_coordinates = (700 / BASEWIDTH) * width, (200 / BASEWIDTH) * width
    quit_button_coordinates = (450 / BASEWIDTH) * width, (500 / BASEWIDTH) * width
    music_button_coordinates = (10 / BASEWIDTH) * width, (658 / BASEWIDTH) * width
    screen_size_button_coordinates = (150 / BASEWIDTH) * width, (658 / BASEWIDTH) * width
    leaderboard_button_coordinates = (400 / BASEWIDTH) * width, (380 / BASEWIDTH) * width
    return start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    """Стартовый экран(главное меню)"""
    global music_on, screen, size, width, height, BASEWIDTH, BASEWIDTH

    intro_text = ["СБОРНИК ИГР", "",
                  "Flappy bird,",
                  "Сапер,",
                  "Морской бой"]
    # Фон и постоянный текст
    background = pygame.transform.scale(load_image('data/menu_image.jpg', pygame), (width, height))
    screen.blit(background, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 30
    for line in intro_text:
        string_rendered = font.render(line, True, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    # Кнопки
    start_flappy_bird = Button(300, 70, screen, pygame)
    start_minesweeper = Button(170, 70, screen, pygame)
    quit_button = Button(200, 70, screen, pygame, active_clr=(255, 0, 0))
    music_button = Button(100, 100, screen, pygame)
    screen_size_button = Button(100, 100, screen, pygame)
    leaderboard_button = Button(300, 70, screen, pygame)

    start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates = resize_main()

    size_counter = 2
    size_counter2 = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.VIDEORESIZE:
                size = width, height = event.w, event.h

                if width < 800 or height < 600:
                    screen = pygame.display.set_mode((800, 600))
                    width, height = 800, 600
                background = pygame.transform.scale(background, (width, height))
                start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates = resize_main()

        screen.blit(background, (0, 0))
        try:
            music_on_local_flappy = start_flappy_bird.draw(start_flappy_bird_coordinates, "Flappy bird",
                                                           action=flappy_bird.flappy_bird,
                                                           font_size=70, args=(music_on, size_counter))
            if music_on_local_flappy:
                size_counter = music_on_local_flappy[1]
                width, height = SCREEN_SIZES[size_counter % 2]
                screen = pygame.display.set_mode((width, height))
                background = pygame.transform.scale(background, (width, height))
                start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates = resize_main()
                pygame.display.set_caption("Сборник игр: главное меню")

                if music_on[2] != music_on_local_flappy[0][2]:
                    music_on = music(music_on, pygame, sound_on, sound_off)

            music_on_local_minesweeper = start_minesweeper.draw(start_minesweeper_coordinates, "Сапер",
                                                                action=minesweeper.minesweeper, font_size=70,
                                                                args=(music_on, size_counter))
            if music_on_local_minesweeper:
                size_counter = music_on_local_minesweeper[1]
                size_counter = music_on_local_minesweeper[1]
                width, height = SCREEN_SIZES[size_counter % 2]
                screen = pygame.display.set_mode((width, height))
                background = pygame.transform.scale(background, (width, height))
                start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates = resize_main()
                pygame.display.set_caption("Сборник игр: главное меню")
                if music_on[2] != music_on_local_minesweeper[0][2]:
                    music_on = music(music_on, pygame, sound_on, sound_off)
        except Exception as e:
            print("Unknown Error. Write to developers.", e)

        quit_button.draw(quit_button_coordinates, "Выход", action=terminate, font_size=70)
        music_on = music_button.draw(music_button_coordinates, image=music_on[0], action=music, font_size=70,
                                     cmd=True, args=(music_on, pygame, sound_on, sound_off)) or music_on

        sz_s = screen_size_button.draw(screen_size_button_coordinates, SCREEN_SIZES_LETTERS[size_counter % 2],
                                       action=pygame.display.set_mode,
                                       args=(SCREEN_SIZES[size_counter % 2],))

        # обработка нажатия на кнопку изменения размера экрана
        if sz_s:
            if size_counter2 % 2 == 0:
                size_counter += 1
                width, height = SCREEN_SIZES[size_counter % 2]
                screen = pygame.display.set_mode((width, height))
                background = pygame.transform.scale(background, (width, height))
                start_flappy_bird_coordinates, start_minesweeper_coordinates, quit_button_coordinates, music_button_coordinates, screen_size_button_coordinates, leaderboard_button_coordinates = resize_main()

        lb = leaderboard_button.draw(leaderboard_button_coordinates, "Лидерборд", font_size=70,
                                     action=leaderboard.open_leaderboard, args=(pygame, SCREEN_SIZES[size_counter % 2]))
        # Если вернулись из лидерборда, то меняем название окна обратно
        if lb:
            pygame.display.set_caption("Сборник игр: главное меню")

        pygame.display.flip()
        clock.tick(60)
        clock.tick(FPS)


if __name__ == '__main__':

    pygame.init()

    pygame.mixer.music.load('data/8bit-background_main.mp3')
    pygame.mixer.music.set_volume(0.2)
    pygame.mixer.music.play(-1)

    screen = pygame.display.set_mode(size)
    pygame.display.flip()
    start_screen()
    while pygame.event.wait().type != pygame.QUIT:
        pass
    pygame.quit()
