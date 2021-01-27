import pygame
import sys
import os
import pytmx
import random

pygame.init()
FPS = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


class game():
    def __init__(self):
        self.player = self.player = Hero('Hero', 16, 372, self)
        self.enemies = []
        self.levels = [[None] * 7 for i in range(7)]
        self.cur_level_x = 3
        self.cur_level_y = 3
        self.isLevelChanging = False

    def generate_map(self):
        startroom = [random.choice([0, 1]) for i in range(4)]
        while startroom == [0, 0, 0, 0]:
            startroom = [random.choice([0, 1]) for i in range(4)]
        self.levels[self.cur_level_x][self.cur_level_y] = startroom
        for coun in range(random.randint(16, 40)):
            self.place_room()
        for x in range(len(self.levels)):
            for y in range(len(self.levels[0])):
                if self.levels[x][y] is not None:
                    self.levels[x][y] = level(
                        'data/map/' + ''.join(list(map(lambda x: str(x), self.levels[x][y]))) + '_0', self.player)
        self.cur_level_x = random.randint(0, 6)
        self.cur_level_y = random.randint(0, 6)
        while self.levels[self.cur_level_x][self.cur_level_y] is None:
            self.cur_level_x = random.randint(0, 6)
            self.cur_level_y = random.randint(0, 6)
        self.player.update_cur_level()
        self.levels[self.cur_level_x][self.cur_level_y].load_level()
        self.levels[self.cur_level_x][self.cur_level_y].spawn_enemies()
        x = random.randint(0, 59)
        y = random.randint(0, 29)
        exit = self.levels[self.cur_level_x][self.cur_level_y].get_tile_properties((x, y), 2)['exit']
        while exit == -1:
            exit = self.levels[self.cur_level_x][self.cur_level_y].get_tile_properties((x, y), 2)['exit']
            x = random.randint(0, 59)
            y = random.randint(0, 29)
        if exit == 2:
            self.player.teleport_self(480, 100)
        elif exit == 1:
            self.player.teleport_self(480, 404)
        elif exit == 4:
            self.player.teleport_self(896, 436)
        elif exit == 3:
            self.player.teleport_self(64, 436)

    def place_room(self):
        vacant_places = [[None] * 7 for i in range(7)]
        for x in range(len(self.levels)):
            for y in range(len(self.levels[0])):
                if self.levels[x][y] is not None:
                    if x > 0 and self.levels[x - 1][y] is None:
                        vacant_places[x - 1][y] = 'Placed'
                    if y > 0 and self.levels[x][y - 1] is None:
                        vacant_places[x][y - 1] = 'Placed'
                    if y < len(self.levels[0]) - 1 and self.levels[x][y + 1] is None:
                        vacant_places[x][y + 1] = 'Placed'
                    if x < len(self.levels) - 1 and self.levels[x + 1][y] is None:
                        vacant_places[x + 1][y] = 'Placed'
        picked_room = [random.randint(0, len(self.levels) - 1), random.randint(0, len(self.levels[0]) - 1)]
        while vacant_places[picked_room[0]][picked_room[1]] != 'Placed':
            picked_room = [random.randint(0, len(self.levels) - 1), random.randint(0, len(self.levels[0]) - 1)]
        self.levels[picked_room[0]][picked_room[1]] = [0] * 4
        self.choose_type(self.levels[picked_room[0]][picked_room[1]], picked_room[0], picked_room[1])

    def choose_type(self, room, x, y):
        neighbours = [0] * 4
        if x > 0 and self.levels[x - 1][y] is not None:
            neighbours[0] = 1
        if y < len(self.levels[0]) - 1 and self.levels[x][y + 1] is not None:
            neighbours[1] = 1
        if y > 0 and self.levels[x][y - 1] is not None:
            neighbours[2] = 1
        if x < len(self.levels) - 1 and self.levels[x + 1][y] is not None:
            neighbours[3] = 1
        if neighbours == [0, 0, 0, 0]:
            return False
        ind = random.randint(0, 3)
        while (room[ind] == 1 or neighbours[ind] == 0) and room != [1, 1, 1, 1]:
            ind = random.randint(0, 3)
        if ind == 0:
            self.levels[x - 1][y][3] = 1
            self.levels[x][y][ind] = 1
        elif ind == 1:
            self.levels[x][y + 1][2] = 1
            self.levels[x][y][ind] = 1
        elif ind == 2:
            self.levels[x][y - 1][1] = 1
            self.levels[x][y][ind] = 1
        else:
            self.levels[x + 1][y][0] = 1
            self.levels[x][y][ind] = 1
        return True

    def change_level(self, exit):
        self.isLevelChanging = True
        if exit == 1:
            self.cur_level_y += 1
            self.player.teleport_self(480, 100)
        elif exit == 2:
            self.cur_level_y -= 1
            self.player.teleport_self(480, 404)
        elif exit == 3:
            self.cur_level_x -= 1
            self.player.teleport_self(896, 436)
        elif exit == 4:
            self.cur_level_x += 1
            self.player.teleport_self(64, 436)
        self.player.update_cur_level()
        self.levels[self.cur_level_x][self.cur_level_y].load_level()
        self.levels[self.cur_level_x][self.cur_level_y].spawn_enemies()
        self.player.invincibleTime = 30
        self.isLevelChanging = False


