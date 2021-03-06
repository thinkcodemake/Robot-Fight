import pygame
from pygame.locals import *
from collections import namedtuple
import random
import csv

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

    def __init__(self, size, defender):
        """
        Initialize the RobotFight game.
        :param size: Number of bots for each generation.
        :param defender: Robot of defender to test against.
        """
        pygame.init()

        self.size = (RobotFight.SCREEN_WIDTH, RobotFight.SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(self.size)
        self.bg_color = (255, 255, 255)

        self.running = True

        self.timer = pygame.time.Clock()

        self.genome_display = Display(0, 0)
        self.gen_display = Display(0, 25)
        self.att_hp_display = Display(0, 50)
        self.def_hp_display = Display(0, 75)
        
        self.current_gen = Generation.new_random_generation(size)
        self.match = None
        self.gen_iter = None
        self.gen_num = 1
        self.match_num = 1

        self.defender = defender
        self.defender.direction = -1

        self.out_data = []

    def start(self):
        """
        Start the RobotFight simulation.
        """
        self.gen_iter = iter(self.current_gen)
        self.match = Match(next(self.gen_iter), self.defender)

        print('New Round: Generation 1')
        print('=========')
        self.main_loop()

    def main_loop(self):
        """
        Begin the main loop of the simulation.
        """
        
        while(self.running):

            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False

                if event.type == KEYDOWN:
                    if event.key == K_n:
                        self.match.end()

            if self.match.running:
                self.match.update()

                self.screen.fill(self.bg_color)
                self.match.draw(self.screen)
                self.draw_displays()

                if self.match.finished():
                    # print()
                    # print(self.match.get_attacker().genome)
                    print('    ', self.match.get_attacker().fitness,
                          self.match.end_message)

                    self.log_match()

                    self.match.end()
                    
            else:
                try:
                    self.match = Match(next(self.gen_iter), self.defender)
                    self.match_num += 1
                except StopIteration:
                    self.new_round()
                
            self.timer.tick(self.FPS)
            pygame.display.update()

        with open('out.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for row in self.out_data:
                writer.writerow(row)
        
        pygame.quit()

    def new_round(self):
        """
        Begin a new round, with a new Generation.
        """
        
        self.gen_num += 1
        self.match_num = 1
        print()
        print('New Round: Generation {0}'.format(self.gen_num))
        print('=========')
        self.current_gen = self.current_gen.breed()
        self.gen_iter = iter(self.current_gen)
        self.match = Match(next(self.gen_iter), self.defender)

    def draw_displays(self):
        """
        Generate messages and draw displays to the screen.
        """
        
        genome_text = '{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}:{}'
        genome_text = genome_text.format(*self.match.get_attacker().genome)
        self.genome_display.draw(genome_text, self.screen)

        att_hp_text = 'Attacker HP: {}'
        att_hp_text = att_hp_text.format(self.match.get_attacker().hp)
        self.att_hp_display.draw(att_hp_text, self.screen)

        def_hp_text = 'Defender HP: {}'
        def_hp_text = def_hp_text.format(self.match.get_defender().hp)
        self.def_hp_display.draw(def_hp_text, self.screen)

        gen_text = 'Generation: {}'
        gen_text = gen_text.format(self.gen_num)
        self.gen_display.draw(gen_text, self.screen)

    def log_match(self):
        """
        Logs the match in out_data.
        """
        row = []

        att = self.match.get_attacker()
        
        row.append(self.gen_num)
        row.append(self.match_num)
        row.append(id(att))
        row += att.genome
        row.append(att.match_time / RobotFight.FPS)
        row.append(att.fitness)
        row.append(self.match.end_message)
        row.append(att.left_parent)
        row.append(att.right_parent)

        self.out_data.append(row)


class Display():

    def __init__(self, x, y):
        self.font = pygame.font.Font(None, 25)
        self.display = None
        self.message = None
        self.x = x
        self.y = y

    def draw(self, message, screen):
        """
        Drawn the given message on the display to the screen.
        :param message: Message to be drawn.
        :param screen: Screen to draw message to.
        """
        
        self.display = self.font.render(message, 1, (0, 0, 0))

        rect = self.display.get_rect()
        rect.move_ip(self.x, self.y)

        screen.blit(self.display, rect)
        
    
class Match():

    MAX_TIME = RobotFight.FPS * 60  # One Minute

    def __init__(self, attacker, defender):
        """
        Initialize the match.
        :param attacker: Attacking Robot of the match.
        :param defender: Defending Robot of the match.
        """
        
        self.attacker = pygame.sprite.Group()
        self.defender = pygame.sprite.Group()
        self.att_bullets = pygame.sprite.Group()
        self.def_bullets = pygame.sprite.Group()
        self.att_melee = pygame.sprite.Group()
        self.def_melee = pygame.sprite.Group()

        self.attacker.add(attacker)
        self.defender.add(defender)

        attacker.set_attack_groups(self.att_bullets, self.att_melee)
        defender.set_attack_groups(self.def_bullets, self.def_melee)

        self.running = True

        self.get_attacker()._move_if_clear(
            Robot.WIDTH,
            (RobotFight.SCREEN_HEIGHT - Robot.HEIGHT))
        self.get_defender()._move_if_clear(
            RobotFight.SCREEN_WIDTH - (Robot.WIDTH * 2),
            (RobotFight.SCREEN_HEIGHT - Robot.HEIGHT))

        self.match_timer = 0

        self.end_mesage = ''

    def get_attacker(self):
        return self.attacker.sprites()[0]

    def get_defender(self):
        return self.defender.sprites()[0]
        
    def update(self):
        self.match_timer += 1
        
        self.attacker.update()
        self.defender.update()
        self.att_bullets.update()
        self.def_bullets.update()
        self.att_melee.update()
        self.def_melee.update()

        self.check_collisions()

    def draw(self, screen):
        self.attacker.draw(screen)
        self.defender.draw(screen)
        self.att_bullets.draw(screen)
        self.def_bullets.draw(screen)
        self.att_melee.draw(screen)
        self.def_melee.draw(screen)

    def end(self):
        self.running = False
        self.get_defender().reset()

        self.get_attacker().match_time = self.match_timer

        self.attacker.empty()
        self.defender.empty()
        self.att_bullets.empty()
        self.def_bullets.empty()
        self.att_melee.empty()
        self.def_melee.empty()

    def finished(self):
        if self.get_defender().hp <= 0:
            self.end_message = 'Defender Defeated!'
            return True
        elif self.get_attacker().hp <=0:
            self.end_message = 'Attacker Defeated!'
            return True
        elif self.get_attacker().hit_oob_limit():
            self.end_message = 'Out of Bounds!'
            return True
        elif self.match_timer >= Match.MAX_TIME:
            self.end_message = 'Ran out of time!'
            return True
        else:
            return False

    def check_collisions(self):
        attacker = self.get_attacker()
        defender = self.get_defender()
        
        for bullet in self.att_bullets:
            if pygame.sprite.collide_rect(bullet, defender):
                defender.hit(bullet.DAMAGE)
                bullet.kill()

                attacker.fitness += bullet.DAMAGE

        for bullet in self.def_bullets:
            if pygame.sprite.collide_rect(bullet, attacker):
                attacker.hit(bullet.DAMAGE)
                bullet.kill()

                attacker.fitness -= bullet.DAMAGE

        for melee in self.att_melee:
            if pygame.sprite.collide_rect(melee, defender):
                defender.hit(melee.DAMAGE)
                melee.kill()

                attacker.fitness += melee.DAMAGE

        for melee in self.def_melee:
            if pygame.sprite.collide_rect(melee, attacker):
                attacker.hit(melee.DAMAGE)
                melee.kill()

                attacker.fitness -= melee.DAMAGE

class Generation():

    DEFAULT_MUTATION = 0.02

    @classmethod
    def new_random_generation(cls, size, mutation=DEFAULT_MUTATION):
        """
        Return a new Generation of random robots.
        :param size: Number of robots in Generation.
        :param mutation: Mutation rate for the generation.
        """
        
        robots = []
        
        for i in range(size):
            robots.append(Robot.new_random_robot())

        return cls(robots, mutation)

    def __init__(self, robots, mutation):
        """
        Initialize the Generation.
        :param robots: Robots of this generation.
        :param mutation: Generational mutation rate.
        """
        
        self.robots = robots
        self.mutation = mutation

    def __iter__(self):
        return iter(self.robots)

    def get_size(self):
        return len(self.robots)

    def breed(self):
        """
        Return a new Generation bred from current Generation, using a 2 point
        crossover.
        """

        # Sort by Ascending Match Time
        self.robots.sort(key=lambda x: x.match_time)
        # Then Decending Fitness Score.
        self.robots.sort(key=lambda x: x.fitness, reverse=True)
        # Effectively using time as a tie breaker.

        new_robots = []

        i = 0

        while i < self.get_size():
            if i <= 1:
                bot = self.robots[i]
                bot.reset()
                new_robots.append(bot)

                i += 1
                continue
            
            index_one = random.randint(0, self.get_size() // 2)
            index_two = random.randint(0, self.get_size() // 2)
            while index_one == index_two:
                index_two = random.randint(0, self.get_size() // 2)

            parent_one = self.robots[index_one]
            parent_two = self.robots[index_two]

            child_one, child_two = parent_one.breed_with(parent_two,
                                                         self.mutation)

            if self.get_size() - i > 1:
                new_robots.append(child_one)
                new_robots.append(child_two)

                i += 2
            else:
                new_robots.append(child_one)

                i += 1

        return Generation(new_robots, self.mutation)


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
    OOB_LIMIT = RobotFight.FPS * 3  # 3 Seconds

    @classmethod
    def generate_random_genome(cls):
        return Genome(
            cls.get_random_chest(),
            cls.get_random_base(),
            cls.get_random_weapon(),
            cls.get_random_weapon(),
            cls.get_random_move(),
            cls.get_random_move(),
            cls.get_random_move(),
            cls.get_random_jump(),
            cls.get_random_jump(),
            cls.get_random_jump(),
            cls.get_random_action(),
            cls.get_random_action(),
            cls.get_random_action(),
            cls.get_random_action(),
            cls.get_random_action(),
            cls.get_random_action()
        )

    @classmethod
    def get_random_chest(cls):
        return random.randint(Robot.MIN_CHEST, Robot.MAX_CHEST)

    @classmethod
    def get_random_base(cls):
        return random.randint(Robot.MIN_BASE, Robot.MAX_BASE)

    @classmethod
    def get_random_weapon(cls):
        return random.randint(0, Robot.NUM_WEAPONS)

    @classmethod
    def get_random_move(cls):
        return random.randint(-Robot.MAX_MOVE, Robot.MAX_MOVE)

    @classmethod
    def get_random_jump(cls):
        return random.randint(0, 1)

    @classmethod
    def get_random_action(cls):
        return random.randint(0, 2)

    @classmethod
    def new_random_robot(cls):
        return cls(cls.generate_random_genome())

    @classmethod
    def mutate_genome(self, genome, rate):
        new_genome = []
        for i, value in enumerate(genome):
            if random.random() <= rate:
                if i == 0:
                    new_genome.append(Robot.get_random_chest())
                elif i == 1:
                    new_genome.append(Robot.get_random_base())
                elif i <= 3:
                    new_genome.append(Robot.get_random_weapon())
                elif i <= 6:
                    new_genome.append(Robot.get_random_move())
                elif i <= 9:
                    new_genome.append(Robot.get_random_jump())
                elif i <= 15:
                    new_genome.append(Robot.get_random_action())
                else:
                    new_genome.append(value)
            else:
                new_genome.append(value)

        return Genome(*new_genome)

    @classmethod
    def new_dumb_bot(cls):
        """
        Return a robot that does nothing.
        """
        genome = Genome(
            cls.MAX_CHEST // 2,
            cls.MIN_BASE,
            *[0 for i in range(14)]
            )
        return cls(genome)

    @classmethod
    def new_good_bot(cls):
        """
        Return a robot that does a variety of actions.
        """
        genome = Genome(
            chest_size=int(cls.MAX_CHEST * 0.75),
            base_size=int(cls.MAX_BASE * 0.75),
            arm_one=1,
            arm_two=2,
            move_one=10,
            move_two=0,
            move_three=-10,
            jump_one=0,
            jump_two=0,
            jump_three=1,
            action_one=0,
            action_two=2,
            action_three=1,
            action_four=1,
            action_five=0,
            action_six=1)
        return cls(genome)
            

    def __init__(self, genome, direction=1, color=None,
                 left_parent=0, right_parent=0):
        """
        Initialize the Robot.
        :param genome: Genome used for the Robot.
        :param direction: Direction robot should move. 1 or -1
        :param color: RGB Tuple color of the robot.
        """

        pygame.sprite.Sprite.__init__(self)
        
        self.genome = genome

        self.hp = self.genome.chest_size * 2

        if color is None:
            self.color = (random.randint(10, 245),
                          random.randint(10, 245),
                          random.randint(10, 245))
        else:
            self.color = color

        self.image = pygame.Surface([Robot.WIDTH, Robot.HEIGHT])  # Temporary Values
        self.image.fill(self.color)

        self.rect = self.image.get_rect()

        self.action_phase = 0
        self.action_switch_count = 0

        self.vertical = 0

        self.fitness = 0
        self.match_time = RobotFight.FPS * 60  # One Minute Default

        self.bullet_group = None
        self.melee_group = None

        self.oob_count = 0

        self.direction = direction

        self.left_parent = left_parent
        self.right_parent = right_parent

    def reset(self):
        """
        Reset the changing values of the Robot back to default.
        """
        
        self.hp = self.genome.chest_size * 2
        self.action_phase = 0
        self.action_switch_count = 0
        self.rect.topleft = (0, 0)
        self.fitness = 0
        self.match_time = RobotFight.FPS * 60

    def set_attack_groups(self, bullet, melee):
        """
        Assign PyGame Sprite Groups for bullets and melee attacks.
        :param bullet: Sprite Group for bullets.
        :param melee: Sprite Group for melees.
        """
        
        self.bullet_group = bullet
        self.melee_group = melee

    def update(self):
        if self.action_switch_count >= RobotFight.FPS:
            self.action_phase += 1

            if self.action_phase >= 6:
                self.action_phase = 0

            self.action_switch_count = 0

            self.action()
            self.check_jump()

        self.action_switch_count += 1
        
        self.move()

    def move(self):
        
        if self.action_phase % 3 == 0:
            self._move_if_clear(self.genome.move_one * self.direction, 0)
        elif self.action_phase % 3 == 1:
            self._move_if_clear(self.genome.move_two * self.direction, 0)
        elif self.action_phase % 3 == 2:
            self._move_if_clear(self.genome.move_three * self.direction, 0)

        if not self.on_floor():
            self.vertical += Robot.GRAVITY
            self._move_if_clear(0, self.vertical)

        if self.on_floor():
            if self.vertical != 0:
                self.vertical = 0
            

    def _move_if_clear(self, x, y):
        self.rect.move_ip(x, y)

        if self.rect.x < 0 - Robot.WIDTH:
            self.oob_count += 1
        elif self.rect.x >= RobotFight.SCREEN_WIDTH - Robot.WIDTH:
            self.oob_count += 1
        else:
            if self.oob_count > 0:
                self.oob_count -= 1

        if self.rect.y >= RobotFight.SCREEN_HEIGHT - Robot.HEIGHT:
            self.rect.y = RobotFight.SCREEN_HEIGHT - Robot.HEIGHT

    def on_floor(self):
        return self.rect.y >= RobotFight.SCREEN_HEIGHT - Robot.HEIGHT

    def check_jump(self):
        if self.action_phase % 3 == 0 and self.genome.jump_one:
            self.jump()
        elif self.action_phase % 3 == 1 and self.genome.jump_two:
            self.jump()
        elif self.action_phase % 3 == 2 and self.genome.jump_three:
            self.jump()

    def jump(self):
        self._move_if_clear(0, -1)
        self.vertical = -10 * (self.genome.base_size / self.genome.chest_size)

    def action(self):

        if self.action_phase % 6 == 0:
            action = self.genome.action_one
        elif self.action_phase % 6 == 1:
            action = self.genome.action_two
        elif self.action_phase % 6 == 2:
            action = self.genome.action_three
        elif self.action_phase % 6 == 3:
            action = self.genome.action_four
        elif self.action_phase % 6 == 4:
            action = self.genome.action_five
        elif self.action_phase % 6 == 5:
            action = self.genome.action_six
        
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
        self.bullet_group.add(Bullet(self, self.direction))

    def melee(self):
        self.melee_group.add(MeleeRange(self))

    def hit(self, damage):
        self.hp -= damage

    def hit_oob_limit(self):
        return self.oob_count >= self.OOB_LIMIT

    def breed_with(self, other, mutation):
        start = random.randint(0, len(self.genome) - 1)
        end = random.randint(0, len(self.genome) - 1)

        if start > end:
            start, end = end, start

        child_one = list(self.genome[:start]) \
                    + list(other.genome[start:end]) \
                    + list(self.genome[end:])

        child_two = list(other.genome[:start]) \
                    + list(self.genome[start:end]) \
                    + list(other.genome[end:])

        genome_one = Robot.mutate_genome(Genome(*child_one), mutation)
        genome_two = Robot.mutate_genome(Genome(*child_two), mutation)

        robot_one = Robot(genome_one,
                          left_parent=id(self),
                          right_parent=id(other))
        robot_two = Robot(genome_two,
                          left_parent=id(self),
                          right_parent=id(other))

        return robot_one, robot_two


class Bullet(pygame.sprite.Sprite):

    SPEED = 5
    DAMAGE = 10

    def __init__(self, attacker, direction):
        pygame.sprite.Sprite.__init__(self)

        self.direction = direction

        self.image = pygame.Surface([Robot.HEIGHT / 3, Robot.HEIGHT / 3])
        color = (attacker.color[0] + 10,
                 attacker.color[1] + 10,
                 attacker.color[2] + 10)
        self.image.fill(color)
        
        self.rect = self.image.get_rect()

        self.rect.topleft = attacker.rect.topleft

    def update(self):
        self.rect.x += (Bullet.SPEED * self.direction)
        if self.rect.x < 0 or self.rect.x > RobotFight.SCREEN_WIDTH:
            self.kill()

class MeleeRange(pygame.sprite.Sprite):

    SIZE = Robot.WIDTH
    DAMAGE = 25

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
    game = RobotFight(10, Robot.new_good_bot())
    game.start()
