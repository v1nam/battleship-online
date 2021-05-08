from threading import Thread

import pygame

from client.interface.game import Game
from client.interface.menu import Menu
from client.misc.network import Network


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((450, 740))
        pygame.display.set_caption("Battleship")

        self.running = True
        self.clock = pygame.time.Clock()
        self.menu = Menu(self.screen)
        self.game = None
        self.thread_started = False

    def run(self):
        while self.running:
            if self.menu.show_menu:
                if (r := self.menu.run()) :
                    if r == "QUIT":
                        self.running = False
                        break
                    if not self.game:
                        self.game = Game(self.screen, Network())
                    self.game.n.send(r)
                    if not self.thread_started:
                        if r == "CREATE":
                            self.recv_thread = Thread(
                                target=self.game.receiving_thread,
                                kwargs={"menu": self.menu},
                            )
                        elif (d := self.game.n.receive()) != "INVALID":
                            if d == "TAKEN":
                                self.menu.game_taken = True
                                continue
                            else:
                                self.recv_thread = Thread(
                                    target=self.game.receiving_thread,
                                    args=(d, self.menu),
                                )
                        else:
                            self.menu.invalid_code = True
                            continue
                        self.recv_thread.daemon = True
                        self.recv_thread.start()
                        self.thread_started = True
                    if not (self.menu.invalid_code or self.menu.game_taken):
                        self.menu.show_menu = False
            elif self.game.run() == "MENU":
                self.menu.show_menu = True
                self.menu.reset()
                self.game.reset()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            pygame.display.flip()
            self.clock.tick(30)

        return pygame.quit()


if __name__ == "__main__":
    Main().run()