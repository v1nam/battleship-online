import pygame
import random

SHIPS = {
    "Carrier": 5,
    "Battleship": 4,
    "Cruiser": 3,
    "Submarine": 3,
    "Destroyer": 2,
}


class Node:
    def __init__(self, rect, color):
        self.rect = rect
        self.ship = None
        self.color = color
        self.empty = 1
        self.aimed = False
        self.perma_color = None


def make_grid(sx, ex, sy, ey, color, size=35):
    return [
        [Node((x, y, size, size), color).__dict__ for y in range(sy, ey, size)]
        for x in range(sx, ex, size)
    ]


def layout_ships():
    grid = make_grid(50, 400, 390, 730, (76, 86, 106))
    for name, size in SHIPS.items():
        while True:
            ship_collision = False
            coords = []
            coord1 = random.randint(0, 9)
            coord2 = random.randint(0, 10 - size)

            if random.choice((True, False)):
                x, y = coord1, coord2
                xi, yi = 0, 1
            else:
                x, y = coord2, coord1
                xi, yi = 1, 0

            for i in range(size):
                new_x = x + (xi * i)
                new_y = y + (yi * i)
                if grid[new_x][new_y]["ship"]:
                    ship_collision = True
                    break
                coords.append((new_x, new_y))
            if not ship_collision:
                break
        for bx, by in coords:
            grid[bx][by]["ship"] = name
    return grid