class level:
    def __init__(self, filename, player, type='0000'):
        self.filename = filename
        self.player = player
        self.enemies = []
        self.isLoaded = False
        self.isCleared = False
        self.isSpawned = False
        self.enemies_group = pygame.sprite.Group()
        self.gui_group = pygame.sprite.Group()
        self.drop = []
        self.type = type

    def load_level(self):
        if not self.isLoaded:
            self.map = pytmx.load_pygame(f'{self.filename}''.tmx')
            self.height = self.map.height
            self.width = self.map.width
            self.tile_width = self.map.tilewidth
            self.tile_height = self.map.tileheight
            self.isLoaded = True

    def render(self, screen):
        if self.isCleared:
            layers = 4
        else:
            layers = 5
        for i in range(layers):
            for y in range(self.height):
                for x in range(self.width):
                    image = self.map.get_tile_image(x, y, i)
                    if image is not None:
                        image = image.convert_alpha()
                        screen.blit(image, (x * self.tile_width, y * self.tile_height))

    def get_tile_properties(self, position, layer):
        return self.map.get_tile_properties(*position, layer)

    def check_is_cleared(self):
        if self.enemies != []:
            for enemy in self.enemies:
                if enemy.hp == 0 and enemy.cur_anim_id == 3 and enemy.is_dead_for > 35:
                    self.enemies_group.remove(enemy)
                    self.gui_group.remove(enemy.hp_sprite[0])
                    del self.enemies[self.enemies.index(enemy)]
        else:
            self.isCleared = True

    def check_for_stacked_enemies(self):
        for enemy in self.enemies:
            for another_enemy in self.enemies:
                if enemy != another_enemy:
                    if enemy.x == another_enemy.x and enemy.y == another_enemy.y and not enemy.isUnstaking and not another_enemy.isUnstaking:
                        self.enemies[self.enemies.index(enemy)].isUnstaking = True

    def spawn_enemies(self):
        if not self.isSpawned:
            for y in range(self.height):
                for x in range(self.width):
                    try:
                        if self.get_tile_properties((x, y), 3)['spawner'] == 1:
                            self.enemies.append(
                                Enemy('Enemy_', x * self.tile_width, y * self.tile_height, self, self.player))
                    except BaseException:
                        pass
            self.isSpawned = True


class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, hp, group):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.hp = hp
        self.image = self.frames[self.hp]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self, x=0, y=0):
        self.image = self.frames[self.hp]
        self.rect = self.rect.move(x, y)


