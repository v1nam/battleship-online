import pygame
from client.misc.colors import *
from client.misc.utils import image_at, make_grid
from pygame import mixer

pygame.init()
mixer.init()
ship = "ship"
aimed = "aimed"
rect = "rect"
empty = "empty"
color = "color"
perma_color = "perma_color"
font = pygame.font.Font("client/assets/retrofont.ttf", 14)


class Player:
    def __init__(self):
        self.grid = []
        self.is_turn = None

        self.ship_img = pygame.image.load("client/assets/ship.png")
        sheet = pygame.image.load("client/assets/ship_fire.png")
        self.wrecks = [
            image_at(sheet, (1, 0, 35, 35)),
            image_at(sheet, (36, 0, 35, 35)),
            image_at(sheet, (71, 0, 35, 35)),
            image_at(sheet, (106, 0, 35, 35)),
        ]
        self.ship_destroyed_img = self.wrecks[0]
        self.fire_index = 0

    def draw_grid(self, screen):
        self.fire_index += 1
        if self.fire_index >= 28:
            self.fire_index = 0
        self.ship_destroyed_img = self.wrecks[self.fire_index // 7]
        for sx in self.grid:
            for square in sx:
                if square[ship] and square[aimed]:
                    r = pygame.Rect(square[rect])
                    r.y += 10
                    screen.blit(self.ship_destroyed_img, r)
                elif square[ship]:
                    screen.blit(self.ship_img, pygame.Rect(square[rect]))
                elif square[aimed]:
                    pygame.draw.circle(
                        screen,
                        WHITE,
                        (square[rect][0] + 17, square[rect][1] + 17),
                        10,
                        1,
                    )
                pygame.draw.rect(
                    screen, square[color], pygame.Rect(square[rect]), square[empty]
                )


class Opponent:
    def __init__(self):
        self.grid = make_grid(50, 400, 30, 370, BLACK)
        self.start_ticks = pygame.time.get_ticks()
        self.sunken_ships = {
            "Carrier": False,
            "Battleship": False,
            "Cruiser": False,
            "Submarine": False,
            "Destroyer": False,
        }
        self.current_sunkship = None
        self.explosion_sound = mixer.Sound("client/assets/explosion.wav")
        self.miss_sound = mixer.Sound("client/assets/miss.wav")
        self.sound_counter = 0

    def draw_grid(self, screen):
        for sx in self.grid:
            for square in sx:
                if square[perma_color]:
                    pygame.draw.circle(
                        screen,
                        square[perma_color],
                        (square[rect][0] + 17, square[rect][1] + 17),
                        11,
                    )
                    square[empty] = 1
                elif self.is_hovered(pygame.mouse.get_pos(), pygame.Rect(square[rect])):
                    square[empty] = 0
                    square[color] = (85, 92, 108)
                else:
                    square[empty] = 1
                pygame.draw.rect(
                    screen, square[color], pygame.Rect(square[rect]), square[empty]
                )
                if (
                    self.is_sunk(self.grid, square[ship])
                    and not self.sunken_ships[square[ship]]
                ):
                    if self.current_sunkship is None:
                        self.current_sunkship = square[ship]
                    if square[ship] != self.current_sunkship:
                        self.sunken_ships[self.current_sunkship] = True
                        self.current_sunkship = square[ship]
                    else:
                        text = f"You sunk their {square[ship]}!"
                        screen.blit(
                            font.render(text, True, WHITE),
                            (450 - len(text) * 10, 0),
                        )

    @staticmethod
    def is_hovered(mouse_pos, rect):
        m_x, m_y = mouse_pos
        return (
            m_y > rect.y
            and m_y < rect.y + rect.height
            and m_x > rect.x
            and m_x < rect.x + rect.width
        )

    @staticmethod
    def is_sunk(grid, ship_name):
        if ship_name:
            return all(y[aimed] for x in grid for y in x if y[ship] == ship_name)
