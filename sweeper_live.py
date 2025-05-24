from random import randint
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.style import Style
import keyboard
import time
import sys

# Define color styles
STYLE_DEFAULT = Style(color="default", bgcolor="default")
STYLE_BLUE = Style(color="default", bgcolor="blue")
STYLE_RED = Style(color="bright_red", bgcolor="red")
STYLE_REVEALED = Style(color="default", bgcolor="default")
STYLE_BOMB = Style(color="red", bgcolor="default")
STYLE_HIGHLIGHT = Style(reverse=True)  # Correct way to implement reverse video

def exit_game():
    keyboard.unhook_all()
    sys.stdout.write("\033[2J\033[H")  # ANSI escape codes to clear screen
    sys.stdout.flush()
    exit()

def printendarr(arr, bc):
    console = Console()
    buffer = []
    for row in arr:
        line = []
        for cell in row:
            if cell == bc:
                line.append(f"[{STYLE_BOMB}]#[/]")
            else:
                line.append(str(cell))
        buffer.append("".join(line))
    console.print("\n".join(buffer), end="")

def createnoise(arr, w, h, bt, bc, cx, cy):
    bombs_placed = 0
    while bombs_placed < bt:
        x, y = randint(0, w - 1), randint(0, h - 1)
        if arr[y][x] != bc and (x, y) != (cx, cy):
            canplace = True
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (cx + j == x) and (cy + i == y):
                        canplace = False
                        break
                if not canplace:
                    break
            if canplace:
                bombs_placed += 1
                arr[y][x] = bc
    return arr

def countbombs(arr, bc, ws):
    w, h = len(arr[0]), len(arr)
    for i in range(h):
        for j in range(w):
            if arr[i][j] == bc:
                continue
            count = 0
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if i + x < 0 or i + x >= h or j + y < 0 or j + y >= w:
                        continue
                    if arr[i + x][j + y] == bc:
                        count += 1
            if count != 0: 
                arr[i][j] = str(count)
            else: 
                arr[i][j] = ws
    return arr

def generate_display(maskedarr, sx, sy, flags, bt):
    grid = []
    for y in range(len(maskedarr)):
        row = []
        for x in range(len(maskedarr[y])):
            cell = maskedarr[y][x]
            
            # Determine base style
            if cell == "[default on blue] [/]":
                style = STYLE_BLUE
                content = " "
            elif cell == "[bright_red on red] [/]":
                style = STYLE_RED
                content = " "
            elif cell in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                style = STYLE_REVEALED
                content = cell
            elif cell == " ":
                style = STYLE_REVEALED
                content = " "
            else:
                style = STYLE_DEFAULT
                content = str(cell)
            
            # Apply highlight if this is the selected cell
            if (y, x) == (sy, sx):
                style += STYLE_HIGHLIGHT
            
            row.append(f"[{style}]{content}[/]")
        grid.append("".join(row))
    
    info = f"Flags: {flags}/{bt} | Arrow keys: Move | Z: Reveal | X: Flag | Q: Quit"
    return Panel("\n".join(grid), title="Minesweeper", subtitle=info)

def countflagsforcell(maskedarr, x, y, fc):
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue
            nx = x + dx
            ny = y + dy
            if 0 <= nx < len(maskedarr[0]) and 0 <= ny < len(maskedarr):
                if maskedarr[ny][nx] == fc:
                    count += 1
    return count

def click(arr, maskedarr, x, y, ws, w, h, mc, bc, fc):
    if maskedarr[y][x] == fc:
        return maskedarr, True
    if arr[y][x] == bc:
        return maskedarr, False
    elif arr[y][x] == ws and maskedarr[y][x] == mc:
        maskedarr[y][x] = ws
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + j < 0 or x + j >= w or y + i < 0 or y + i >= h:
                    continue
                if maskedarr[y + i][x + j] == mc:
                    maskedarr, _ = click(arr, maskedarr, x + j, y + i, ws, w, h, mc, bc, fc)
    elif isinstance(maskedarr[y][x], (int, str)) and str(arr[y][x]) == str(maskedarr[y][x]):
        if countflagsforcell(maskedarr, x, y, fc) == int(arr[y][x]):
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if maskedarr[ny][nx] == mc:
                            maskedarr, game = click(arr, maskedarr, nx, ny, ws, w, h, mc, bc, fc)
                            if not game:
                                return maskedarr, False
    else:
        maskedarr[y][x] = arr[y][x]
    return maskedarr, True

