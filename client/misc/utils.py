import pygame
import random


def make_grid(sx, ex, sy, ey, color, size=35):
    return [
        [Node((x, y, size, size), color).__dict__ for y in range(sy, ey, size)]
        for x in range(sx, ex, size)
    ]


def image_at(sheet, rect):
    rect = pygame.Rect(*rect)
    image = pygame.Surface(rect.size).convert_alpha()
    image.blit(sheet, (0, 0), rect)
    image.set_colorkey((0, 0, 0))
    return image


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