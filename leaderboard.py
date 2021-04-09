import sqlite3
import pygame
import sys
import datetime
from scripts import load_image, print_text_from_center, Button


class LeaderBoard:
    def __init__(self, GameName: str, TableStructure: dict):
        self.gamename = GameName
        if TableStructure != dict():
            SqliteRequest = []
            TypesDict = {int: "INTEGER", str: "STRING", bool: "BOOL",
                         datetime.datetime: "DATETIME", datetime.time: "TIME", datetime.date: "DATE"}
            for k, v in TableStructure.items():
                SqliteRequest.append(f"{k} {TypesDict.get(v, '')}")
            self.Values = ", ".join(SqliteRequest)
            with sqlite3.connect("leaderboard.db") as connection:
                cursor = connection.cursor()
                cursor.execute(f"""CREATE TABLE IF NOT EXISTS {GameName} ({self.Values})""")
                connection.commit()

    def AddRecord(self, *values):
        with sqlite3.connect("leaderboard.db") as connection:
            cursor = connection.cursor()
            cursor.execute(fr"""INSERT INTO {self.gamename} VALUES {values}""".replace('"', ""))

    def _GetRecords(self):
        with sqlite3.connect("leaderboard.db") as connection:
            cursor = connection.cursor()
            return cursor.execute(f"""SELECT * FROM {self.gamename}""").fetchall()


