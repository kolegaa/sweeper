from random import randint

def createnoise(w, h, bt, ws, bc,cx,cy):  # width, height, bomb count, white space, bomb character
    arr = [[ws for _ in range(h)] for _ in range(w)]
    bombs_placed = 0
    while bombs_placed < bt:
        x, y = randint(0, w - 1), randint(0, h - 1)
        if arr[x][y] != bc and (x,y) != (cx,cy):  # Only place a bomb if the cell is empty and not the input cell
            arr[x][y] = bc
            bombs_placed += 1
    return arr

def countbombs(arr):  # count the bombs around each cell
    w, h = len(arr), len(arr[0])
    for i in range(w):
        for j in range(h):
            if arr[i][j] == "*":
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

def printarr(arr):  # print the array
    for i in arr:
        for j in i:
            print(j, end=" ")
        print()
    print()

def click(arr, maskedarr, x, y, ws, w, h, mc): 
    if arr[x][y] == "*":
        print("Game Over")
        return maskedarr, False
    elif arr[x][y] == 0 and maskedarr[x][y] == mc:
        maskedarr[x][y] = ws
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i < 0 or x + i >= len(arr) or y + j < 0 or y + j >= len(arr[0]):
                    continue
                click(arr, maskedarr, x + i, y + j, ws, w, h, mc)
    else:
        maskedarr[x][y] = str(arr[x][y])
    return maskedarr, True

def start(h, w, ws, bt, bc, mc): #basic tui for testing  # height, width, white space, bomb count, bomb character, masked character
    maskedarr = [[mc for _ in range(h)] for _ in range(w)]
    cy, cx = map(int, input("Enter coordinates (y x): ").split())
    arr = createnoise(w, h, bt, ws, bc, cx,cy)
    arr = countbombs(arr)  # Count bombs before clicking
    game = True
    maskedarr,game = click(arr, maskedarr, cx, cy, ws, w, h, mc)
    while game:
        printarr(maskedarr)
        y,x = map(int, input("Enter coordinates (x y): ").split())
        if maskedarr[x][y] == mc:
            maskedarr,game = click(arr, maskedarr, x, y, ws, w, h, mc)
        else:
            print("Already clicked")

start(5, 5, "o", 5, "*", "O")