def flag(maskedarr, x, y, mc, fc, flags):
    if maskedarr[y][x] == mc:
        maskedarr[y][x] = fc
        flags += 1
    elif maskedarr[y][x] == fc:
        maskedarr[y][x] = mc
        flags -= 1
    return maskedarr, flags

def checkwin(arr, maskedarr, bc, w, h, mc, flag_char):
    for i in range(h): 
        for j in range(w):
            if arr[i][j] == bc and maskedarr[i][j] != flag_char:
                return False
            elif arr[i][j] != bc and maskedarr[i][j] == mc:
                return False
    return True 

def select(live, maskedarr, sx, sy, game, flags, bt):
    selected = False
    action = ""
    while not selected and game:
        live.update(generate_display(maskedarr, sx, sy, flags, bt))
        event = keyboard.read_event(suppress=True)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == "right" and sx < len(maskedarr[0]) - 1:
                sx += 1
            elif event.name == "left" and sx > 0:
                sx -= 1
            elif event.name == "down" and sy < len(maskedarr) - 1:
                sy += 1
            elif event.name == "up" and sy > 0:
                sy -= 1
            elif event.name == "z":
                action = "click"
                selected = True
            elif event.name == "x":
                action = "flag"
                selected = True
            elif event.name == "q":
                action = "quit"
                selected = True
    return action, sx, sy

def main(h, w, bt, bc, mc, ws, fc):
    console = Console()
    game = True
    sx, sy = 0, 0
    flags = 0
    maskedarr = [[mc for _ in range(w)] for _ in range(h)]
    
    with Live(refresh_per_second=20, transient=True) as live:
        action, sx, sy = select(live, maskedarr, sx, sy, game, flags, bt)
        cx, cy = sx, sy
        arr = [[ws for _ in range(w)] for _ in range(h)]
        arr = createnoise(arr, w, h, bt, bc, cx, cy)
        arr = countbombs(arr, bc, ws)

        if action == "click":
            maskedarr, game = click(arr, maskedarr, sx, sy, ws, w, h, mc, bc, fc)
        elif action == "flag":
            maskedarr, flags = flag(maskedarr, sx, sy, mc, fc, flags)
        elif action == "quit":
            exit_game()

        while game:
            if checkwin(arr, maskedarr, bc, w, h, mc, fc):
                live.update(generate_display(arr, -1, -1, flags, bt))
                console.print("\nYou win!")
                time.sleep(2)
                exit_game()
                
            if not game:
                live.update(generate_display(arr, -1, -1, flags, bt))
                console.print("\nGame Over")
                time.sleep(2)
                exit_game()
                
            action, sx, sy = select(live, maskedarr, sx, sy, game, flags, bt)
            if action == "click":
                maskedarr, game = click(arr, maskedarr, sx, sy, ws, w, h, mc, bc, fc)
            elif action == "flag":
                maskedarr, flags = flag(maskedarr, sx, sy, mc, fc, flags)
            elif action == "quit":
                exit_game()

def titlescreen():
    console = Console()
    selected = ""
    ind = 0
    difficulties = {
        "Beginner": (8, 8, 10), 
        "Intermediate": (16, 16, 40), 
        "Expert": (30, 16, 99), 
        "Custom": (0, 0, 0)
    }
    
    def generate_menu():
        menu_lines = [
            "Welcome to Minesweeper!",
            "Select difficulty:",
            *[
                f"[reverse]{i+1}. {name}[/]" if i == ind else f"{i+1}. {name}"
                for i, name in enumerate(difficulties)
            ],
            "\nArrow keys: Move | Enter: Select | Q: Quit"
        ]
        return Panel("\n".join(menu_lines), title="Minesweeper")
    
    with Live(refresh_per_second=10, transient=True) as live:
        while selected == "":
            live.update(generate_menu())
            event = keyboard.read_event(suppress=True)
            if event.event_type == keyboard.KEY_DOWN:
                if event.name == "down":
                    ind = min(ind + 1, len(difficulties) - 1)
                elif event.name == "up":
                    ind = max(ind - 1, 0)
                elif event.name == "q":
                    exit_game()
                elif event.name == "enter":
                    selected = list(difficulties.keys())[ind]
    
    console.print(f"You selected: {selected}")
    if selected == "Custom":
        w = int(console.input("Enter width: "))
        h = int(console.input("Enter height: "))
        bt = int(console.input("Enter bomb count: "))
    else:
        w, h, bt = difficulties[selected]
    
    main(h, w, bt, "#", "[default on blue] [/]", " ", "[bright_red on red] [/]")

if __name__ == "__main__":
    try:
        titlescreen()
    except KeyboardInterrupt:
        exit_game()