class Board:
    def __init__(self, width: int, height: int, columns: int, rows: int):
        # значения по умолчанию
        self.left = 40
        self.top = 40
        self.size_y = 20
        self.cur_y = 0
        self.width = width
        self.height = height

        self.MousePos = pygame.mouse.get_pos()
        self.ClickInScrollbarRect = False

    def SetValues(self, width: int, height: int, values: list, columns: int, rows: int):
        self.width = width
        self.height = height
        self.columns = columns
        self.rows = rows
        rows += 1
        self.board = [[""] * columns for _ in range(rows)]
        self.fullheight = rows * self.size_y
        self.size_x = (self.width // columns)
        self.screen = pygame.Surface((self.width, self.fullheight))
        self.cur_y = 0
        values = [list(map(str, values[i])) for i in range(len(values))]
        for i in range(min(len(self.board), len(values))):
            self.board[i] = values[i]
        self.Redraw()

    def Render(self, screen: pygame.Surface, redraw=False):
        if redraw:
            self.Redraw()
        drawrect = pygame.Rect(0, self.cur_y, self.width, self.height)
        scrollbar_x = self.left + self.width + self.size_y
        pygame.draw.rect(screen, (170, 170, 170),
                         (scrollbar_x, self.top, self.size_y, self.height))
        scrollbar_height = self.size_y * 4

        LMBClicked = pygame.mouse.get_pressed()[0] == 1

        MousePos = pygame.mouse.get_pos()
        MouseDelta = 0, 0
        if LMBClicked and self.ClickInScrollbarRect:
            MouseDelta = MousePos[0] - self.MousePos[0], MousePos[1] - self.MousePos[1]
        else:
            self.ClickInScrollbarRect = False
        self.MousePos = MousePos
        ScrollBarColor = (140, 140, 140)

        ScrollBarPosY = int(self.top + self.height * self.cur_y / self.fullheight)
        ScrollBarPosYMax = int(self.top + self.height - scrollbar_height)

        self.cur_y = max(min(self.cur_y + self.fullheight * (MouseDelta[1] / self.height), self.fullheight), 0)

        ScrollBarRect = (scrollbar_x, min(ScrollBarPosY, ScrollBarPosYMax), self.size_y, scrollbar_height)

        if LMBClicked and ScrollBarRect[0] <= MousePos[0] <= ScrollBarRect[0] + ScrollBarRect[2] and \
                ScrollBarRect[1] <= MousePos[1] <= ScrollBarRect[1] + ScrollBarRect[3]:
            self.ClickInScrollbarRect = True
            ScrollBarColor = (120, 120, 120)

        pygame.draw.rect(screen, ScrollBarColor, ScrollBarRect)
        screen.blit(self.screen, (self.left, self.top), drawrect)

    def Redraw(self):
        self.screen.fill((150, 150, 150))
        cur_y = 0
        cur_x = 0
        for j in range(self.columns):
            pygame.draw.rect(self.screen, (120, 120, 120), (cur_x, cur_y, self.size_x, self.size_y))
            pygame.draw.rect(self.screen, (0, 0, 0), (cur_x, cur_y, self.size_x, self.size_y), 1)
            print_text_from_center(self.board[0][j], cur_x + self.size_x // 2, cur_y + self.size_y // 2,
                                   self.screen, pygame, self.size_y - self.size_y // 10)
            cur_x += self.size_x
        cur_y += self.size_y
        for i in range(self.rows):
            cur_x = 0
            for j in range(self.columns):
                pygame.draw.rect(self.screen, (150, 150, 150), (cur_x, cur_y, self.size_x, self.size_y))
                pygame.draw.rect(self.screen, (0, 0, 0), (cur_x, cur_y, self.size_x, self.size_y), 1)
                print_text_from_center(self.board[i + 1][j], cur_x + self.size_x // 2, cur_y + self.size_y // 2,
                                       self.screen, pygame, self.size_y - self.size_y // 10)
                cur_x += self.size_x
            cur_y += self.size_y

    def ScrollDown(self):
        self.cur_y = min(self.cur_y + 10, self.rows * self.size_y)

    def ScrollUp(self):
        self.cur_y = max(self.cur_y - 10, 0)

    def _GetRenderHeight(self) -> int:
        return min(self.rows * self.size_y, self.height)


class LeaderBoardWindow(LeaderBoard):
    def __init__(self, screen_size=(1024, 768)):
        super().__init__("", dict())
        self.FPS = 60
        self.WIDTH, self.HEIGHT = screen_size
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Сборник игр: Таблица рекордов")
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        self.close_button_icon = load_image("data/close_button.png", pygame)
        self.left_button_icon = load_image("data/ArrowLeft.png", pygame)
        self.right_button_icon = load_image("data/ArrowRight.png", pygame)
        self.goto_menu = Button(100, 100, self.screen, pygame, active_clr=(255, 0, 0))
        self.next_game = Button(100, 100, self.screen, pygame)
        self.previous_game = Button(100, 100, self.screen, pygame)
        self.clock = pygame.time.Clock()
        with sqlite3.connect("leaderboard.db") as connection:
            cursor = connection.cursor()
            self.games = cursor.execute("""SELECT name FROM sqlite_master WHERE type='table';""").fetchall()
            self.currentgame = 0
            if len(self.games) > 0:
                self.gamename = self.games[self.currentgame][0]
                self.records = self._GetRecords()
                if len(self.records) > 0:
                    rows = len(self.records)
                    columns = len(self.records[0])
                    self.Board = Board(self.WIDTH - 80, min(rows * 20, 550), columns, rows)
                    self._SetNewGame()

    def StartRender(self):
        self._MainLoop()

    def _MainLoop(self):
        goto_menu_coords = 890, 640
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:
                        self.Board.ScrollUp()
                    elif event.button == 5:
                        self.Board.ScrollDown()

            self.screen.fill((187, 187, 187))

            goto_menu_coords = self.WIDTH - 100 * 1.5, self.HEIGHT - 100 * 1.2
            if self.goto_menu.draw(goto_menu_coords, image=self.close_button_icon, font_size=70, cmd="close"):
                return True

            if len(self.games) > 0:
                if len(self.records) > 0:
                    self.Board.Render(self.screen, False)
                    NextButtonCoords = self.WIDTH // 2 - 100 * 1.2, self.HEIGHT - 100 * 1.2
                    PreviousButtonCoords = self.WIDTH // 2 + 100 * 0.2, self.HEIGHT - 100 * 1.2
                    if len(self.games) > 1:
                        if self.next_game.draw(NextButtonCoords, image=self.left_button_icon, cmd=True):
                            self.currentgame = (self.currentgame + 1) % len(self.games)
                            self._SetNewGame()
                        elif self.previous_game.draw(PreviousButtonCoords, image=self.right_button_icon, cmd=True):
                            self.currentgame = (self.currentgame - 1) % len(self.games)
                            self._SetNewGame()
                else:
                    print_text_from_center("В данной игре у вас еще нет рекордов!", self.WIDTH // 2, self.HEIGHT // 2,
                                           self.screen, pygame, 50)
            else:
                print_text_from_center("Нет данных для отображения", self.WIDTH // 2, self.HEIGHT // 2,
                                       self.screen, pygame, 50)
            self.clock.tick(self.FPS)
            pygame.display.flip()

    def _SetNewGame(self):
        with sqlite3.connect("leaderboard.db") as connection:
            self.gamename = self.games[self.currentgame][0]
            cursor = connection.cursor()
            self.records = self._GetRecords()
            if len(self.records) > 0:
                cursor.execute(f"select * from {self.gamename}")
                names = [description[0] for description in cursor.description]
                rows = len(self.records)
                columns = len(self.records[0])
                self.Board.SetValues(self.WIDTH - 80, min((rows + 1) * 20, 550), [names] + self.records, columns, rows)


def open_leaderboard(pygame, screen_size):
    board = LeaderBoardWindow(screen_size)
    board.StartRender()
    return 1


if __name__ == "__main__":
    pygame.init()
    board = LeaderBoardWindow()
    board.StartRender()
    # board.AddRecord(123, "hello world")
