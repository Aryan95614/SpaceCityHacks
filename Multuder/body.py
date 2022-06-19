import pygame
from Multuder.constants import *
import os
from pygame.locals import *
import random

join = lambda x, y: os.path.join(x, y)
load = lambda x: pygame.image.load(x)
scale = lambda x, y: pygame.transform.scale(load(x), y)
flip = lambda x: pygame.transform.flip(x, True, False)
ranlen = lambda x: range(len(x))

groups = pygame.sprite.Group()
enemies = pygame.sprite.Group()
lasers = pygame.sprite.Group()
lava = pygame.sprite.Group()

shooters = pygame.sprite.Group()
LaserShooter = pygame.sprite.Group()
shootEnemies = pygame.sprite.Group()


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(groups)
        self.right_shooting = scale(join('assets', 'shooting.png'), info['Player Size'])
        self.left_shooting = flip(self.right_shooting)
        self.player_img = scale(join('assets', 'man.png'), info['Player Size'])
        self.walking_img = scale(join('assets', 'man1.png'), info['Player Size'])
        self.right_imgs = [self.player_img, self.walking_img]
        self.left_imgs = list(map(flip, [self.player_img, self.walking_img]))
        self.change = info['Change']
        self.index = 0
        self.image = self.right_imgs[self.index]
        self.width = self.image.get_width() - 20
        self.height = self.image.get_height()
        self.counter = 0
        self.jump_counter = 0
        self.rect = self.player_img.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.on_air = False
        self.jumped = False
        self.shooting = False
        self.direction = 0

    def update(self, screen, world, velocity_on_platform, window):
        self.key = pygame.key.get_pressed()
        dy = 0
        dx = 0
        walk_cooldown = 10
        jump_cooldown = 5

        if self.key[
            pygame.K_SPACE] and self.jumped == False and self.vel_y == 0 and self.jump_counter < jump_cooldown and self.on_air == False:
            self.jump_counter += 5
            self.vel_y = -17
            self.jumped = True

        if self.key[pygame.K_SPACE] is False:
            self.jumped = False
            self.jump_counter = 0

        if self.key[pygame.K_e]:
            self.right_imgs.insert(0, self.right_shooting)
            self.left_imgs.insert(0, self.left_shooting)
            self.shooting = True

        if self.key[pygame.K_j]:
            if self.right_shooting in self.right_imgs:
                self.right_imgs.remove(self.right_shooting)
            if self.left_shooting in self.left_imgs:
                self.left_imgs.remove(self.left_shooting)
            self.shooting = False

        if self.key[pygame.K_a]:
            dx -= self.change
            self.counter += 1
            self.direction = -1

        if self.key[pygame.K_d]:
            dx += self.change
            self.counter += 1
            self.direction = 1

        if self.key[pygame.K_a] == False and self.key[pygame.K_d] == False:
            self.counter = 0
            self.index = 0
            if self.direction == 1:
                self.image = self.right_imgs[self.index]
            if self.direction == -1:
                self.image = self.left_imgs[self.index]

        if self.counter > walk_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.right_imgs):
                self.index = 0
            if self.direction == 1:
                self.image = self.right_imgs[self.index]
            if self.direction == -1:
                self.image = self.left_imgs[self.index]

        self.vel_y += 1
        dy += self.vel_y
        if self.vel_y > 10:
            self.vel_y = 10

        self.on_air = True
        for tile in world.tile_list:

            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0

            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                # jumping
                if self.vel_y < 0:
                    dy = tile[1].bottom - self.rect.top
                    self.vel_y = 0
                # falling
                elif self.vel_y >= 0:
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.on_air = False
                if tile[2] == 9:
                    dx += velocity_on_platform

                if tile[2] == 10:
                    window.playerDead = True
                    window.lose = False

        if self.rect.bottom > info['Size'][1]:
            self.rect.bottom = info['Size'][1]
            dy = 0
        self.rect.x += dx
        self.rect.y += dy

        screen.blit(self.image, self.rect)


class Laser(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(LaserShooter)
        self.image = scale(join('assets', 'laser.png'), info['Laser Size']).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, win, obj):
        self.rect.y -= 5
        if self.rect.midtop == 0:
            self.kill()

        for enemy in obj.enemies:

            if pygame.sprite.collide_rect(self, enemy):
                enemy.kills()
                obj.enemies.remove(enemy)

        win.blit(self.image, self.rect)


class MainPlayer(pygame.sprite.DirtySprite):
    def __init__(self):
        super().__init__(shooters)
        self.image = scale(join('assets', 'Spaceship.png'), info['Player Size'])
        self.rect = self.image.get_rect()
        self.rect.x = 300
        self.rect.y = 600
        self.laser = []
        self.change = 5
        self.counterShooter = 0

    def update(self, win, obj):
        dx = 0
        shoot_cooldown = 1
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_a] and not self.rect.left <= 0:
            dx -= self.change

        if self.keys[pygame.K_d] and not self.rect.right >= info['Shooter_Size'][0]:
            dx += self.change


        if self.keys[pygame.K_SPACE] and self.counterShooter < shoot_cooldown:
            self.counterShooter += 1
            self.laser.append(Laser(self.rect.x, self.rect.y))


        for i in ranlen(self.laser):
            self.laser[i].draw(win, obj)
        if not self.keys[pygame.K_SPACE] and self.counterShooter == shoot_cooldown:
            self.counterShooter = 0

        self.rect.x += dx
        win.blit(self.image, self.rect)