class Drop(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, level, type, space_tiles_number=0):
        super().__init__(level.gui_group)
        self.frames = []
        self.space_tiles_number = space_tiles_number
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.crush = True
        self.level = level
        self.knockback_time = 0
        self.knockback_direction = 1
        self.x = x
        self.y = y + 16
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.type = type
        self.x_step = 0
        self.y_step = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))
        for i in range(self.space_tiles_number):
            del self.frames[-1]

    def knockback(self, k, direction):
        self.knockback_time = 2 * k
        way_is_clear = True
        if direction:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 + 1 + tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 + 1 + tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction = 1
            else:
                self.knockback_direction = 0
        else:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 - 1 - tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 - 1 - tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction = -1
            else:
                self.knockback_direction = 0

    def clear_move(self):
        self.x_step = 0
        self.y_step = 0

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if self.knockback_time != 0:
            self.x_step = 16 * self.knockback_direction
            self.y_step = -16 * abs(self.knockback_direction)
            self.knockback_time -= 1
        if self.level.get_tile_properties((self.x // 16, self.y // 16), 2)['solid'] == 0 and self.crush:
            self.y_step = 16
        else:
            self.crush = False
        if self.level.get_tile_properties((self.x // 16, self.y // 16), 2)['solid'] == 0 and not self.crush:
            self.crush = True
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


class Enemy(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, level, player):
        super().__init__(level.enemies_group)
        self.afkTime = 0
        self.level = level
        self.reactToAfk = [0, False]
        self.player = player
        self.invincibleTime = 0
        self.frames = []
        self.react = 0
        self.is_dead_for = 0
        self.cur_frame = 0
        self.showHitTime = 0
        self.knockback_time = 0
        self.knockback_direction = [1, 1]
        self.crush = True
        self.mirror = False
        self.isUnstaking = False
        self.hp = 2
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        num = random.randint(0, 1)
        self.anims_folder_name = anims_folder_name + str(num)
        line = list(map(lambda x: int(x), open('data/enemy_prop.txt', 'r').readlines()[num].split(',')))
        self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'landing']
        self.coun_of_frames_of_anims = {}
        for i in range(len(self.all_anims_names)):
            self.coun_of_frames_of_anims[self.all_anims_names[i]] = line[i]
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x - 32, y - 80)
        self.image = self.frames[self.cur_frame]
        self.hp_sprite = [HP(load_image('GUI/Heart.png'), 3, 1, self.x - 24, self.y - 80, 2, self.level.gui_group)]

    def choose_anim(self, id, mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = f'{self.anims_folder_name}/{self.all_anims_names[id]}/{self.all_anims_names[id]}_'
        for i in range(self.coun_of_frames_of_anims[self.all_anims_names[id]]):
            self.frames.append(load_image(path + str(i + 1) + '.png'))
            if self.mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def add_some_color(self, image, r=0, g=0, b=0):
        w, h = image.get_size()
        for x in range(w):
            for y in range(h):
                color = image.get_at((x, y))
                if r != 0:
                    color[0] = r
                if g != 0:
                    color[1] = g
                if b != 0:
                    color[2] = b
                image.set_at((x, y), color)
        return image

    def idle_if_need(self):
        if self.x_step == 0 and self.y_step == 0 and self.cur_anim_id not in [0,
                                                                              3] and self.cur_frame > 3 and self.crush is False and self.hp > 0:
            self.choose_anim(0, self.mirror)

    def play_dead_if_need(self):
        if self.hp == 0 and self.cur_anim_id != 3:
            self.choose_anim(3, self.mirror)

    def move(self, k=True, f=1):
        if k:
            if self.cur_anim_id == 4 and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)[
                'solid'] == 0:
                self.choose_anim(4)
                self.x_step = 8 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 8 * f
            else:
                self.x_step = 8 * f
        else:
            if self.cur_anim_id == 4 and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)[
                'solid'] == 0:
                self.choose_anim(4, True)
                self.x_step = -8 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -8 * f
            else:
                self.x_step = -8 * f

    def move_right(self):
        if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 2)['solid'] > 0 or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 4)[
            'solid'] > 0):
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 2)['solid'] > 0 or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 4)[
            'solid'] > 0):
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            if self.player.invincibleTime == 0:
                self.player.hp -= 1
                self.player.showHitTime = 6
                self.player.knockback(1, not self.mirror)
                self.player.invincibleTime = 20

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def do_anything(self):
        if random.choice([True, False]):
            if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 2)['solid'] > 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 4)[
                'solid'] > 0)):
                if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 + 1), 2)['solid'] > 0:
                    self.reactToAfk = [3, True]
        else:
            if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 2)['solid'] > 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 4)[
                'solid'] > 0)):
                if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16 + 1), 2)['solid'] > 0:
                    self.reactToAfk = [3, False]

    def knockback(self, k, direction):
        self.knockback_time = 2 * k
        way_is_clear = True
        if direction:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 + 1 + tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 + 1 + tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction[0] = 1
            else:
                self.knockback_direction[0] = 0
        else:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 - 1 - tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 - 1 - tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction[0] = -1
            else:
                self.knockback_direction[0] = 0
        way_is_clear = True
        for tile_in_way in range(1, self.knockback_time + 1):
            try:
                if self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way), 2)[
                    'solid'] == 1 or (
                        not self.level.isCleared and
                        self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way), 4)[
                            'solid'] == 1):
                    way_is_clear = False
            except BaseException:
                way_is_clear = False
        if way_is_clear:
            self.knockback_direction[0] = -1
        else:
            self.knockback_direction[0] = 0

    def colide_trap(self):
        try:
            if self.hp > 0:
                for y in range(2):
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 - y), 3)['trap'] == 1:
                        self.invincibleTime = 30
                        self.hp -= 1
                        self.knockback(2, self.mirror)
        except BaseException:
            pass

    def drop_items(self):
        if random.randint(0, 10) > -1:
            self.level.drop.append(Drop(load_image('drop/hp.png'), 3, 3, self.x, self.y, self.level, 'hp', 1))
            self.level.drop[-1].knockback(1, random.choice([True, False]))

    def draw_effects(self):
        if self.showHitTime != 0 and self.cur_anim_id != 3:
            self.image = self.add_some_color(self.image, 180)
            self.showHitTime -= 1
            if self.showHitTime == 0:
                self.choose_anim(self.cur_anim_id, self.mirror)

    def update(self):
        if self.cur_anim_id == 3:
            if self.is_dead_for == 0:
                self.drop_items()
            if self.cur_frame < self.coun_of_frames_of_anims['dead'] - 1:
                self.cur_frame += 1
            self.is_dead_for += 1
        else:
            self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.draw_effects()
        if self.invincibleTime != 0:
            self.invincibleTime -= 1
        else:
            self.colide_trap()
        if self.knockback_time != 0:
            self.x_step = 16 * self.knockback_direction[0]
            self.y_step = -16 * abs(self.knockback_direction[1])
            self.knockback_time -= 1
        if self.player.hp > 0 and self.hp > 0 and self.y // 16 + 4 > self.player.y // 16 and self.y // 16 - 4 < self.player.y // 16 and (
                self.x // 16 + 16 > self.player.x // 16 and self.x // 16 - 16 < self.player.x // 16):
            self.react += 1
            if self.x // 16 == self.player.x // 16 and self.react // 16 > 0:
                self.attack()
                self.react = 0
            elif self.x // 16 == self.player.x // 16:
                pass
            elif self.x < self.player.x:
                self.move_right()
            else:
                self.move_left()
        elif self.hp > 0:
            self.afkTime += 1
            if self.afkTime // 24 != 0:
                self.afkTime = 0
                if random.choice([True, False]):
                    self.do_anything()
            elif self.reactToAfk[0] != 0:
                if self.reactToAfk[1]:
                    self.move_left()
                else:
                    self.move_right()
                self.reactToAfk[0] -= 1
        if self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 0 and self.crush:
            if self.cur_anim_id not in [2, 4] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(4, self.mirror)
            self.y_step = 16
        else:
            self.crush = False
        if not self.crush and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 0:
            self.crush = True
        self.hp_sprite[0].hp = 2 - self.hp
        if self.isUnstaking:
            self.isUnstaking = False
            self.x_step += 8
        self.hp_sprite[0].update(self.x_step, self.y_step)
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


