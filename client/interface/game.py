import pygame
from client.interface.player_opponent import *
from client.misc.colors import *


class Game:
    def __init__(self, screen, network):
        self.screen = screen
        self.game_over = False
        self.waiting = True
        self.opp_disconnected = False
        self.room_id = ""
        self.sent_over = False

        self.player = Player()
        self.opponent = Opponent()
        self.n = network

        self.sent = set()
        self.final_text = ""
        self.big_font = pygame.font.Font("client/assets/retrofont.ttf", 34)
        self.menu_button = pygame.Rect(125, 0, 200, 28)

    @staticmethod
    def check_game_over(grid):
        return all(sq[aimed] for x in grid for sq in x if sq[ship])

    def receiving_thread(self, board=None, menu=None):
        while 1:
            if not board:
                received = self.n.receive()
            else:
                received = board
                board = None
            if received:
                if menu:
                    if received == "TAKEN":
                        menu.game_taken = True
                        menu.show_menu = True
                    elif received == "INVALID":
                        menu.invalid_code = True
                        menu.show_menu = True
                if received == "END" and not menu.show_menu and not self.waiting:
                    self.opp_disconnected = True
                    break
                if isinstance(received, dict):
                    if received["category"] == "BOARD":
                        received = received["payload"]
                        self.waiting = False
                        self.player.is_turn = received[0]
                        self.player.grid = received[1]
                        for xi, yi, ship_ in received[2]:
                            self.opponent.grid[xi][yi][ship] = ship_
                    elif received["category"] == "ID":
                        self.room_id = received["payload"]
                    elif received["category"] == "POSITION":
                        rx, ry = received["payload"]
                        self.player.is_turn = True
                        self.player.grid[rx][ry][aimed] = True

    def render(self):
        pygame.draw.line(self.screen, BLACK, (0, 384), (450, 384), 10)
        self.player.draw_grid(self.screen)
        for ex, sx in enumerate(self.opponent.grid):
            for es, square in enumerate(sx):
                if (
                    Opponent.is_hovered(
                        pygame.mouse.get_pos(), pygame.Rect(square[rect])
                    )
                    and pygame.mouse.get_pressed(3)[0]
                    and self.player.is_turn
                ):
                    self.opponent.grid[ex][es][aimed] = True
                    if (x := (ex, es)) not in self.sent:
                        if square[ship]:
                            self.opponent.grid[ex][es][perma_color] = RED
                            while self.opponent.sound_counter < 1:
                                self.opponent.explosion_sound.play()
                                self.opponent.sound_counter += 1
                            self.opponent.sound_counter = 0
                        else:
                            self.opponent.grid[ex][es][perma_color] = WHITE
                            while self.opponent.sound_counter < 1:
                                self.opponent.miss_sound.play()
                                self.opponent.sound_counter += 1
                            self.opponent.sound_counter = 0
                        self.player.is_turn = False
                        self.sent.add(x)
                        self.n.send({"category": "POSITION", "payload": x})
        self.opponent.draw_grid(self.screen)

    def game_over_screen(self):
        if self.final_text == "You Lost!":
            for ex, sx in enumerate(self.player.grid):
                for es, square in enumerate(sx):
                    if square[ship]:
                        r = pygame.Rect(square[rect])
                        r.y += 10
                        self.screen.blit(self.player.ship_destroyed_img, r)
                        break
        pygame.draw.rect(self.screen, BACKGROUND, (0, 0, 450, 20))
        pygame.draw.rect(self.screen, BLACK, self.menu_button, 2)
        font = pygame.font.Font("client/assets/retrofont.ttf", 14)
        menu_text = font.render("Return To Menu", True, BLUE)
        self.screen.blit(menu_text, (225 - menu_text.get_width() // 2, 6))

        txt = self.big_font.render(self.final_text, True, GREEN)
        self.screen.blit(
            txt,
            (225 - txt.get_width() // 2, 370 - txt.get_height() // 2),
        )
        if (
            self.menu_button.collidepoint(*pygame.mouse.get_pos())
            and pygame.mouse.get_pressed(3)[0]
        ):
            return "MENU"

    def run(self):
        if not self.waiting:
            if self.check_game_over(self.opponent.grid):
                self.game_over = True
                self.final_text = "You Won!"
            elif self.check_game_over(self.player.grid):
                self.game_over = True
                self.final_text = "You Lost!"
            if not self.game_over:
                self.screen.fill(BACKGROUND)
                if self.opp_disconnected:
                    txt = self.big_font.render("Opponent Has Left", True, RED)
                    self.screen.blit(
                        txt, (225 - txt.get_width() // 2, 370 - txt.get_height() // 2)
                    )
                else:
                    self.render()
                    font = pygame.font.Font("client/assets/retrofont.ttf", 14)
                    if self.player.is_turn:
                        text = font.render("Your turn", True, WHITE)
                    else:
                        text = font.render("Opponent's turn", True, WHITE)
                    self.screen.blit(text, (0, 0))
            else:
                if not self.sent_over:
                    self.n.send({"category": "OVER"})
                    self.sent_over = True
                return self.game_over_screen()
        else:
            self.screen.fill(BACKGROUND)
            txt = self.big_font.render("Waiting For Player", True, GREEN)
            font = pygame.font.Font("client/assets/retrofont.ttf", 24)
            roomid_text = font.render(self.room_id, True, GREEN)
            self.screen.blit(
                txt, (225 - txt.get_width() // 2, 370 - txt.get_height() // 2)
            )
            self.screen.blit(
                roomid_text,
                (
                    225 - roomid_text.get_width() // 2,
                    (370 - txt.get_height() // 2) + 100,
                ),
            )

    def reset(self):
        self.game_over = False
        self.waiting = True
        self.opp_disconnected = False
        self.room_id = ""
        self.sent_over = False

        self.player = Player()
        self.opponent = Opponent()

        self.sent = set()
        self.final_text = ""
