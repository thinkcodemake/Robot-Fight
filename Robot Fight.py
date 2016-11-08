import pygame
from pygame.locals import *
from collections import namedtuple
import random

genome_fields = [
    'chest_size',
    'base_size',
    'arm_one',
    'arm_two',
    'move_one',
    'move_two',
    'move_three',
    'jump_one',
    'jump_two',
    'jump_three',
    'action_one',
    'action_two',
    'action_three',
    'action_four',
    'action_five',
    'action_six'
    ]

Genome = namedtuple('Genome', genome_fields)


class RobotFight():

    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 500

    def __init__(self):
        """
        Initialize game.
        """

        pygame.init()

        self.size = (RobotFight.SCREEN_WIDTH, RobotFight.SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(self.size)
        self.bg_color = (255, 255, 255)

        self.running = True

        self.timer = pygame.time.Clock()

        self.fighter_bot = pygame.sprite.Group()
        self.fighter_bot.add(Robot())

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

            self.fighter_bot.update()
            
            self.screen.fill(self.bg_color)
            self.fighter_bot.draw(self.screen)
            
            self.timer.tick(60)
            pygame.display.update()
            
        pygame.quit()


class Robot(pygame.sprite.Sprite):

    MIN_CHEST = 10
    MAX_CHEST = 100
    MIN_BASE = 10
    MAX_BASE = 100
    NUM_WEAPONS = 2
    MAX_MOVE = 10
    HEIGHT = RobotFight.SCREEN_HEIGHT / 10
    WIDTH = (HEIGHT * 2) / 3

    def __init__(self, genome=None):
        """
        Initialize the Robot.
        """

        pygame.sprite.Sprite.__init__(self)
        
        if genome is None:
            self.genome = self.generate_random_genome()
        else:
            self.genome = genome

        self.image = pygame.Surface([Robot.WIDTH, Robot.HEIGHT])  # Temporary Values
        self.image.fill((255, 0, 0))  # Temporary Values

        self.rect = self.image.get_rect()

    def generate_random_genome(self):
        """
        Return a randomly generated genome.
        """
        return Genome(
            random.randint(Robot.MIN_CHEST, Robot.MAX_CHEST),  # chest_size
            random.randint(Robot.MIN_BASE, Robot.MAX_BASE),  # base_size
            random.randint(0, Robot.NUM_WEAPONS),  # arm_one
            random.randint(0, Robot.NUM_WEAPONS),  # arm_two
            random.randint(-Robot.MAX_MOVE, Robot.MAX_MOVE),  # move_one
            random.randint(-Robot.MAX_MOVE, Robot.MAX_MOVE),  # move_two
            random.randint(-Robot.MAX_MOVE, Robot.MAX_MOVE),  # move_three
            random.randint(0, 1),  # jump_one
            random.randint(0, 1),  # jump_two
            random.randint(0, 1),  # jump_three
            random.randint(0, 2),  # action_one
            random.randint(0, 2),  # action_two
            random.randint(0, 2),  # action_three
            random.randint(0, 2),  # action_four
            random.randint(0, 2),  # action_five
            random.randint(0, 2),  # action_six
        )


if __name__ == '__main__':
    game = RobotFight()
    game.start()