class Hero(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, game):
        super().__init__(player_group)
        self.game = game
        self.level = ''
        self.frames = []
        self.cur_frame = 0
        self.pickup_color = (0, 0, 0)
        self.showPickupTime = 0
        self.showHitTime = 0
        self.crush = True
        self.mirror = False
        self.invincibleTime = 0
        self.knockback_time = 0
        self.knockback_direction = [1, 1]
        self.hp = 4
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'jump', 'landing']
        self.coun_of_frames_of_anims = {'idle': 6, 'run': 8, 'attack': 6, 'dead': 6, 'jump': 4, 'landing': 1}
        self.jumping = 0
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x, y)
        self.image = self.frames[self.cur_frame]
        self.hp_sprite = [HP(load_image('GUI/Heart.png'), 3, 1, 32, 16, 2, player_gui_group),
                          HP(load_image('GUI/Heart.png'), 3, 1, 48, 16, 2, player_gui_group)]

    def update_cur_level(self):
        self.level = self.game.levels[self.game.cur_level_x][self.game.cur_level_y]

    def teleport_self(self, x, y):
        self.rect = pygame.Rect(x - 64, y - 64, self.frames[0].get_width(), self.frames[0].get_height())
        self.x = x
        self.y = y

    def add_some_color(self, image, r=0, g=0, b=0):
        w, h = image.get_size()
        for x in range(w):
            for y in range(h):
                color = image.get_at((x, y))
                if r != 0:
                    color[0] = r
                if g != 0:
                    color[1] = g
                if b != 0:
                    color[2] = b
                image.set_at((x, y), color)
        return image

    def choose_anim(self, id, mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = f'{self.anims_folder_name}/{self.all_anims_names[id]}/{self.all_anims_names[id]}_'
        for i in range(self.coun_of_frames_of_anims[self.all_anims_names[id]]):
            self.frames.append(load_image(path + str(i + 1) + '.png'))
            if self.mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def idle_if_need(self):
        if self.x_step == 0 and self.y_step == 0 and self.cur_anim_id not in [0,
                                                                              3] and self.cur_frame > 3 and self.crush is False and self.hp > 0:
            self.choose_anim(0, self.mirror)

    def play_dead_if_need(self):
        if self.hp == 0 and self.cur_anim_id != 3:
            self.choose_anim(3, self.mirror)

    def move(self, k=True, f=1):
        if k:
            if self.cur_anim_id == 5 and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)[
                'solid'] == 0:
                self.choose_anim(5)
                self.x_step = 16 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 16 * f
            else:
                self.x_step = 16 * f
        else:
            if self.cur_anim_id == 5 and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)[
                'solid'] == 0:
                self.choose_anim(5, True)
                self.x_step = -16 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -16 * f
            else:
                self.x_step = -16 * f

    def move_right(self):
        if self.level.get_tile_properties((self.x // 16 + 2, self.y // 16), 2)['solid'] > 0 or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 2, self.y // 16), 4)[
            'solid'] > 0):
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if self.level.get_tile_properties((self.x // 16 - 2, self.y // 16), 2)['solid'] > 0 or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16 - 2, self.y // 16), 4)[
            'solid'] > 0):
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)

    def jump(self):
        if self.cur_anim_id not in [4, 5] and not self.crush and self.jumping == 0:
            way_is_clear = True
            for tile_in_way in range(1, 11):
                try:
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way), 2)['solid'] != 1 and (
                            self.level.isCleared or (not self.level.isCleared and self.level.get_tile_properties(
                            (self.x // 16, self.y // 16 - tile_in_way), 4)['solid'] != 1)):
                        pass
                    else:
                        way_is_clear = False
                        self.jumping = tile_in_way // 2 - 2
                except BaseException:
                    way_is_clear = False
                    try:
                        if self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way + 2), 2)[
                            'exit'] != -1 and self.level.isCleared:
                            self.jumping = tile_in_way // 2
                    except BaseException:
                        self.jumping = tile_in_way // 2 - 2
            if way_is_clear:
                self.choose_anim(4, self.mirror)
                self.crush = True
                self.jumping = 5
            elif self.jumping != 0:
                self.choose_anim(4, self.mirror)
                self.crush = True

    def jump_off(self):
        if self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['exit'] == 1 and self.level.isCleared:
            self.game.change_level(1)
        elif self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 2 and (
                self.level.isCleared or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 4)[
            'solid'] != 1)):
            self.y_step = 16
            self.choose_anim(4)

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            for enemy in self.level.enemies:
                if enemy.hp != 0:
                    if self.y // 16 + 2 > enemy.y // 16 and self.y // 16 - 2 < enemy.y // 16:
                        if self.x // 16 + 4 > enemy.x // 16 and self.x // 16 - 4 < enemy.x // 16:
                            enemy.hp -= 1
                            enemy.showHitTime = 6
                            enemy.knockback(2, not self.mirror)

    def pickup_drop(self):
        for drop in self.level.drop:
            if self.y // 16 + 2 > drop.y // 16 and self.y // 16 - 2 < drop.y // 16:
                if self.x // 16 + 2 > drop.x // 16 and self.x // 16 - 2 < drop.x // 16:
                    if drop.type == 'hp':
                        if self.hp < 4:
                            self.pickup_color = (0, 180, 0)
                            self.showPickupTime = 6
                            self.hp += 1
                            self.level.gui_group.remove(drop)
                            del self.level.drop[self.level.drop.index(drop)]

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def knockback(self, k, direction):
        self.knockback_time = 2 * k
        way_is_clear = True
        if direction:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 + 2 + tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 + 2 + tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction[0] = 1
            else:
                self.knockback_direction[0] = 0
        else:
            for tile_in_way in range(1, self.knockback_time + 1):
                try:
                    if self.level.get_tile_properties((self.x // 16 - 2 - tile_in_way, self.y // 16), 2)[
                        'solid'] > 0 or (
                            not self.level.isCleared and
                            self.level.get_tile_properties((self.x // 16 - 2 - tile_in_way, self.y // 16), 4)[
                                'solid'] > 0):
                        way_is_clear = False
                except BaseException:
                    way_is_clear = False
            if way_is_clear:
                self.knockback_direction[0] = -1
            else:
                self.knockback_direction[0] = 0
        way_is_clear = True
        for tile_in_way in range(1, self.knockback_time + 1):
            try:
                if self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way), 2)[
                    'solid'] == 1 or (
                        not self.level.isCleared and
                        self.level.get_tile_properties((self.x // 16, self.y // 16 - tile_in_way), 4)[
                            'solid'] == 1):
                    way_is_clear = False
            except BaseException:
                way_is_clear = False
        if way_is_clear:
            self.knockback_direction[1] = 2
        else:
            self.knockback_direction[1] = 0

    def colide_trap(self):
        try:
            if self.hp > 0:
                for y in range(4):
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 - y), 3)['trap'] == 1:
                        self.invincibleTime = 30
                        self.hp -= 1
                        self.knockback(2, self.mirror)
        except BaseException:
            pass

    def is_in_exit_tile(self):
        if self.level.isCleared:
            try:
                for tile_in_way in range(2):
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 + 1 - tile_in_way), 2)['exit'] != -1:
                        return self.level.get_tile_properties((self.x // 16, self.y // 16 + 2 - tile_in_way), 2)['exit']
                    if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16 - tile_in_way), 2)['exit'] != -1:
                        return self.level.get_tile_properties((self.x // 16 + 1, self.y // 16 - tile_in_way), 2)['exit']
                    elif self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 - tile_in_way), 2)[
                        'exit'] != -1:
                        return self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 - tile_in_way), 2)['exit']
            except BaseException:
                pass

    def draw_effects(self):
        if self.showHitTime != 0 and self.cur_anim_id != 3:
            self.image = self.add_some_color(self.image, 180)
            self.showHitTime -= 1
            if self.showHitTime == 0:
                self.choose_anim(self.cur_anim_id, self.mirror)
        if self.showPickupTime != 0 and self.cur_anim_id != 3:
            self.image = self.add_some_color(self.image, *self.pickup_color)
            self.showPickupTime -= 1
            if self.showPickupTime == 0:
                self.choose_anim(self.cur_anim_id, self.mirror)

    def update(self):
        if self.cur_anim_id in [3]:
            if self.cur_frame < 5:
                self.cur_frame += 1
        else:
            self.cur_frame += 1
        if self.invincibleTime != 0:
            self.invincibleTime -= 1
        else:
            self.colide_trap()
        if self.knockback_time != 0:
            self.x_step = 16 * self.knockback_direction[0]
            self.y_step = -16 * abs(self.knockback_direction[1])
            self.knockback_time -= 1
        self.pickup_drop()
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.draw_effects()
        if self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 0 and self.crush:
            if self.cur_anim_id not in [2, 5] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(5, self.mirror)
            self.y_step = 16
        else:
            self.crush = False
        if self.jumping > 0 and self.crush:
            self.jumping = 0
        if self.jumping > 0 and self.crush is False:
            self.jumping -= 1
            self.y_step = -32
        elif self.jumping < 1 and not self.crush and \
                self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 0:
            self.crush = True
        if self.hp > 2:
            if self.hp > 3:
                self.hp_sprite[1].hp = 0
            else:
                self.hp_sprite[1].hp = 1
            self.hp_sprite[0].hp = 0
        elif self.hp == 2:
            self.hp_sprite[0].hp = 0
            self.hp_sprite[1].hp = 2
        elif self.hp == 1:
            self.hp_sprite[1].hp = 2
            self.hp_sprite[0].hp = 1
        else:
            self.hp_sprite[0].hp = 2
            self.hp_sprite[1].hp = 2
        for i in range(2):
            self.hp_sprite[i].update()
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