class EnemyShooter(pygame.sprite.DirtySprite):
    def __init__(self, win):
        super().__init__(shootEnemies)
        self.image = scale(join('assets', 'enemy.png'), info['Shooter_Enemy_Size']).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(20, info['Shooter_Size'][1] - 70)
        self.rect.y = random.randint(-20, 0)
        self.change = random.randint(2, 5) * random.choice([1, -1])

    def display(self, win):

        if self.rect.right >= info['Shooter_Size'][1]:
            self.change *= -1
            self.rect.y += 5
            self.rect.x -= 1
        if self.rect.left <= 0:
            self.change *= -1
            self.rect.y += 75
            self.rect.x += 1

        self.rect.x += self.change
        win.blit(self.image, self.rect)

    def kills(self):
        self.rect.x += 2000

class World():
    def __init__(self, data, tile_size):
        self.tile_list = list()
        self.tile_size = (tile_size, tile_size)
        self.dirt_img = scale(join('assets', 'dirt.png'), self.tile_size)
        self.grass_img = scale(join('assets', 'grass_block.png'), self.tile_size)
        self.platform_img = scale(join('assets', 'platform.png'), info['Platform Size'])
        self.velocity = 1

        row_count = 0
        for row in data:
            col_count = 1
            for tile in row:
                if tile == 1:
                    img = self.dirt_img
                    img_rect = img.get_rect()
                    img_rect.x = (col_count * self.tile_size[0]) - self.tile_size[0]
                    img_rect.y = row_count * self.tile_size[1]
                    self.tile_list.append([img, img_rect, tile])
                if tile == 2:
                    img = pygame.transform.scale(self.grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = (col_count * self.tile_size[0]) - self.tile_size[0]
                    img_rect.y = (row_count * self.tile_size[1])
                    tile = (img, img_rect, tile)
                    self.tile_list.append(tile)
                if tile == 9:
                    img = pygame.transform.scale(self.platform_img, (tile_size, tile_size))
                    img_rect = img.get_rect().inflate(-30, -20)
                    img_rect.x = (col_count * self.tile_size[0]) - self.tile_size[0]
                    img_rect.y = (row_count * self.tile_size[1])
                    tile = (img, img_rect, tile)
                    self.tile_list.append(tile)
                if tile == 10:
                    img = pygame.transform.scale(self.grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = (col_count * self.tile_size[0]) - self.tile_size[0]
                    img_rect.y = (row_count * self.tile_size[1])
                    tile = (img, img_rect, tile)
                    self.tile_list.append(tile)

                if tile == 3:
                    enemies.add(enemy(col_count * self.tile_size[0] - 50, row_count * self.tile_size[1]))

                if tile == 6:
                    lava.add(Lava(col_count * self.tile_size[0] - self.tile_size[0], row_count * self.tile_size[1]))
                col_count += 1
            row_count += 1

    def draw(self, screen):
        for tile in ranlen(self.tile_list):
            screen.blit(self.tile_list[tile][0], self.tile_list[tile][1])
            if self.tile_list[tile][2] == 9:
                if self.tile_list[tile][1].left == 150:
                    self.velocity *= -1
                if self.tile_list[tile][1].right == 350:
                    self.velocity *= -1

                self.tile_list[tile][1].left += self.velocity


class Lava(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__(lava)
        self.image = scale(join('assets', 'lava.png'), info['Enemy Size'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class enemy(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__(enemies)
        self.image = scale(join('assets', 'devil.png'), info['Enemy Size'])
        self.rect = self.image.get_rect().inflate(-15, -25)
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self, screen):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class platform(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__(enemies)
        self.image = scale(join('assets', 'platform.png'), info['Platform Size'])
        self.rect = self.image.get_rect()  # .inflate(-15, -25)
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self, screen):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 50:
            self.move_direction *= -1
            self.move_counter *= -1


class laser(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__(enemies)
        self.image = scale(join('assets', 'laser.png'), info['Laser Size'])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, screen):
        pass


class Window():

    def __init__(self):
        self.win = pygame.display.set_mode(info['Size'])
        pygame.display.set_caption('Multuder')
        pygame.display.set_icon(load(join('assets', 'volcano.png')))
        self.sun = scale(join('assets', 'sun.png'), (87, 87))  # convert to sun size
        self.cloud = scale(join('assets', 'clouds.png'), (87, 87))  # convert to cloud size
        self.BasicInfo = pygame.font.SysFont('Helvetica', 20)
        self.WinorLose = pygame.font.SysFont(pygame.font.get_default_font(), 80)
        self.playHeart = 3
        self.text = f'Hearts: {self.playHeart}'
        self.heartInfo = self.BasicInfo.render(f'{self.text}', True, info['White'])
        self.gameover = False
        self.tile_size = info['Size'][0] // 20
        self.winner = self.WinorLose.render('You Win![w]', True, info['White'])
        self.loser = self.WinorLose.render('You Lose![r]', True, info['White'])
        self.world_data = [
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
            [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 0, 0, 0, 2, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
            [1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 10, 10, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
            [1, 0, 2, 0, 0, 7, 9, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 0, 2, 2, 2, 2, 2, 1],
            [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        self.world = World(self.world_data, self.tile_size)
        self.playerDead = False
        self.lose = True
        self.player = Player(100, 620)
        self.clock = pygame.time.Clock()

    def blitwin(self, image, x, y):
        self.win.blit(image, (x, y))

    def update(self):
        self.clock.tick(60)
        self.win.fill(info['Color'])
        self.blitwin(self.sun, 64, 28)
        self.blitwin(self.cloud, 256, 59)
        self.blitwin(self.cloud, 90, 234)
        self.blitwin(self.cloud, 555, 134)
        self.blitwin(self.cloud, 440, 333)

        # self.draw_grid()
        if pygame.sprite.spritecollide(self.player, lava, False) or pygame.sprite.spritecollide(self.player, enemies,
                                                                                                False):
            self.playHeart -= 1
            self.text = f'Hearts: {self.playHeart}'
            self.heartInfo = self.BasicInfo.render(f'{self.text}', True, info['White'])
            self.player.rect.x = 100
            self.player.rect.y = 620

        if self.playHeart == 0:
            self.playerDead = True

        if self.playerDead:
            groups.remove(self.player)
            if self.lose:
                self.blitwin(self.loser, 300, 300)
            else:
                self.blitwin(self.winner, 300, 300)

        else:
            enemies.update(self.win)
            enemies.draw(self.win)

        self.world.draw(self.win)

        lava.update(self.win)
        lava.draw(self.win)

        # self.player.display(self.win, self.world)

        groups.update(self.win, self.world, self.world.velocity, self)
        groups.draw(self.win)

        self.blitwin(self.heartInfo, 600, 32)
        pygame.display.update()

    def draw_grid(self):
        for line in range(0, 20):
            pygame.draw.line(self.win, (255, 255, 255), (0, line * self.tile_size),
                             (info['Size'][0], line * self.tile_size))
            pygame.draw.line(self.win, (255, 255, 255), (line * self.tile_size, 0),
                             (line * self.tile_size, info['Size'][1]))

    def play(self):
        while not self.gameover:
            self.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

        pygame.quit()


class Shooter:

    def __init__(self):
        # set below image to dataclass
        self.background = scale(join('assets', 'Background.jpg'), info['Shooter_Size'])
        self.background_rect = self.background.get_rect()
        self.background_rect.x = 0
        self.background_rect.y = 0
        self.Clock = pygame.time.Clock()
        self.WinorLose = pygame.font.SysFont(pygame.font.get_default_font(), 80)
        self.winner = self.WinorLose.render('You Win![w]', True, info['White'])
        self.loser = self.WinorLose.render('You Lose![r]', True, info['White'])
        self.player = MainPlayer()
        self.win = pygame.display.set_mode(info['Shooter_Size'])
        self.enemies = [EnemyShooter(self.win) for i in range(8)]
        self.gameover = False

    def draw(self, image, rect):
        self.win.blit(image, rect)

    def update(self):
        self.Clock.tick(60)
        self.draw(self.background, self.background_rect)
        self.player.update(self.win, self)

        for i in ranlen(self.enemies):
            self.enemies[i].display(self.win)
            if self.enemies[i].rect.y == 500:
                self.win.blit(self.winner, (100, 200))

        if len(self.enemies) == 0:
            self.win.blit(self.winner, (200, 200))

        pygame.display.update()

    def play(self):
        while not self.gameover:
            self.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True

class ThirdGame:
    def __init__(self):

        self.win = pygame.display.set_mode(info['Third Game'])
        self.gameover = False
        self.keys = pygame.key.get_pressed()
        self.clock = pygame.time.Clock()
        self.x = 200
        self.y = 500
        self.color = (255, 0, 0)

    def update(self):
        self.clock.tick(60)
        self.keys = pygame.key.get_pressed()

        if self.keys[pygame.K_a]:
            self.x -= 1

        if self.keys[pygame.K_d]:
            self.x += 1

        if self.keys[pygame.K_w]:
            self.y -= 1

        if self.keys[pygame.K_s]:
            self.y += 1

        if self.keys[pygame.K_SPACE]:
            self.color = (0, 255, 0)

        if self.keys[pygame.K_t]:
            self.color = (0, 0, 255)

        if self.keys[pygame.K_b]:
            self.color = (255, 0, 0)


        pygame.draw.rect(self.win, self.color, pygame.Rect(self.x, self.y, 60, 20)) # color is red
        pygame.display.update()
    def play(self):

        while not self.gameover:
            self.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameover = True
