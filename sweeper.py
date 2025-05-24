from random import randint
from rich.console import Console
import keyboard
import time

def exit_game():
    exit()

def printendarr(arr,bc):
    console = Console()
    console.clear()
    buffer = ""
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if arr[i][j] == bc:
                buffer+="[red]"+str(arr[i][j])+"[/]"
            else: buffer+=str(arr[i][j])
        buffer+="\n"
    console.print(buffer)

def createnoise(arr,w, h, bt, bc,cx,cy):  # width, height, bomb count, white space, bomb character
    bombs_placed = 0
    while bombs_placed < bt:
        x, y = randint(0, w - 1), randint(0, h - 1)
        if arr[y][x] != bc and (x,y) != (cx,cy):
            # Check 3x3 area around first click
            canplace = True
            for i in range(-1, 2):  # Fixed range
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

def countbombs(arr,bc,ws):  # count the bombs around each cell
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

def printarr(arr,sx,sy):  # print the array
    console = Console()
    console.clear()
    buffer = ""
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if (i,j) == (sy,sx):
                buffer+="[r]"+str(arr[i][j])+"[/r]"
            else: buffer+=str(arr[i][j])
        buffer+="\n"
    console.print(buffer)

def countflagsforcell(maskedarr, x, y, fc):
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue  # Skip self
            nx = x + dx
            ny = y + dy
            if 0 <= nx < len(maskedarr[0]) and 0 <= ny < len(maskedarr):
                if maskedarr[ny][nx] == fc:
                    count += 1
    return count

def click(arr, maskedarr, x, y, ws, w, h, mc,bc,fc):
    console=Console()
    # Skip if cell is flagged
    if maskedarr[y][x] == fc:
        return maskedarr, True
    if arr[y][x] == bc:
        printendarr(arr,bc)
        console.print("Game Over")
        return maskedarr, False
    elif arr[y][x] == ws and maskedarr[y][x] == mc:
        maskedarr[y][x] = ws
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + j < 0 or x + j >= w or y + i < 0 or y + i >= h:
                    continue
                if maskedarr[y + i][x + j] == mc:
                    maskedarr, _ = click(arr, maskedarr, x + j, y + i, ws, w, h, mc, bc, fc)
    elif isinstance(maskedarr[y][x], int) and arr[y][x] == maskedarr[y][x]:
        # Chord reveal logic
        if countflagsforcell(maskedarr, x, y, fc) == arr[y][x]:
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
        maskedarr[y][x] = arr[y][x]  # Store as integer instead of string
    return maskedarr, True

def flag(maskedarr, x, y, mc,fc,flags):  # flag a cell
    if maskedarr[y][x] == mc:
        maskedarr[y][x] = fc
        flags +=1
    elif maskedarr[y][x] == fc:
        maskedarr[y][x] = mc
        flags -=1
    return maskedarr,flags

def checkwin(arr,maskedarr, bc, w, h, mc,flag):
    for i in range(h): 
        for j in range(w):
            if arr[i][j] == bc and maskedarr[i][j] != flag:
                return False
            elif arr[i][j] != bc and maskedarr[i][j] == mc:
                return False
    return True 

def select(maskedarr,sx,sy,game,flags):
    selected = False
    action = ""
    while not selected and game:
        printarr(maskedarr, sx, sy)
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:  # Check if the key is pressed down
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

def main(h,w,bt,bc,mc,ws,fc): # height, width, bomb count, bomb character, masked character, white space, flagged character
    console=Console()
    game = True
    sx,sy = 0,0
    flags = 0
    maskedarr = [[mc for _ in range(w)] for _ in range(h)]
    action, sx, sy = select(maskedarr,sx,sy,game,flags)
    cx,cy = sx,sy
    arr = [[ws for _ in range(w)] for _ in range(h)]
    arr = createnoise(arr,w, h, bt, bc, cx,cy)
    arr = countbombs(arr,bc,ws)  # Count bombs before clicking

    if action == "click":
        maskedarr,game = click(arr, maskedarr, sx, sy, ws, w, h, mc,bc,fc)
    elif action == "flag":
        maskedarr,flags = flag(maskedarr, sx, sy, mc,fc,flags)
    elif action == "quit":
        exit_game()

    if checkwin(arr, maskedarr, bc, w, h, mc,fc):
            printendarr(arr,bc)
            console.print("You win")
            exit_game()

    while game:
        action,sx,sy=select(maskedarr,sx,sy,game,flags)
        if action == "click":
            maskedarr,game = click(arr, maskedarr, sx, sy, ws, w, h, mc,bc,fc)
        elif action == "flag":
            maskedarr,flags  = flag(maskedarr, sx, sy, mc,fc,flags)
        elif action == "quit":
            exit_game()
        if checkwin(arr, maskedarr, bc, w, h, mc,fc):
            printendarr(arr,bc)
            console.print("You win")
            exit_game()
    exit_game()

def titlescreen():
    console = Console()
    console.print("Welcome to Minesweeper!")
    console.print("select difficulty")
    selected = ""
    ind = 0
    difficulties = {"Beginner":(8,8,10), "Intermediate":(16,16,40), "Expert":(30,16,99),"Custom":(0,0,0)}
    buffer ="Welcome to Minesweeper! \n select difficulty"
    for i in range(len(difficulties)):
            if i == ind:
                buffer += "\n"+f"[r]{i+1}. {list(difficulties.keys())[i]}[/r]"
            else:
                buffer += "\n"+f"{i+1}. {list(difficulties.keys())[i]}"
    while selected == "":
        console.clear()
        console.print(buffer)
        time.sleep(0.1)
        buffer ="Welcome to Minesweeper! \n select difficulty"
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN and event.name == "down":
            ind+=1
        elif event.event_type== keyboard.KEY_DOWN and event.name == "up":
            ind-=1
        elif event.event_type==keyboard.KEY_DOWN and event.name == "q":
            exit_game()
        elif event.event_type == keyboard.KEY_DOWN and event.name == "enter":
            selected = list(difficulties.keys())[ind]
        for i in range(len(difficulties)):
            if i == ind:
                buffer += "\n"+f"[r]{i+1}. {list(difficulties.keys())[i]}[/r]"
            else:
                buffer += "\n"+f"{i+1}. {list(difficulties.keys())[i]}"
    console.print("You selected: "+selected)
    if selected == "Custom":
        w = int(console.input("Enter width: "))
        h = int(console.input("Enter height: "))
        bt = int(console.input("Enter bomb count: "))
    else:
        w,h,bt = difficulties[selected]
    main(h,w, bt, "#", "[default on blue] [/]", "[default on default] [/]","[bright_red on red] [/]") # height, width, bomb count, bomb character, masked character, white space, flag character

if __name__ == "__main__":
    titlescreen()