size = width, height = 960, 480
screen = pygame.display.set_mode(size)
player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
player_gui_group = pygame.sprite.Group()
clock = pygame.time.Clock()
Game = game()
Game.generate_map()
running = True
update_anims_player = pygame.USEREVENT + 1
pygame.time.set_timer(update_anims_player, 60)
update_anims_enemy = pygame.USEREVENT + 2
pygame.time.set_timer(update_anims_enemy, 80)
background = load_image('map/background1.png')
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            Game.levels[Game.cur_level_x][Game.cur_level_y].drop.append(
                Drop(load_image('drop/hp.png'), 3, 3, event.pos[0], (event.pos[1] // 16) * 16,
                     Game.levels[Game.cur_level_x][Game.cur_level_y], 'hp',
                     1))
        if event.type == update_anims_player:
            player_group.update()
            Game.player.idle_if_need()
            Game.player.play_dead_if_need()
            Game.player.clear_move()
            Game.levels[Game.cur_level_x][Game.cur_level_y].gui_group.update()
            for drop_ in Game.levels[Game.cur_level_x][Game.cur_level_y].drop:
                drop_.clear_move()
        if event.type == update_anims_enemy:
            Game.levels[Game.cur_level_x][Game.cur_level_y].enemies_group.update()
            for enemy in Game.levels[Game.cur_level_x][Game.cur_level_y].enemies:
                enemy.idle_if_need()
                enemy.play_dead_if_need()
                enemy.clear_move()
        if Game.player.knockback_time == 0 and Game.player.hp > 0:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                Game.player.jump()
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                # Game.levels[Game.cur_level_x][Game.cur_level_y].enemies[0].move_right()
                Game.player.move_right()
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                # Game.levels[Game.cur_level_x][Game.cur_level_y].enemies[0].move_left()
                Game.player.move_left()
            if pygame.key.get_pressed()[pygame.K_f]:
                Game.player.attack()
            if pygame.key.get_pressed()[pygame.K_DOWN]:
                Game.player.jump_off()
    if Game.player.is_in_exit_tile() and not Game.isLevelChanging:
        Game.change_level(Game.player.is_in_exit_tile())
    screen.blit(background, (0, 0))
    Game.levels[Game.cur_level_x][Game.cur_level_y].render(screen)
    player_group.draw(screen)
    Game.levels[Game.cur_level_x][Game.cur_level_y].enemies_group.draw(screen)
    Game.levels[Game.cur_level_x][Game.cur_level_y].gui_group.draw(screen)
    if not Game.levels[Game.cur_level_x][Game.cur_level_y].isCleared:
        Game.levels[Game.cur_level_x][Game.cur_level_y].check_is_cleared()
        Game.levels[Game.cur_level_x][Game.cur_level_y].check_for_stacked_enemies()
    player_gui_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()