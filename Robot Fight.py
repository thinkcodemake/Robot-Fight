import pygame
from pygame.locals import *
from collections import namedtuple

class RobotFight():

    def __init__(self):
        """
        Initialize game.
        """

        pygame.init()

        self.size = (1000, 500)
        self.screen = pygame.display.set_mode(self.size)
        self.bg_color = (255, 255, 255)

        self.running = True

        self.timer = pygame.time.Clock()

    def start(self):
        """
        Start Robot Fight.
        """
        self.main_loop()

    def main_loop(self):
        """
        Start and run the Main Loop.
        """
        while(self.running):

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
            
            self.screen.fill(self.bg_color)

            self.timer.tick(60)
            pygame.display.update()
            
        pygame.quit()


if __name__ == '__main__':
    game = RobotFight()
    game.start()
