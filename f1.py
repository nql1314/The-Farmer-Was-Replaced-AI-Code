clear()
PATH = {
    (0, 0):East, (1, 0):East, (2, 0):East, (3, 0):East, (4, 0):East, (5, 0):East, (6, 0):East, (7, 0):North, 
    (7, 1):West, (6, 1):West, (5, 1):West, (4, 1):West, (3, 1):West, (2, 1):West, (1, 1):North, (1, 2):East, 
    (2, 2):East, (3, 2):East, (4, 2):East, (5, 2):East, (6, 2):East, (7, 2):North, (7, 3):West, (6, 3):West,
    (5, 3):West, (4, 3):West, (3, 3):West, (2, 3):West, (1, 3):North, (1, 4):East, (2, 4):East, (3, 4):East,
    (4, 4):East, (5, 4):East, (6, 4):East, (7, 4):North, (7, 5):West, (6, 5):West, (5, 5):West, (4, 5):West,
    (3, 5):West, (2, 5):West, (1, 5):North, (1, 6):East, (2, 6):East, (3, 6):East, (4, 6):East, (5, 6):East, 
    (6, 6):East, (7, 6):North, (7, 7):West, (6, 7):West, (5, 7):West, (4, 7):West, (3, 7):West, (2, 7):West, 
    (1, 7):West, (0, 7):South, (0, 6):South, (0, 5):South, (0, 4):South, (0, 3):South, (0, 2):South, (0, 1):South,
}

for direction1 in PATH:
    quick_print(str(direction1)+": [")
    for direction in PATH:
        quick_print(str(PATH[get_pos_x(), get_pos_y()])+",")
        move(PATH[get_pos_x(), get_pos_y()])
    quick_print("]")
    move(PATH[get_pos_x(), get_pos_y()])



