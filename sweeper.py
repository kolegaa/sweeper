import unicurses as uc
from random import randint

class MinesweeperGame:
    def __init__(self, width, height, bombs, stdscr):
        self.width = width
        self.height = height
        self.bombs = bombs
        self.stdscr = stdscr

        # Game characters
        self.BOMB = "#"
        self.MASKED = "."
        self.EMPTY = " "
        self.FLAG = "F"

        self.flags = 0
        self.game_over = False
        self.arr = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        self.masked = [[self.MASKED for _ in range(width)] for _ in range(height)]
        self.cursor_x = 0
        self.cursor_y = 0

    def setup(self, first_x, first_y):
        self.arr = [[self.EMPTY for _ in range(self.width)] for _ in range(self.height)]
        self.masked = [[self.MASKED for _ in range(self.width)] for _ in range(self.height)]
        self.flags = 0
        self.game_over = False
        self.place_bombs(first_x, first_y)
        self.count_bombs()

    def place_bombs(self, cx, cy):
        placed = 0
        while placed < self.bombs:
            x, y = randint(0, self.width - 1), randint(0, self.height - 1)
            if self.arr[y][x] != self.BOMB and (x, y) != (cx, cy):
                # Don't place bomb on first click or adjacent
                if not any((cx + dx, cy + dy) == (x, y) for dx in range(-1, 2) for dy in range(-1, 2)):
                    self.arr[y][x] = self.BOMB
                    placed += 1

    def count_bombs(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.arr[y][x] == self.BOMB:
                    continue
                count = sum(
                    1 for dx in range(-1, 2) for dy in range(-1, 2)
                    if 0 <= x + dx < self.width and 0 <= y + dy < self.height
                    and self.arr[y + dy][x + dx] == self.BOMB
                )
                self.arr[y][x] = count if count else self.EMPTY

    def draw(self, highlight_x=None, highlight_y=None):
        uc.clear()
        for y in range(self.height):
            for x in range(self.width):
                cell = self.masked[y][x]
                attr = 0
                if (x, y) == (highlight_x, highlight_y):
                    attr = uc.color_pair(2)
                elif cell == self.BOMB:
                    attr = uc.color_pair(1)
                elif cell == self.FLAG:
                    attr = uc.color_pair(3)
                elif isinstance(cell, int):
                    attr = uc.color_pair(cell + 3)
                uc.mvaddstr(y, x, str(cell), attr)  # y, x order is correct for curses
        uc.refresh()

    def reveal(self, x, y):
        if self.masked[y][x] == self.FLAG:
            return True
        if self.arr[y][x] == self.BOMB:
            self.show_end_screen("Game Over! Press any key to exit")
            return False
        self._reveal_recursive(x, y)
        return True

    def _reveal_recursive(self, x, y):
        if self.masked[y][x] != self.MASKED:
            return
        self.masked[y][x] = self.arr[y][x]
        if self.arr[y][x] == self.EMPTY:
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        self._reveal_recursive(nx, ny)

    def toggle_flag(self, x, y):
        if self.masked[y][x] == self.MASKED:
            self.masked[y][x] = self.FLAG
            self.flags += 1
        elif self.masked[y][x] == self.FLAG:
            self.masked[y][x] = self.MASKED
            self.flags -= 1

    def check_win(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.arr[y][x] == self.BOMB and self.masked[y][x] != self.FLAG:
                    return False
                if self.arr[y][x] != self.BOMB and self.masked[y][x] == self.MASKED:
                    return False
        return True

    def show_end_screen(self, message):
        # Reveal all spaces when game is lost
        for y in range(self.height):
            for x in range(self.width):
                self.masked[y][x] = self.arr[y][x]
        
        self.draw()
        uc.mvaddstr(self.height + 1, 0, message)
        uc.refresh()
        uc.getch()
        self.game_over = True

    def play(self):
        self.cursor_x, self.cursor_y = 0, 0
        first_move = True
        while not self.game_over:
            self.draw(self.cursor_x, self.cursor_y)
            key = uc.wgetch(self.stdscr)
            # Move right
            if key in (uc.KEY_RIGHT, 261, 454, ord('d'), ord('l')) and self.cursor_x < self.width - 1:
                self.cursor_x += 1
            # Move left
            elif key in (uc.KEY_LEFT, 260, 452, ord('a'), ord('h')) and self.cursor_x > 0:
                self.cursor_x -= 1
            # Move down
            elif key in (uc.KEY_DOWN, 258, 456, ord('s'), ord('j')) and self.cursor_y < self.height - 1:
                self.cursor_y += 1
            # Move up
            elif key in (uc.KEY_UP, 259, 450, ord('w'), ord('k')) and self.cursor_y > 0:
                self.cursor_y -= 1
            elif key == ord('z'):
                if first_move:
                    self.setup(self.cursor_x, self.cursor_y)
                    first_move = False
                if not self.reveal(self.cursor_x, self.cursor_y):
                    break
                if self.check_win():
                    self.show_end_screen("You win! Press any key to exit")
                    break
            elif key == ord('x'):
                self.toggle_flag(self.cursor_x, self.cursor_y)
            elif key == ord('q'):
                exit_game()
            else:
                uc.mvaddstr(self.height + 2, 0, f"KEY: {key}   ")  # Show key code at bottom
                uc.refresh()

def exit_game():
    uc.endwin()
    exit()

def init_colors():
    uc.start_color()
    uc.init_pair(1, uc.COLOR_RED, uc.COLOR_BLACK)      # Bomb
    uc.init_pair(2, uc.COLOR_BLACK, uc.COLOR_WHITE)    # Cursor
    uc.init_pair(3, uc.COLOR_RED, uc.COLOR_BLACK)      # Flag
    for i in range(1, 9):
        uc.init_pair(3 + i, i, uc.COLOR_BLACK)         # Numbers

def titlescreen(stdscr):
    uc.clear()
    uc.mvaddstr(0, 0, "Welcome to Minesweeper!")
    uc.mvaddstr(1, 0, "Select difficulty")
    difficulties = {
        "Beginner": (8, 8, 10),
        "Intermediate": (16, 16, 40),
        "Expert": (30, 16, 99),
        "Custom": (0, 0, 0)
    }
    keys = list(difficulties.keys())
    ind = 0

    while True:
        for i, name in enumerate(keys):
            attr = uc.A_REVERSE if i == ind else 0
            uc.mvaddstr(i + 2, 0, f"{i + 1}. {name}", attr)
        uc.refresh()
        key = uc.wgetch(stdscr)
        if key in (uc.KEY_DOWN, 258, 456, ord('s'), ord('j')) and ind < len(keys) - 1:
            ind += 1
        elif key in (uc.KEY_UP, 259, 450, ord('w'), ord('k')) and ind > 0:
            ind -= 1
        elif key == ord('q'):
            exit_game()
        elif key == 10:  # Enter
            selected = keys[ind]
            break

    uc.clear()
    uc.mvaddstr(0, 0, f"You selected: {selected}")
    uc.refresh()

    if selected == "Custom":
        uc.mvaddstr(1, 0, "Enter width: ")
        uc.echo()
        w = int(uc.getstr(1, 12).decode('utf-8'))
        uc.mvaddstr(2, 0, "Enter height: ")
        h = int(uc.getstr(2, 13).decode('utf-8'))
        uc.mvaddstr(3, 0, "Enter bomb count: ")
        bt = int(uc.getstr(3, 17).decode('utf-8'))
        uc.noecho()
    else:
        w, h, bt = difficulties[selected]

    init_colors()
    return w, h, bt

def mainloop(stdscr):
    while True:
        w, h, bt = titlescreen(stdscr)
        game = MinesweeperGame(w, h, bt, stdscr)
        game.play()
        uc.clear()
        uc.mvaddstr(0, 0, "Press Q to quit or any other key to play again")
        uc.refresh()
        key = uc.wgetch(stdscr)
        if key == ord('q'):
            break

if __name__ == "__main__":
    stdscr = uc.initscr()
    uc.noecho()
    uc.cbreak()
    uc.keypad(stdscr, True)
    uc.curs_set(0)
    if uc.has_colors():
        uc.start_color()
    try:
        mainloop(stdscr)
    finally:
        exit_game()