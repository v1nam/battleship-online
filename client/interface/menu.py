import pygame
import random
from client.misc.colors import *


class Particle:
    def __init__(self, location, velocity, time):
        self.location = location
        self.velocity = velocity
        self.time = time


class Ship:
    def __init__(self):
        self.image = pygame.image.load("client/assets/ship.png")
        self.dir = "<"
        if random.choice((True, False)) == True:
            self.image = pygame.transform.flip(self.image, True, False)
            self.dir = ">"
        self.x = 450 if self.dir == "<" else -self.image.get_width()
        self.y = random.choice((random.randint(250, 320), random.randint(510, 650)))
        self.visible = True

    def draw(self, screen):
        self.x = self.x + 3 if self.dir == ">" else self.x - 3
        if self.x < -self.image.get_width() or self.x > 750 + self.image.get_width():
            self.visible = False
        screen.blit(self.image, (self.x, self.y))


class Menu:
    def __init__(self, screen):
        self.font = pygame.font.Font("client/assets/retrofont.ttf", 36)
        self.small_font = pygame.font.Font("client/assets/retrofont.ttf", 25)
        self.screen = screen
        self.load_entities()
        self.invalid_code = False
        self.show_menu = True
        self.game_taken = False
        self.particles = []
        self.ships = [Ship() for _ in range(3)]

    def run(self):
        self.screen.fill(BACKGROUND)
        self.draw_ships()
        title = self.font.render("BATTLESHIP", True, CYAN)
        online_text = self.small_font.render("ONLINE", True, AQUA)
        self.screen.blit(title, (225 - title.get_width() // 2, 140))
        self.screen.blit(online_text, (225 - online_text.get_width() // 2, 190))

        pygame.draw.rect(self.screen, self.create_button_color, self.create_button)
        pygame.draw.rect(self.screen, BLACK, self.create_button, 4)
        pygame.draw.rect(self.screen, BACKGROUND, self.join_button)
        pygame.draw.rect(self.screen, BLACK, self.join_button, 4)

        self.screen.blit(
            self.create_text, (225 - self.create_text.get_width() // 2, 365)
        )
        if not self.join_hover:
            self.join_code = ""
            self.screen.blit(
                self.join_text, (225 - self.join_text.get_width() // 2, 465)
            )
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "QUIT"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        self.join_code = self.join_code[:-1]
                    if event.key == pygame.K_RETURN:
                        if len(self.join_code) == 6:
                            return {"category": "JOIN", "payload": self.join_code}
                    elif (t := event.unicode) in __import__("string").ascii_lowercase:
                        self.join_code += t
                    self.join_code = self.join_code[:6]
            if self.join_code == "" or self.join_code == "_":
                self.update_cursor()
                self.join_code = self.cursor
            else:
                self.join_code = self.join_code.strip("_")
            code_text = self.small_font.render(self.join_code, True, BLUE)
            self.screen.blit(code_text, (225 - code_text.get_width() // 2, 465))
            if self.invalid_code:
                text = self.small_font.render("Invalid Code", True, RED)
                self.screen.blit(text, (230 - text.get_width() // 2, 585))
            elif self.game_taken:
                text = self.small_font.render("Game Occupied", True, RED)
                self.screen.blit(text, (230 - text.get_width() // 2, 585))
        m_x, m_y = pygame.mouse.get_pos()
        if self.create_button.collidepoint(m_x, m_y):
            if pygame.mouse.get_pressed(3)[0]:
                return {"category": "CREATE"}
            self.join_hover = False
            self.invalid_code = False
            self.game_taken = False
            self.create_button_color = HOVER
        elif self.join_button.collidepoint(m_x, m_y):
            self.join_hover = True
            self.create_button_color = BACKGROUND
        else:
            self.join_hover = False
            self.invalid_code = False
            self.game_taken = False
            self.create_button_color = BACKGROUND

        self.draw_particles([50, 170])
        self.draw_particles([390, 170])

    def update_cursor(self):
        self.blink_count += 1
        if self.blink_count > 15:
            self.cursor = "_" if self.cursor == "" else ""
            self.blink_count = 0

    def reset(self):
        self.join_hover = False
        self.join_code = ""
        self.invalid_code = False
        self.blink_count = 0
        self.cursor = "_"
        self.game_taken = False

    def load_entities(self):
        self.create_text = self.small_font.render("NEW GAME", True, BLUE)
        self.join_text = self.small_font.render("JOIN GAME", True, BLUE)
        self.create_button = pygame.Rect(100, 350, 250, 60)
        self.join_button = pygame.Rect(100, 450, 250, 60)
        self.join_hover = False
        self.join_code = ""
        self.blink_count = 0
        self.cursor = "_"
        self.create_button_color = BACKGROUND

    def draw_particles(self, loc):
        self.particles.append(
            Particle(loc, [random.randint(0, 14) / 9 - 1, -2.5], random.randint(4, 6))
        )
        for particle in self.particles:
            particle.location[0] += particle.velocity[0]
            particle.location[1] += particle.velocity[1]
            particle.time -= 0.1
            pygame.draw.circle(
                self.screen, (190, 220, 219), particle.location, particle.time
            )
            radius = particle.time * 2
            self.screen.blit(
                self.circle_surf(radius, (38, 67, 86)),
                [int(i - radius) for i in particle.location],
                special_flags=pygame.BLEND_RGB_ADD,
            )
            if particle.time <= 2:
                self.particles.remove(particle)

    @staticmethod
    def circle_surf(radius, color):
        surf = pygame.Surface((radius * 2, radius * 2))
        pygame.draw.circle(surf, color, (radius, radius), radius)
        surf.set_colorkey((0, 0, 0))
        return surf

    def draw_ships(self):
        self.ships = sorted(self.ships, key=lambda s: s.x)
        for ship in self.ships:
            if any(
                ship != s and ship.y >= s.y and ship.y <= s.y + s.image.get_width()
                for s in self.ships
            ):
                self.ships.remove(ship)
        for ship in self.ships:
            ship.draw(self.screen)
        self.ships = [ship for ship in self.ships if ship.visible]
        while len(self.ships) < 3:
            self.ships.append(Ship())