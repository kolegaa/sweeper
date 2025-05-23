from random import randint
from rich.console import Console
import keyboard
import time

def createnoise(w, h, bt, ws, bc,cx,cy):  # width, height, bomb count, white space, bomb character
    arr = [[ws for _ in range(h)] for _ in range(w)]
    bombs_placed = 0
    while bombs_placed < bt:
        x, y = randint(0, w - 1), randint(0, h - 1)
        if arr[y][x] != bc and (x,y) != (cx,cy):  # Only place a bomb if the cell is empty and not the clicked cell
            bombs_placed += 1
    return arr

def countbombs(arr,bc):  # count the bombs around each cell
    w, h = len(arr), len(arr[0])
    for i in range(w):
        for j in range(h):
            if arr[i][j] == bc:
                continue
            count = 0
            for x in range(-1, 2):
                for y in range(-1, 2):
                    if i + x < 0 or i + x >= w or j + y < 0 or j + y >= h:
                        continue
                    if arr[i + x][j + y] == "*":
                        count += 1
            arr[i][j] = count
    return arr

def printarr(arr,sx,sy):  # print the array
    console = Console()
    console.clear()
    buffer = ""
    for i in range(len(arr)):
        for j in range(len(arr[i])):
            if (i,j) == (sy,sx):
                buffer+="[r]"+arr[i][j]+"[/r]"
            else: buffer+=arr[i][j]
        buffer+="\n"
    console.print(buffer)

def click(arr, maskedarr, x, y, ws, w, h, mc): 
    console=Console()
    if arr[y][x] == mc:
        console.print("Game Over")
        return maskedarr, False
    elif arr[y][x] == 0 and maskedarr[y][x] == mc:
        maskedarr[y][x] = ws
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i < 0 or x + i >= len(arr) or y + j < 0 or y + j >= len(arr[0]):
                    continue
                maskedarr,coconutphoto=click(arr, maskedarr, x + i, y + j, ws, w, h, mc)
    else:
        maskedarr[y][x] = str(arr[y][x])
    return maskedarr, True

def flag(maskedarr, x, y, mc,fc):  # flag a cell
    if maskedarr[y][x] == mc:
        maskedarr[y][x] = fc
    elif maskedarr[y][x] == fc:
        maskedarr[y][x] = mc
    return maskedarr

def checkwin(arr,maskedarr, bc, w, h, mc,flag):
    for i in range(w): 
        for j in range(h):
            if arr[i][j] == bc and maskedarr[i][j] != flag:
                return False
            elif arr[i][j] != bc and maskedarr[i][j] == mc:
                return False
    return True 

def select(maskedarr,sx,sy,game):
    selected = False
    action = ""
    pressed = False
    while not selected and game:
        printarr(maskedarr, sx, sy)
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:  # Check if the key is pressed down
            if event.name == "d" and sx < len(maskedarr[0]) - 1:
                sx += 1
            elif event.name == "a" and sx > 0:
                sx -= 1
            elif event.name == "s" and sy < len(maskedarr) - 1:
                sy += 1
            elif event.name == "w" and sy > 0:
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


def main(h,w,bt,bc,mc,ws,fc):
    game = True
    sx,sy = 0,0
    maskedarr = [[mc for _ in range(h)] for _ in range(w)]
    action, sx, sy = select(maskedarr,sx,sy,game)
    cx,cy = sx,sy
    arr = createnoise(w, h, bt, ws, bc, cx,cy)
    arr = countbombs(arr,bc)  # Count bombs before clicking
    console=Console()
    if action == "click":
        if maskedarr[sy][sx] == mc:
            maskedarr,game = click(arr, maskedarr, sx, sy, ws, w, h, mc)
        else:
            console.print("Already clicked")
    elif action == "flag":
        maskedarr = flag(maskedarr, sx, sy, mc,fc)
    elif action == "quit":
        exit()
    while game:
        action,sx,sy=select(maskedarr,sx,sy,game)
        if action == "click":
            if maskedarr[sy][sx] == mc:
                maskedarr,game = click(arr, maskedarr, sx, sy, ws, w, h, mc)
            else:
                console.print("Already clicked")
        elif action == "flag":
            maskedarr = flag(maskedarr, sx, sy, mc,fc)
        elif action == "quit":
            break
        if checkwin(arr, maskedarr, bc, w, h, mc,fc):
            console.print("You win")
            break

def titlescreen():
    console = Console()
    console.print("Welcome to Minesweeper!")
    console.print("select difficulty")
    selected = ""
    ind = 0
    difficulties = {"Beginner":(8,8,10), "Intermediate":(16,16,40), "Expert":(30,16,99),"Custom":(0,0,0)}
    buffer ="Welcome to Minesweeper! \n select difficulty"
    for i in range(len(difficulties)):
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
        elif event.event_type == keyboard.KEY_DOWN and event.name == "enter":
            selected = list(difficulties.keys())[ind]
        for i in range(len(difficulties)):
            if i == ind:
                buffer += "\n"+f"[r]{i+1}. {list(difficulties.keys())[i]}[/r]"
            else:
                buffer += "\n"+f"{i+1}. {list(difficulties.keys())[i]}"
    console.print("You selected: "+selected)
    if selected == "Custom":
        input()
        w = int(input("Enter width: "))
        h = int(input("Enter height: "))
        bt = int(input("Enter bomb count: "))
    else:
        w,h,bt = difficulties[selected]
    main(h,w, bt, "#", "[cyan on blue]  [/]", "o","[pink on red]  [/]")

if __name__ == "__main__":
    titlescreen()