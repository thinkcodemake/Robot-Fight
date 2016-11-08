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
    FPS = 60

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

        self.fighter_bullets = pygame.sprite.Group()
        self.fighter_melee = pygame.sprite.Group()

        self.fighter_bot = pygame.sprite.Group()
        self.fighter_bot.add(Robot(self.fighter_bullets, self.fighter_melee))

        

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
            self.fighter_bullets.update()
            self.fighter_melee.update()
            
            self.screen.fill(self.bg_color)
            self.fighter_melee.draw(self.screen)
            self.fighter_bot.draw(self.screen)
            self.fighter_bullets.draw(self.screen)
            
            self.timer.tick(self.FPS)
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
    MAX_ACTIONS = 6
    GRAVITY = 1

    def __init__(self, bullet_group, melee_group, genome=None, color=None):
        """
        Initialize the Robot.
        """

        pygame.sprite.Sprite.__init__(self)
        
        if genome is None:
            self.genome = self.generate_random_genome()
        else:
            self.genome = genome

        if color is None:
            self.color = (random.randint(10, 245),
                          random.randint(10, 245),
                          random.randint(10, 245))
        else:
            self.color = color

        self.image = pygame.Surface([Robot.WIDTH, Robot.HEIGHT])  # Temporary Values
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.move_ip(Robot.WIDTH,
                          (RobotFight.SCREEN_HEIGHT - Robot.HEIGHT))

        self.action_phase = 1
        self.action_switch_count = 0

        self.vertical = 0

        self.bullet_group = bullet_group
        self.melee_group = melee_group

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

    def update(self):
        """
        Handle logic.
        """
        if self.action_switch_count >= RobotFight.FPS:
            self.action_phase += 1

            if self.action_phase > 6:
                self.action_phase = 1

            self.action_switch_count = 0

            self.action()

            self.check_jump()

        self.action_switch_count += 1
        
        self.move()

    def move(self):
        
        if self.action_phase % 3 == 0:
            self._move_if_clear(self.genome.move_one, 0)
        elif self.action_phase % 3 == 1:
            self._move_if_clear(self.genome.move_two, 0)
        elif self.action_phase % 3 == 2:
            self._move_if_clear(self.genome.move_three, 0)

        if not self.on_floor():
            self.vertical += Robot.GRAVITY
            self._move_if_clear(0, self.vertical)

        if self.on_floor():
            if self.vertical != 0:
                self.vertical = 0
            

    def _move_if_clear(self, x, y):
        self.rect.move_ip(x, y)

        if self.rect.x < 0:
            self.rect.x = 0
        elif self.rect.x >= RobotFight.SCREEN_WIDTH - Robot.WIDTH:
            self.rect.x = RobotFight.SCREEN_WIDTH - Robot.WIDTH

        if self.rect.y < 0:
            self.rect.y = 0
        elif self.rect.y >= RobotFight.SCREEN_HEIGHT - Robot.HEIGHT:
            self.rect.y = RobotFight.SCREEN_HEIGHT - Robot.HEIGHT

    def on_floor(self):
        return self.rect.y == RobotFight.SCREEN_HEIGHT - Robot.HEIGHT

    def check_jump(self):
        if self.action_phase % 3 == 0 & self.genome.jump_one:
            self.jump()
        elif self.action_phase % 3 == 1 & self.genome.jump_two:
            self.jump()
        elif self.action_phase % 3 == 2 & self.genome.jump_three:
            self.jump()

    def jump(self):
        self._move_if_clear(0, -1)
        self.vertical = -10  # Temp Value, will be based on other stuff
        print('Jumping')

    def action(self):

        action = self.genome[self.action_phase + 9]
        
        if action == 0:
            pass
        elif action == 1:
            self._perform_action(self.genome.arm_one)
        elif action == 2:
            self._perform_action(self.genome.arm_two)

    def _perform_action(self, weapon):
        if weapon == 0:
            pass
        elif weapon == 1:
            self.shoot()
        elif weapon == 2:
            self.melee()

    def shoot(self):
        print('Shooting')
        self.bullet_group.add(Bullet(self, 1))

    def melee(self):
        print('Meleeing')
        self.melee_group.add(MeleeRange(self))


class Bullet(pygame.sprite.Sprite):

    SPEED = 5

    def __init__(self, attacker, direction):
        pygame.sprite.Sprite.__init__(self)

        self.direction = direction

        self.image = pygame.Surface([Robot.HEIGHT / 3, Robot.HEIGHT / 3])
        self.image.fill(attacker.color)  # Temporary Value
        
        self.rect = self.image.get_rect()

        self.rect.x = attacker.rect.x
        self.rect.y = attacker.rect.y

    def update(self):
        self.rect.x += (Bullet.SPEED * self.direction)
        if self.rect.x < 0 or self.rect.x > RobotFight.SCREEN_WIDTH:
            self.kill()

class MeleeRange(pygame.sprite.Sprite):

    SIZE = Robot.WIDTH

    def __init__(self, attacker):
        pygame.sprite.Sprite.__init__(self)

        area = [
            (Robot.WIDTH + (MeleeRange.SIZE * 2)),
            (Robot.HEIGHT + (MeleeRange.SIZE * 2))
            ]

        self.image = pygame.Surface(area)

        color = (attacker.color[0] - 10,
                 attacker.color[1] - 10,
                 attacker.color[2] - 10)
        
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.center = attacker.rect.center

        self.attacker = attacker

        self.life = 0

    def update(self):
        self.life += 1

        self.rect.center = self.attacker.rect.center

        if self.life > RobotFight.FPS:
            self.kill()

if __name__ == '__main__':
    game = RobotFight()
    game.start()
