from random import randint
import unicurses as uc

def exit_game():
    uc.endwin()
    exit()

def printendarr(arr, bc, stdscr):
    uc.clear()
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j] == bc:
                uc.mvaddstr(i, j, str(arr[i][j]), uc.color_pair(1))
            else:
                uc.mvaddstr(i, j, str(arr[i][j]))
    uc.refresh()

def createnoise(arr, w, h, bt, bc, cx, cy):
    bombs_placed = 0
    while bombs_placed < bt:
        x, y = randint(0, w - 1), randint(0, h - 1)
        if arr[y][x] != bc and (x,y) != (cx,cy):
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
            if count != 0: arr[i][j] = count
            else: arr[i][j] = ws
    return arr

def printarr(arr, sx, sy, stdscr):
    uc.clear()
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if (i,j) == (sy,sx):
                uc.mvaddstr(i, j, str(arr[i][j]), uc.color_pair(2))
            elif arr[i][j] == '#':  # Bomb
                uc.mvaddstr(i, j, str(arr[i][j]), uc.color_pair(1))
            elif arr[i][j] == 'F':  # Flag
                uc.mvaddstr(i, j, str(arr[i][j]), uc.color_pair(3))
            elif isinstance(arr[i][j], int):  # Numbers
                uc.mvaddstr(i, j, str(arr[i][j]), uc.color_pair(arr[i][j] + 3))
            else:
                uc.mvaddstr(i, j, str(arr[i][j]))
    uc.refresh()

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

def click(arr, maskedarr, x, y, ws, w, h, mc, bc, fc, stdscr):
    if maskedarr[y][x] == fc:
        return maskedarr, True
    if arr[y][x] == bc:
        printendarr(arr, bc, stdscr)
        uc.mvaddstr(h+1, 0, "Game Over! Press any key to exit")
        uc.refresh()
        uc.getch()
        return maskedarr, False
    elif arr[y][x] == ws and maskedarr[y][x] == mc:
        maskedarr[y][x] = ws
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + j < 0 or x + j >= w or y + i < 0 or y + i >= h:
                    continue
                if maskedarr[y + i][x + j] == mc:
                    maskedarr, _ = click(arr, maskedarr, x + j, y + i, ws, w, h, mc, bc, fc, stdscr)
    elif isinstance(maskedarr[y][x], int) and arr[y][x] == maskedarr[y][x]:
        if countflagsforcell(maskedarr, x, y, fc) == arr[y][x]:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if maskedarr[ny][nx] == mc:
                            maskedarr, game = click(arr, maskedarr, nx, ny, ws, w, h, mc, bc, fc, stdscr)
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

def select(maskedarr, sx, sy, game, flags, stdscr):
    selected = False
    action = ""
    while not selected and game:
        printarr(maskedarr, sx, sy, stdscr)
        key = uc.getch()
        if key == uc.KEY_RIGHT and sx < len(maskedarr[0]) - 1:
            sx += 1
        elif key == uc.KEY_LEFT and sx > 0:
            sx -= 1
        elif key == uc.KEY_DOWN and sy < len(maskedarr) - 1:
            sy += 1
        elif key == uc.KEY_UP and sy > 0:
            sy -= 1
        elif key == ord('z'):
            action = "click"
            selected = True
        elif key == ord('x'):
            action = "flag"
            selected = True
        elif key == ord('q'):
            action = "quit"
            selected = True
    return action, sx, sy

def main(h, w, bt, bc, mc, ws, fc, stdscr):
    game = True
    sx, sy = 0, 0
    flags = 0
    maskedarr = [[mc for _ in range(w)] for _ in range(h)]
    action, sx, sy = select(maskedarr, sx, sy, game, flags, stdscr)
    cx, cy = sx, sy
    arr = [[ws for _ in range(w)] for _ in range(h)]
    arr = createnoise(arr, w, h, bt, bc, cx, cy)
    arr = countbombs(arr, bc, ws)

    if action == "click":
        maskedarr, game = click(arr, maskedarr, sx, sy, ws, w, h, mc, bc, fc, stdscr)
    elif action == "flag":
        maskedarr, flags = flag(maskedarr, sx, sy, mc, fc, flags)
    elif action == "quit":
        exit_game()

    if not game:  # Game over
        return

    if checkwin(arr, maskedarr, bc, w, h, mc, fc):
        printendarr(arr, bc, stdscr)
        uc.mvaddstr(h+1, 0, "You win! Press any key to exit")
        uc.refresh()
        uc.getch()
        return

    while game:
        action, sx, sy = select(maskedarr, sx, sy, game, flags, stdscr)
        if action == "click":
            maskedarr, game = click(arr, maskedarr, sx, sy, ws, w, h, mc, bc, fc, stdscr)
            if not game:  # Game over
                break
        elif action == "flag":
            maskedarr, flags = flag(maskedarr, sx, sy, mc, fc, flags)
        elif action == "quit":
            exit_game()

        if checkwin(arr, maskedarr, bc, w, h, mc, fc):
            printendarr(arr, bc, stdscr)
            uc.mvaddstr(h+1, 0, "You win! Press q to exit")
            uc.refresh()
            uc.getch()
            break

def titlescreen(stdscr):
    uc.clear()
    uc.mvaddstr(0, 0, "Welcome to Minesweeper!")
    uc.mvaddstr(1, 0, "select difficulty")
    
    difficulties = {"Beginner": (8,8,10), "Intermediate": (16,16,40), "Expert": (30,16,99), "Custom": (0,0,0)}
    keys = list(difficulties.keys())
    ind = 0
    
    while True:
        for i in range(len(keys)):
            if i == ind:
                uc.mvaddstr(i+2, 0, f"{i+1}. {keys[i]}", uc.A_REVERSE)
            else:
                uc.mvaddstr(i+2, 0, f"{i+1}. {keys[i]}")
        
        uc.refresh()
        key = uc.getch()
        
        if key == uc.KEY_DOWN and ind < len(keys) - 1:
            ind += 1
        elif key == uc.KEY_UP and ind > 0:
            ind -= 1
        elif key == ord('q'):
            exit_game()
        elif key == 10:  # Enter key
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
    
    # Initialize color pairs
    uc.start_color()
    # Bomb color (red)
    uc.init_pair(1, uc.COLOR_RED, uc.COLOR_BLACK)
    # Cursor color (white background)
    uc.init_pair(2, uc.COLOR_BLACK, uc.COLOR_WHITE)
    # Flag color (red background)
    uc.init_pair(3, uc.COLOR_RED, uc.COLOR_BLACK)
    # Number colors (4-11)
    for i in range(1, 9):
        uc.init_pair(3 + i, i, uc.COLOR_BLACK)
    
    # Define characters for the game
    bc = "#"  # bomb character
    mc = "."  # masked character
    ws = " "  # white space
    fc = "F"  # flag character
    
    main(h, w, bt, bc, mc, ws, fc, stdscr)

if __name__ == "__main__":
    stdscr = uc.initscr()
    uc.noecho()
    uc.cbreak()
    uc.keypad(stdscr, True)
    uc.curs_set(0)  # Hide cursor
    
    # Check if terminal supports colors
    if uc.has_colors():
        uc.start_color()
    
    try:
        while True:  # Main game loop to allow playing again
            titlescreen(stdscr)
            uc.clear()
            uc.mvaddstr(0, 0, "Press Q to quit or any other key to play again")
            uc.refresh()
            key = uc.getch()
            if key == ord('q'):
                break
    finally:
        exit_game()