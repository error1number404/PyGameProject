import pygame
import sys
import os
import pytmx
import random
import pygame_gui
import pickle

pygame.init()
FPS = 60


class shop():
    def open_shop(self):
        if Game.inShop:
            self.manager = 'deleted'  # manager creates another CPU process / pickle can't save objects when it uses in not main process
            self.add_hp_but = 'deleted'
            self.add_attack_but = 'deleted'
        else:
            self.manager = pygame_gui.UIManager((960, 480), 'data/GUI/shop.json')
            self.add_hp_but = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((230, 200), (60, 60)),
                                                           manager=self.manager,
                                                           text='+')
            self.add_attack_but = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((675, 200), (60, 60)),
                                                               manager=self.manager,
                                                               text='+')
        Game.inShop = not Game.inShop

    def button_activity(self, pressed_button):
        if pressed_button == self.add_hp_but and Game.player.coins >= Game.prices[0]:
            Game.player.coins -= Game.prices[0]
            Game.prices[0] += 15
            Game.player.max_hp += 25
        if pressed_button == self.add_attack_but and Game.player.coins >= Game.prices[1]:
            Game.player.coins -= Game.prices[0]
            Game.prices[1] += 15
            Game.player.max_attack_strength += 10


class numbers_for_display(pygame.sprite.Sprite):
    def __init__(self, x, y, number, level, color=[255, 255, 255]):
        super().__init__(numbers_group)
        self.x = x
        self.level = level
        self.y = y
        self.color = color
        self.number = number
        font = pygame.font.Font('data/font/font.ttf', 24)
        self.image = font.render(number, True, color)
        self.rect = pygame.Rect(x, y, 1, 1)
        self.max_frame = 8

    def save(self):
        self.image = 'saved'
        for i in range(len(Game.levels)):
            for j in range(len(Game.levels[0])):
                if Game.levels[i][j] == self.level:
                    self.level_x = i
                    self.level_y = j
        self.level = 'saved'

    def load(self):
        font = pygame.font.Font('data/font/font.ttf', 24)
        self.image = font.render(self.number, True, self.color)
        self.level = Game.levels[self.level_x][self.level_y]

    def update(self):
        if self.max_frame > 0:
            self.max_frame -= 1
            self.rect = self.rect.move(0, -5)
        else:
            numbers_group.remove(self)
            del self.level.numbers[self.level.numbers.index(self)]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return [image, name]


class game():
    def __init__(self):
        self.GUI = []
        self.difficulty = 0
        self.levels = [[None] * 7 for i in range(7)]
        self.cur_level_x = random.randint(0, 6)
        self.cur_level_y = random.randint(0, 6)
        self.isLevelChanging = False
        self.MapIsOpen = False
        self.gameIsStarted = False
        self.player = self.player = Hero('Hero', 16, 372, self)  # surface
        self.inVendorRoom = False
        self.inBossRoom = False
        self.inMenu = False
        self.inShop = False
        self.playerIsDead = False
        self.prices = [50, 50]
        self.tips = [['vendor_tip'], ['variable_tip']]  # [(x,y),'string',requirement,function,isPlayerNear]
        self.Vendor = Vendor(656, 260, self)  # surface

    def save(self):
        for i in range(len(self.levels)):
            for j in range(len(self.levels[0])):
                if self.levels[i][j]:
                    self.levels[i][j].save()
        for i in range(len(self.GUI)):
            self.GUI[i].save()
        self.player.save()
        self.Vendor.save()

    def load(self):
        for i in range(len(self.levels)):
            for j in range(len(self.levels[0])):
                if self.levels[i][j]:
                    self.levels[i][j].load()
        for i in range(len(self.GUI)):
            self.GUI[i].load()
        self.player.load()
        self.Vendor.load()

    def save_game(self, name):
        self.save()
        global player_group, enemies_group, numbers_group, vendor_group
        self.player_group = player_group
        self.enemies_group = enemies_group
        self.numbers_group = numbers_group
        self.vendor_group = vendor_group
        with open(f'data/saves/{name}.dat', 'wb') as file:
            pickle.dump(self, file)
        self.player_group = ''
        self.enemies_group = ''
        self.numbers_group = ''
        self.vendor_group = ''
        self.load()

    def load_game(self, name):
        global Game, player_group, enemies_group, numbers_group, vendor_group
        with open(f'data/saves/{name}.dat', 'rb') as file:
            Game = pickle.load(file)
        player_group = Game.player_group
        enemies_group = Game.enemies_group
        numbers_group = Game.numbers_group
        vendor_group = Game.vendor_group
        Game.load()

    def start_new_game(self):
        global player_group, enemies_group, numbers_group, vendor_group
        player_group = pygame.sprite.Group()
        enemies_group = pygame.sprite.Group()
        numbers_group = pygame.sprite.Group()
        vendor_group = pygame.sprite.Group()
        self.__init__()
        self.gameIsStarted = True
        self.load_vendor_room()

    def unload_game(self):
        global player_group, enemies_group, numbers_group, vendor_group
        player_group.empty()
        enemies_group.empty()
        numbers_group.empty()
        vendor_group.empty()
        self.__init__

    def load_vendor_room(self):
        self.levels = [[None] * 7 for i in range(7)]
        self.inVendorRoom = True
        self.levels[3][3] = level(f'data/map/vendor_room', self.player, self)
        self.levels[3][3].load_level()
        self.player.teleport_self(480, 100)
        self.cur_level_x = 3
        self.cur_level_y = 3
        self.difficulty += 1
        self.player.update_cur_level()

    def generate_map(self):
        self.levels = [[None] * 7 for i in range(7)]
        self.cur_level_x = random.randint(0, 6)
        self.cur_level_y = random.randint(0, 6)
        self.levels[self.cur_level_x][self.cur_level_y] = [0] * 4
        for coun in range(random.randint(16, 25)):
            self.place_room()
        for x in range(len(self.levels)):
            for y in range(len(self.levels[0])):
                if self.levels[x][y] is not None:
                    self.levels[x][y] = level(f'data/map/{"".join(list(map(lambda x: str(x), self.levels[x][y])))}_0',
                                              self.player, self)
        while not self.place_boss_room():
            pass
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
        while not self.choose_type(self.levels[picked_room[0]][picked_room[1]], picked_room[0], picked_room[1]):
            pass

    def place_boss_room(self):
        is_type_picked = False
        boss_type = '0000'
        x = random.randint(1, len(self.levels) - 2)
        y = random.randint(1, len(self.levels[0]) - 2)
        while not is_type_picked:
            if self.levels[x][y] is None:
                if x > 0:
                    if self.levels[x - 1][y]:
                        is_type_picked = True
                        boss_type = '1000'
                    else:
                        if y < len(self.levels[0]) - 1 and self.levels[x][y + 1]:
                            is_type_picked = True
                            boss_type = '0100'
                        else:
                            x = random.randint(0, len(self.levels) - 1)
                            y = random.randint(0, len(self.levels[0]) - 1)
                elif x < len(self.levels) - 1:
                    if self.levels[x + 1][y]:
                        is_type_picked = True
                        boss_type = '0001'
                    else:
                        if y < len(self.levels[0]) - 1 and self.levels[x][y + 1]:
                            is_type_picked = True
                            boss_type = '0100'
                        else:
                            x = random.randint(0, len(self.levels) - 1)
                            y = random.randint(0, len(self.levels[0]) - 1)
            else:
                x = random.randint(0, len(self.levels) - 1)
                y = random.randint(0, len(self.levels[0]) - 1)
        if boss_type == '1000':
            try:
                level_type = list(self.levels[x - 1][y].type)
                level_type[3] = '1'
                self.levels[x - 1][y] = level(f'data/map/{"".join(level_type)}_0',
                                              self.player, self)
            except BaseException:
                return False
        elif boss_type == '0001':
            try:
                level_type = list(self.levels[x - 1][y].type)
                level_type[0] = '1'
                self.levels[x + 1][y] = level(f'data/map/{"".join(level_type)}_0',
                                              self.player, self)
            except BaseException:
                return False
        elif boss_type == '0100':
            try:
                level_type = list(self.levels[x - 1][y].type)
                level_type[2] = '1'
                self.levels[x][y + 1] = level(f'data/map/{"".join(level_type)}_0',
                                              self.player, self)
            except BaseException:
                return False

        self.levels[x][y] = level(f'data/map/{boss_type}_0_boss',
                                  self.player, self)
        self.levels[x][y].isBossRoom = True
        print(x, y)
        return True

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

    def draw_gui(self, screen):
        for gui in self.GUI:
            gui.draw(screen)
        font = pygame.font.Font('data/font/font.ttf', 24)
        text = font.render(f"Уровень подземелья: {self.difficulty}", True, [255, 255, 255])
        screen.blit(text, (16, 76))

    def check_for_loot_on_level_and_show(self, x, y):
        surface = pygame.Surface((60, 30))
        isHpOnLevel = False
        isCoinOnLevel = False
        for i in self.levels[x][y].drop:
            if i.type == 'hp':
                isHpOnLevel = True
            elif i.type == 'coin':
                isCoinOnLevel = True
            if isHpOnLevel and isCoinOnLevel:
                break
        if isHpOnLevel:
            surface.blit(load_image('map/minimap/png/hp.png')[0], (4, 8))
        if isCoinOnLevel:
            surface.blit(load_image('map/minimap/png/coin.png')[0], (32, 4))
        surface = surface.convert()
        colorkey = surface.get_at((0, 0))
        surface.set_colorkey(colorkey)
        return surface

    def load_minimap(self, screen):
        if not self.MapIsOpen:
            minimap = self.load_piece_of_minimap(self.cur_level_x, self.cur_level_y, 120, 60, False, -30, -15)
            minimap.blit(load_image('hero/hat.png')[0], (52, 20))
            screen.blit(minimap, (820, 20))
        else:
            minimap = pygame.Surface((880, 400))
            for x in range(len(self.levels)):
                for y in range(len(self.levels[0])):
                    if self.levels[x][y] is not None and self.levels[x][y].isLoaded:
                        minimap.blit(self.load_piece_of_minimap(x, y, 180, 90, True),
                                     (230 + (x - 1) * 60, 95 + (y - 1) * 30))
            minimap.blit(load_image('hero/hat.png')[0], (252 + self.cur_level_x * 60, 100 + self.cur_level_y * 30))
            screen.blit(minimap, (40, 40))

    def load_piece_of_minimap(self, room_x, room_y, surface_width, surface_height, convert_to_alpha=False, offset_x=0,
                              offset_y=0):
        minimap = pygame.Surface((surface_width, surface_height))
        x_pos = [room_x - 1, room_x, room_x + 1]
        y_pos = [room_y - 1, room_y, room_y + 1]
        neighbours_dict = {0: [room_x - 1, room_y], 1: [room_x, room_y + 1], 2: [room_x, room_y - 1],
                           3: [room_x + 1, room_y], }
        if self.levels[room_x][room_y].isBossRoom:
            minimap.blit(load_image(f'map/minimap/png/{self.levels[room_x][room_y].type}_boss.png')[0],
                         (offset_x + 60 * x_pos.index(room_x), offset_y + 30 * y_pos.index(room_y)))
        else:
            minimap.blit(load_image(f'map/minimap/png/{self.levels[room_x][room_y].type}.png')[0],
                         (offset_x + 60 * x_pos.index(room_x), offset_y + 30 * y_pos.index(room_y)))
        minimap.blit(self.check_for_loot_on_level_and_show(room_x, room_y),
                     (offset_x + 60 * x_pos.index(room_x),
                      offset_y + 30 * y_pos.index(room_y)))
        for i in range(4):
            if self.levels[room_x][room_y].type[i] == '1':
                if self.levels[neighbours_dict[i][0]][neighbours_dict[i][1]].isBossRoom:
                    minimap.blit(load_image(
                        f'map/minimap/png/{self.levels[neighbours_dict[i][0]][neighbours_dict[i][1]].type}_boss.png')[
                                     0],
                                 (offset_x + 60 * x_pos.index(neighbours_dict[i][0]),
                                  offset_y + 30 * y_pos.index(neighbours_dict[i][1])))
                else:
                    minimap.blit(load_image(
                        f'map/minimap/png/{self.levels[neighbours_dict[i][0]][neighbours_dict[i][1]].type}.png')[0],
                                 (offset_x + 60 * x_pos.index(neighbours_dict[i][0]),
                                  offset_y + 30 * y_pos.index(neighbours_dict[i][1])))
                if not self.levels[neighbours_dict[i][0]][neighbours_dict[i][1]].isLoaded:
                    minimap.blit(load_image(f'map/minimap/png/not_visited.png')[0],
                                 (offset_x + 2 + 60 * x_pos.index(neighbours_dict[i][0]),
                                  offset_y + 2 + 30 * y_pos.index(neighbours_dict[i][1])))
                else:
                    minimap.blit(self.check_for_loot_on_level_and_show(neighbours_dict[i][0], neighbours_dict[i][1]),
                                 (offset_x + 60 * x_pos.index(neighbours_dict[i][0]),
                                  offset_y + 30 * y_pos.index(neighbours_dict[i][1])))
        if convert_to_alpha:
            minimap = minimap.convert()
            colorkey = minimap.get_at((0, 0))
            minimap.set_colorkey(colorkey)
        return minimap

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
        if exit == 5:
            self.inVendorRoom = False
            self.generate_map()
        else:
            self.player.update_cur_level()
            self.levels[self.cur_level_x][self.cur_level_y].load_level()
            self.levels[self.cur_level_x][self.cur_level_y].spawn_enemies()
        self.player.invincibleTime = 30
        self.isLevelChanging = False

    def draw_tips(self, screen):
        for tip in self.tips:
            if len(tip) > 1:
                if tip[2](self):
                    if self.player.y // 16 - 6 <= tip[0][1] // 16 <= self.player.y // 16 + 6:
                        if self.player.x // 16 - 3 <= tip[0][0] // 16 <= self.player.x // 16 + 3:
                            if not tip[-1]:
                                self.tips[self.tips.index(tip)][-1] = True
                            font = pygame.font.Font('data/font/font.ttf', 16)
                            text = font.render(tip[1], True, [255, 255, 255])
                            screen.blit(text, tip[0])
                        else:
                            if tip[-1]:
                                self.tips[self.tips.index(tip)][-1] = False


class level:
    def __init__(self, filename, player, game):
        self.filename = filename
        self.game = game
        self.player = player
        self.enemies = []
        self.isLoaded = False
        self.isCleared = False
        self.isSpawned = False
        self.isBossRoom = False
        self.numbers = []
        self.enemies_group = pygame.sprite.Group()
        self.gui_group = pygame.sprite.Group()
        self.drop = []
        self.type = self.filename.split('/')[2][:4]

    def save(self):
        self.player = 'saved'
        self.game = 'saved'
        for i in range(len(self.enemies)):
            self.enemies[i].save()
        for i in range(len(self.drop)):
            self.drop[i].save()
        for i in range(len(self.numbers)):
            self.numbers[i].save()
        if self.isLoaded:
            self.map = 'saved'

    def load(self):
        self.game = Game
        self.player = self.game.player
        for i in range(len(self.enemies)):
            self.enemies[i].load()
        for i in range(len(self.drop)):
            self.drop[i].load()
        for i in range(len(self.numbers)):
            self.numbers[i].load()
        if self.isLoaded:
            self.map = pytmx.load_pygame(f'{self.filename}''.tmx')

    def load_level(self):
        if not self.isLoaded:
            self.map = pytmx.load_pygame(f'{self.filename}''.tmx')  # surface
            self.height = self.map.height
            self.width = self.map.width
            self.tile_width = self.map.tilewidth
            self.tile_height = self.map.tileheight
            if self.isBossRoom:
                for y in range(self.height):
                    for x in range(self.width):
                        try:
                            if self.get_tile_properties((x, y), 1)['description'] == 'vendor_enter':
                                self.game.tips[1] = [(x * 16, (y - 4) * 16), 'Для возвращения на остров, нажмите Е',
                                                     self.check_requirment, self.game.load_vendor_room, False]
                                break
                        except BaseException:
                            pass
            self.isLoaded = True

    def check_requirment(self, obj):
        if obj.levels[obj.cur_level_x][obj.cur_level_y].isCleared and obj.inBossRoom:
            return True
        return False

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
                    del self.enemies[self.enemies.index(enemy)]
        else:
            self.isCleared = True
            if len(self.game.GUI) > 2:
                del self.game.GUI[-1]

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
                        if self.isBossRoom:
                            if self.get_tile_properties((x, y), 3)['boss_spawner'] != '':
                                self.enemies.append(
                                    Boss(self.get_tile_properties((x, y), 3)['boss_spawner'], x * self.tile_width,
                                         y * self.tile_height,
                                         self, self.player, self.game))

                    except BaseException:
                        pass
            self.isSpawned = True


class Projectile(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, shooter, direction, y_offset, max_frame_number, max_attack_strength):
        super().__init__(shooter.level.enemies_group)
        self.frames = []
        self.level = shooter.level
        self.shooter = shooter
        self.max_frame_number = max_frame_number
        self.cut_sheet(sheet[0], columns, rows)
        self.columns = columns
        self.rows = rows
        self.filename = sheet[1]
        self.cur_frame = 0
        self.x = x
        self.y = y
        self.max_attack_strength = max_attack_strength
        if direction:
            self.direction = -1
        else:
            self.direction = 1
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y + y_offset)

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        self.level = 'saved'
        self.shooter.save()

    def load(self):
        self.frames = []
        self.cut_sheet(load_image(self.filename)[0], self.columns, self.rows)
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.level = Game.levels[Game.cur_level_x][Game.cur_level_y]
        self.shooter.load()

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        isHitPlayer = False
        if self.x // 16 == self.level.player.x // 16 and self.y // 16 - 1 <= self.level.player.y // 16 <= self.y // 16 + 1:
            isHitPlayer = True
            attack_strength = random.randint(self.max_attack_strength - 10, self.max_attack_strength)
            if self.level.player.hp - attack_strength < 0:
                self.level.numbers.append(
                    numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                self.level.player.hp = 0
            else:
                self.level.numbers.append(
                    numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                self.level.player.hp -= attack_strength
            self.level.player.showHitTime = 6
            self.level.player.invincibleTime = 20
            if self.direction == -1:
                self.level.player.knockback(1, False)
            else:
                self.level.player.knockback(1, True)
        if self.cur_frame < self.max_frame_number and not isHitPlayer:
            self.image = self.frames[self.cur_frame]
            self.rect = self.rect.move(16 * self.direction, 0)
            self.x += 16 * self.direction
            self.cur_frame += 1
        else:
            del self.shooter.projectiles[self.shooter.projectiles.index(self)]
            self.level.enemies_group.remove(self)


class HP:
    def __init__(self, target, x, y, bar_file, color='Dark Green', text_color=[255, 255, 255]):
        self.target = target
        self.x = x
        self.y = y
        self.color = color
        self.text_color = text_color
        self.bar = load_image(bar_file)[0]
        self.bar_file = bar_file
        self.w = self.bar.get_width()
        self.h = self.bar.get_height()

    def save(self):
        self.bar = 'saved'
        self.target.save()

    def load(self):
        self.bar = load_image(self.bar_file)[0]
        self.target.load()

    def draw(self, screen):
        screen.blit(self.bar, (self.x, self.y))
        pygame.draw.rect(screen, self.color,
                         [self.x + 4, self.y + 4, (self.w - 8) * self.target.hp / self.target.max_hp, self.h - 8])
        font = pygame.font.Font('data/font/font.ttf', 24)
        text = font.render(f"{self.target.hp}/{self.target.max_hp}", True, self.text_color)
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (self.x + (self.w - text_w) / 2, self.y + (self.h - text_h) / 2))


class Coins:
    def __init__(self, target, x, y, coins_file, text_color=[255, 255, 255]):
        self.target = target
        self.x = x
        self.y = y
        self.text_color = text_color
        self.coins = load_image(coins_file)[0]
        self.coins_file = coins_file

    def draw(self, screen):
        screen.blit(self.coins, (self.x, self.y))
        font = pygame.font.Font('data/font/font.ttf', 24)
        text = font.render(f"{self.target.coins}", True, self.text_color)
        text_w = text.get_width()
        text_h = text.get_height()
        screen.blit(text, (self.x + 40, self.y))

    def save(self):
        self.coins = 'saved'
        self.target.save()

    def load(self):
        self.coins = load_image(self.coins_file)[0]
        self.target.load()


class Drop(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, level, type, y_offset=0, coin_value=0):
        super().__init__(level.gui_group)
        self.frames = []
        self.columns = columns
        self.rows = rows
        self.y_offset = y_offset
        self.filename = sheet[1]
        self.cut_sheet(sheet[0], columns, rows)
        self.cur_frame = 0
        self.crush = True
        self.level = level
        self.knockback_time = 0
        self.knockback_direction = 1
        self.x = x
        self.y = y
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y - y_offset)
        self.type = type
        self.x_step = 0
        self.y_step = 0
        if self.type == 'coin':
            self.coin_value = coin_value * random.randint(15, 25)

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        for i in range(len(Game.levels)):
            for j in range(len(Game.levels[0])):
                if self.level == Game.levels[i][j]:
                    self.level_x = i
                    self.level_y = j
        self.level = 'saved'

    def load(self):
        self.frames = []
        self.cut_sheet(load_image(self.filename)[0], self.columns, self.rows)
        self.rect = self.rect.move(self.x, self.y - self.y_offset)
        self.image = self.frames[self.cur_frame]
        self.level = Game.levels[self.level_x][self.level_y]

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

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


class Vendor(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__(vendor_group)
        self.game = game
        self.game.tips[0] = [(x - 64, y - 80), 'Для открытия магазина, нажми E',
                             self.check_requirment, Shop.open_shop, False]
        self.frames = []
        self.cur_frame = 0
        self.x, self.y = x, y
        self.cut_sheet(load_image('vendor/idle.png')[0], 7, 1)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x - 32, y - 60)
        self.image = self.frames[self.cur_frame]

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        self.game = 'saved'

    def load(self):
        self.frames = []
        self.cut_sheet(load_image('vendor/idle.png')[0], 7, 1)
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.game = Game

    def check_requirment(self, obj):
        if obj.inVendorRoom:
            return True
        return False

    def cut_sheet(self, sheet, columns, rows):
        w = sheet.get_width() // columns
        h = sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))

    def update(self):
        self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]


class Enemy(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, level, player):
        super().__init__(level.enemies_group)
        self.afkTime = 0
        self.level = level
        self.reactToAfk = [0, False]
        self.max_attack_strength = 20 + self.level.game.difficulty * 15
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
        self.isRanged = False
        self.hp = 35 + 35 * self.level.game.difficulty
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        num = random.randint(0, 3)
        self.anims_folder_name = anims_folder_name + str(num)
        line = list(map(lambda x: int(x), open('data/enemy_prop.txt', 'r').readlines()[num].split(',')))
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        self.projectiles = []
        if num > 0 and random.choice([True, False]):
            self.isRanged = True
            self.projectile_y_offset = [0, -20, -68, -20][num]
            self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'landing', 'projectile', 'projectile_attack']
        else:
            self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'landing', '_', '_']
        self.coun_of_frames_of_anims = {}
        for i in range(len(self.all_anims_names)):
            self.coun_of_frames_of_anims[self.all_anims_names[i]] = line[i]
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x - 64, y - 84)
        self.image = self.frames[self.cur_frame]

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        self.game = 'saved'
        self.level = 'saved'
        self.player = 'saved'
        self.attack_sound = 'saved'
        for i in range(len(self.projectiles)):
            self.projectiles[i].save()

    def load(self):
        self.choose_anim(self.cur_anim_id, self.mirror)
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.game = Game
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        self.level = self.game.levels[self.game.cur_level_x][self.game.cur_level_y]
        self.player = self.game.player
        for i in range(len(self.projectiles)):
            self.projectiles[i].load()

    def cut_sheet(self, sheet, columns, rows):
        w = sheet.get_width() // columns
        h = sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))
                if self.mirror:
                    self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def choose_anim(self, id, mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = f'{self.anims_folder_name}/{self.all_anims_names[id]}'
        if self.cur_anim_id == 2:
            path += f'_{random.randint(0, 1)}'
        self.cut_sheet(load_image(f'{path}.png')[0],
                       self.coun_of_frames_of_anims[self.all_anims_names[self.cur_anim_id]],
                       1)

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
                                                                              3] and self.cur_frame > \
                self.coun_of_frames_of_anims[
                    self.all_anims_names[self.cur_anim_id]] and self.crush is False and self.hp > 0:
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

    def attack(self, mirror):
        if self.cur_anim_id not in [2, 6]:
            if self.isRanged:
                self.choose_anim(6, mirror)
            else:
                self.choose_anim(2, mirror)
                self.attack_sound.play()
                if self.player.invincibleTime == 0:
                    attack_strength = random.randint(self.max_attack_strength - 10, self.max_attack_strength)
                    if self.player.hp - attack_strength < 0:
                        self.level.numbers.append(
                            numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                        self.player.hp = 0
                    else:
                        self.level.numbers.append(
                            numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                        self.player.hp -= attack_strength
                    self.player.showHitTime = 6
                    self.player.knockback(1, not self.mirror)
                    self.player.invincibleTime = 20

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def do_anything(self):
        if random.choice([True, False]):
            if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 2)['solid'] == 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 4)[
                'solid'] == 0)):
                if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 + 1), 2)['solid'] > 0:
                    self.reactToAfk = [3, True]
        else:
            if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 2)['solid'] == 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 4)[
                'solid'] == 0)):
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
            self.knockback_direction[1] = 1
        else:
            self.knockback_direction[1] = 0

    def colide_trap(self):
        try:
            if self.hp > 0:
                for y in range(2):
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 - y), 3)['trap'] == 1:
                        self.invincibleTime = 30
                        self.showHitTime = 6
                        if self.hp - 30 < 0:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level))
                            self.hp = 0
                        else:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level))
                            self.hp -= 30
                        self.knockback(2, self.mirror)
        except BaseException:
            pass

    def drop_items(self):
        for i in range(random.randint(0, 2)):
            type = random.choice(['coin', 'hp'])
            if type == 'coin':
                coin_value = random.randint(1, 5)
                self.level.drop.append(
                    Drop(load_image(f'drop/{type}_{coin_value}.png'), 1, 1, self.x, self.y, self.level, type, 20,
                         coin_value))
            else:
                self.level.drop.append(
                    Drop(load_image(f'drop/{type}.png'), 8, 1, self.x, self.y, self.level, type, 16))
            self.level.drop[-1].knockback(1, random.choice([True, False]))

    def draw_effects(self):
        if self.showHitTime != 0 and self.cur_anim_id != 3:
            self.image = self.add_some_color(self.image, 180)
            self.showHitTime -= 1
            if self.showHitTime == 0:
                self.choose_anim(self.cur_anim_id, self.mirror)

    def update(self):
        if self.cur_anim_id == 6 and self.cur_frame == self.coun_of_frames_of_anims['projectile_attack']:
            self.projectiles.append(Projectile(load_image(f'{self.anims_folder_name}/{self.all_anims_names[5]}.png'),
                                               self.coun_of_frames_of_anims[self.all_anims_names[5]], 1, self.x,
                                               self.y - 16, self, self.mirror, self.projectile_y_offset,
                                               self.coun_of_frames_of_anims['projectile'],
                                               self.max_attack_strength - 10))
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
            try_to_attack = random.choice([True, False])
            if self.react // 12 > 0 and try_to_attack:
                if not self.isRanged and self.x // 16 <= self.player.x // 16 < self.x // 16 + 3:
                    self.attack(False)
                    self.react = 0
                elif not self.isRanged and self.x // 16 - 3 < self.player.x // 16 <= self.x // 16:
                    self.attack(True)
                    self.react = 0
                elif self.isRanged and self.x // 16 <= self.player.x // 16 < self.x // 16 + 8:
                    self.attack(False)
                    self.react = 0
                elif self.isRanged and self.x // 16 - 8 < self.player.x // 16 <= self.x // 16:
                    self.attack(True)
                    self.react = 0
            elif (self.isRanged and self.x // 16 - 8 < self.player.x // 16 < self.x // 16 + 8) or (
                    not self.isRanged and self.x // 16 - 3 < self.player.x // 16 < self.x // 16 + 3):
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
        if self.isUnstaking:
            self.isUnstaking = False
            self.x_step += 8
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


class Boss(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, level, player, game):
        super().__init__(level.enemies_group)
        self.afkTime = 0
        self.game = game
        self.level = level
        self.max_attack_strength = 60 + self.game.difficulty * 30
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
        self.isRanged = False
        self.isUnstaking = False
        self.max_hp = 150 + 150 * self.game.difficulty
        self.hp = self.max_hp
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.projectiles = []
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        self.projectile_y_offset = -96
        line = list(map(lambda x: int(x), open('data/boss_prop.txt', 'r').readlines()[0].split(',')))
        self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'landing', 'projectile', 'projectile_attack']
        self.coun_of_frames_of_anims = {}
        for i in range(len(self.all_anims_names)):
            self.coun_of_frames_of_anims[self.all_anims_names[i]] = line[i]
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x - 96, y - 108)
        self.image = self.frames[self.cur_frame]
        self.game.GUI.append(HP(self, 408, 16, "GUI/boss_hp_bar.png", 'red'))

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        self.game = 'saved'
        self.level = 'saved'
        self.player = 'saved'
        self.attack_sound = 'saved'
        for i in range(len(self.projectiles)):
            self.projectiles[i].save()

    def load(self):
        self.choose_anim(self.cur_anim_id, self.mirror)
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.game = Game
        self.level = self.game.levels[self.game.cur_level_x][self.game.cur_level_y]
        self.player = self.game.player
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        for i in range(len(self.projectiles)):
            self.projectiles[i].load()

    def cut_sheet(self, sheet, columns, rows):
        w = sheet.get_width() // columns
        h = sheet.get_height() // rows
        for j in range(rows):
            for i in range(columns):
                frame_location = (w * i, h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, (w, h))))
                if not self.mirror:
                    self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def choose_anim(self, id, mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = f'{self.anims_folder_name}/{self.all_anims_names[id]}'
        if self.cur_anim_id == 2:
            path += f'_{random.randint(0, 1)}'
        self.cut_sheet(load_image(f'{path}.png')[0],
                       self.coun_of_frames_of_anims[self.all_anims_names[self.cur_anim_id]],
                       1)

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
                                                                              3] and self.cur_frame > \
                self.coun_of_frames_of_anims[
                    self.all_anims_names[self.cur_anim_id]] and self.crush is False and self.hp > 0:
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

    def attack(self, mirror):
        if self.cur_anim_id not in [2, 6]:
            if self.isRanged:
                self.choose_anim(6, mirror)
            else:
                self.attack_sound.play()
                self.choose_anim(2, mirror)
                if self.player.invincibleTime == 0:
                    attack_strength = random.randint(self.max_attack_strength - 10, self.max_attack_strength)
                    if self.player.hp - attack_strength < 0:
                        self.level.numbers.append(
                            numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                        self.player.hp = 0
                    else:
                        self.level.numbers.append(
                            numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level, [255, 0, 0]))
                        self.player.hp -= attack_strength
                    self.player.showHitTime = 6
                    self.player.knockback(1, not self.mirror)
                    self.player.invincibleTime = 20

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def do_anything(self):
        if random.choice([True, False]):
            if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 2)['solid'] == 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 - 1, self.y // 16), 4)[
                'solid'] == 0)):
                if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 + 1), 2)['solid'] > 0:
                    self.reactToAfk = [3, True]
        else:
            if self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 2)['solid'] == 0 and (
                    self.level.isCleared or (
                    not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 1, self.y // 16), 4)[
                'solid'] == 0)):
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
            self.knockback_direction[1] = 1
        else:
            self.knockback_direction[1] = 0

    def colide_trap(self):
        try:
            if self.hp > 0:
                for y in range(2):
                    if self.level.get_tile_properties((self.x // 16, self.y // 16 - y), 3)['trap'] == 1:
                        self.invincibleTime = 30
                        self.showHitTime = 6
                        if self.hp - 30 < 0:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level))
                            self.hp = 0
                        else:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level))
                            self.hp -= 30
                        self.knockback(2, self.mirror)
        except BaseException:
            pass

    def drop_items(self):
        for i in range(random.randint(3, 8)):
            type = random.choice(['coin', 'hp'])
            if type == 'coin':
                coin_value = random.randint(1, 5)
                self.level.drop.append(
                    Drop(load_image(f'drop/{type}_{coin_value}.png'), 1, 1, self.x, self.y, self.level, type, 20,
                         coin_value))
            else:
                self.level.drop.append(
                    Drop(load_image(f'drop/{type}.png'), 8, 1, self.x, self.y, self.level, type, 16))
            self.level.drop[-1].knockback(2, random.choice([True, False]))

    def draw_effects(self):
        if self.showHitTime != 0 and self.cur_anim_id != 3:
            self.image = self.add_some_color(self.image, 180)
            self.showHitTime -= 1
            if self.showHitTime == 0:
                self.choose_anim(self.cur_anim_id, self.mirror)

    def update(self):
        if self.cur_anim_id != 6:
            self.isTryingToShoot = random.choice([True, False])
        if self.cur_anim_id == 6 and self.cur_frame == self.coun_of_frames_of_anims['projectile_attack']:
            self.projectiles.append(Projectile(load_image(f'{self.anims_folder_name}/{self.all_anims_names[5]}.png'),
                                               self.coun_of_frames_of_anims[self.all_anims_names[5]], 1, self.x - 64,
                                               self.y - 16, self, self.mirror, self.projectile_y_offset,
                                               self.coun_of_frames_of_anims['projectile'],
                                               self.max_attack_strength - 5))
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
            try_to_attack = random.choice([True, False])
            if self.react // 8 > 0 and try_to_attack:
                if self.x // 16 <= self.player.x // 16 < self.x // 16 + 5:
                    self.isRanged = False
                    self.attack(False)
                    self.react = 0
                elif self.x // 16 - 5 < self.player.x // 16 <= self.x // 16:
                    self.isRanged = False
                    self.attack(True)
                    self.react = 0
                elif self.x // 16 <= self.player.x // 16 < self.x // 16 + 7 and self.isTryingToShoot:
                    self.isRanged = True
                    self.attack(False)
                    self.react = 0
                elif self.x // 16 - 7 < self.player.x // 16 <= self.x // 16 and self.isTryingToShoot:
                    self.isRanged = True
                    self.attack(True)
                    self.react = 0
            elif (self.x // 16 - 7 < self.player.x // 16 < self.x // 16 + 7 and self.isTryingToShoot) or (
                    self.x // 16 - 5 < self.player.x // 16 < self.x // 16 + 5):
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
        if self.isUnstaking:
            self.isUnstaking = False
            self.x_step += 8
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


class Hero(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, game):
        super().__init__(player_group)
        self.game = game
        self.level = ''
        self.max_attack_strength = 60
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
        self.hp = 150
        self.coins = 50
        self.max_hp = 150
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.all_anims_names = ['idle', 'run', 'attack', 'dead', 'jump', 'landing']
        self.coun_of_frames_of_anims = {'idle': 6, 'run': 8, 'attack': 6, 'dead': 6, 'jump': 4, 'landing': 1}
        self.jumping = 0
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        self.pickup_drop_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/pickup_drop.mp3')
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x, y)
        self.image = self.frames[self.cur_frame]
        self.game.GUI.append(HP(self, 16, 16, 'GUI/hp_bar.png'))
        self.game.GUI.append(Coins(self, 16, 48, 'GUI/coin.png'))

    def update_cur_level(self):
        self.level = self.game.levels[self.game.cur_level_x][self.game.cur_level_y]
        if self.level.isBossRoom:
            self.game.inBossRoom = True
        else:
            self.game.inBossRoom = False

    def save(self):
        self.image = 'saved'
        self.frames = 'saved'
        self.game = 'saved'
        self.level = 'saved'
        self.attack_sound = 'saved'
        self.pickup_drop_sound = 'saved'

    def load(self):
        self.choose_anim(self.cur_anim_id, self.mirror)
        self.image = self.frames[self.cur_frame % len(self.frames)]
        self.game = Game
        self.update_cur_level()
        self.attack_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/attack.mp3')
        self.pickup_drop_sound = pygame.mixer.Sound(f'data/{self.anims_folder_name}/pickup_drop.mp3')

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
            self.frames.append(load_image(path + str(i + 1) + '.png')[0])
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
        if self.level.get_tile_properties((self.x // 16, self.y // 16 + 2), 2)['exit'] == 1 and self.level.isCleared:
            self.game.change_level(1)
        elif self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 2 and (
                self.level.isCleared or (
                not self.level.isCleared and self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 4)[
            'solid'] != 1)):
            self.y_step = 16
            self.choose_anim(4)

    def attack(self):
        if self.cur_anim_id != 2:
            self.attack_sound.play()
            self.choose_anim(2, self.mirror)
            for enemy in self.level.enemies:
                if enemy.hp != 0:
                    if self.y // 16 + 2 > enemy.y // 16 and self.y // 16 - 2 < enemy.y // 16:
                        if self.x // 16 + 4 > enemy.x // 16 and self.x // 16 - 4 < enemy.x // 16:
                            attack_strength = random.randint(self.max_attack_strength - 15, self.max_attack_strength)
                            if enemy.hp - attack_strength < 0:
                                self.level.numbers.append(
                                    numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level))
                                enemy.hp = 0
                            else:
                                self.level.numbers.append(
                                    numbers_for_display(self.x, self.y, f'-{attack_strength}', self.level))
                                enemy.hp -= attack_strength
                            enemy.showHitTime = 6
                            enemy.knockback(2, not self.mirror)

    def pickup_drop(self):
        for drop in self.level.drop:
            if self.y // 16 + 2 > drop.y // 16 and self.y // 16 - 2 < drop.y // 16:
                if self.x // 16 + 2 > drop.x // 16 and self.x // 16 - 2 < drop.x // 16:
                    if drop.type == 'hp':
                        heal_power = random.randint(50, 60)
                        if self.hp < self.max_hp:
                            self.pickup_color = (0, 180, 0)
                            self.pickup_drop_sound.play()
                            self.showPickupTime = 6
                            if self.hp + heal_power < self.max_hp:
                                self.hp += heal_power
                                self.level.numbers.append(
                                    numbers_for_display(self.x, self.y, f'+{heal_power}', self.level, [0, 255, 0]))
                            else:
                                self.level.numbers.append(
                                    numbers_for_display(self.x, self.y, f'+{heal_power}', self.level, [0, 255, 0]))
                                self.hp = self.max_hp
                            self.level.gui_group.remove(drop)
                            del self.level.drop[self.level.drop.index(drop)]
                    if drop.type == 'coin':
                        self.pickup_drop_sound.play()
                        self.coins += drop.coin_value
                        self.level.numbers.append(
                            numbers_for_display(self.x, self.y, f'+{drop.coin_value}', self.level, [255, 215, 0]))
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
                        if self.hp - 30 < 0:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level, [255, 0, 0]))
                            self.hp = 0
                        else:
                            self.level.numbers.append(
                                numbers_for_display(self.x, self.y, f'-{30}', self.level, [255, 0, 0]))
                            self.hp -= 30
                        self.showHitTime = 6
                        self.knockback(2, not self.mirror)
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

    def check_for_stack(self):
        for y in range(2):
            if self.level.get_tile_properties((self.x // 16, self.y // 16 - y), 2)['solid'] == 1:
                if self.level.get_tile_properties((self.x // 16 - 1, self.y // 16 - y), 2)['solid'] != 1:
                    self.x -= 16
                    self.rect = self.rect.move(-16, 0)
                elif self.level.get_tile_properties((self.x // 16 + 1, self.y // 16 - y), 2)['solid'] != 1:
                    self.x += 16
                    self.rect = self.rect.move(16, 0)

    def update(self):
        self.check_for_stack()
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
            if self.level.get_tile_properties((self.x // 16, self.y // 16 - 1), 2)['solid'] != 1 and \
                    self.level.get_tile_properties((self.x // 16, self.y // 16 - 2), 2)['solid'] != 1:
                self.jumping -= 1
                self.y_step = -32
            else:
                self.jumping = 0
                self.crush = True
        elif self.jumping < 1 and not self.crush and \
                self.level.get_tile_properties((self.x // 16, self.y // 16 + 1), 2)['solid'] == 0:
            self.crush = True
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


class Menu:
    def __init__(self, game, manager):
        self.buttons = {}
        self.game = game
        self.manager = manager
        self.inFrontView = True
        self.saves = []
        self.type = 'start'

    def load_front_view(self):
        if self.type == 'start':
            self.buttons["Save game"].hide()
            self.buttons["Menu exit"].hide()
            self.buttons["Do save"].hide()
            self.text_tip_for_load.kill()
            self.buttons["Exit"].kill()
            self.buttons["New game"].kill()
            self.buttons["Load game"].kill()
            self.buttons["Exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 210), (240, 40)),
                                                                manager=self.manager,
                                                                text='Выход на рабочий стол')
            self.buttons["New game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 70), (240, 40)),
                                                                    manager=self.manager,
                                                                    text='Начать новую игру')
            self.buttons["Load game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 140), (240, 40)),
                                                                     manager=self.manager,
                                                                     text='Загрузить игру')
            self.text_tip_for_load = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 70), (330, 40)),
                                                                 manager=self.manager,
                                                                 text='Выберите сохранение')
        elif self.type == 'ingame':
            self.buttons["New game"].hide()
            self.buttons["Load game"].show()
            self.buttons["Save game"].show()
            self.buttons["Do save"].hide()
            self.buttons["Exit"].kill()
            self.buttons["Menu exit"].kill()
            self.buttons["Load game"].kill()
            self.buttons["Exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 280), (240, 40)),
                                                                manager=self.manager,
                                                                text='Выход на рабочий стол')
            self.buttons["Menu exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 210), (240, 40)),
                                                                     manager=self.manager,
                                                                     text='Выход в главное меню')
            self.buttons["Load game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 140), (240, 40)),
                                                                     manager=self.manager,
                                                                     text='Загрузить игру')
        elif self.type == 'dead':
            self.buttons["Save game"].hide()
            self.buttons["Exit"].kill()
            self.buttons["New game"].kill()
            self.buttons["Load game"].kill()
            self.buttons["Menu exit"].kill()
            self.text_tip_for_load.kill()
            self.buttons["Exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 325), (240, 40)),
                                                                manager=self.manager,
                                                                text='Выход на рабочий стол')
            self.buttons["New game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 115), (240, 40)),
                                                                    manager=self.manager,
                                                                    text='Начать новую игру')
            self.buttons["Load game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 185), (240, 40)),
                                                                     manager=self.manager,
                                                                     text='Загрузить игру')
            self.buttons["Menu exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 255), (240, 40)),
                                                                     manager=self.manager,
                                                                     text='Выход в главное меню')
            self.text_tip_for_load = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((315, 75), (330, 40)),
                                                                 manager=self.manager,
                                                                 text='Выберите сохранение')
        self.inFrontView = True
        self.text_tip_for_save.hide()
        self.text_tip_for_load.hide()
        self.enter_line.hide()
        self.buttons["Do save"].hide()
        for i in self.saves:
            i.hide()

    def load_menu(self):
        self.game.inMenu = True
        self.buttons["New game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 70), (240, 40)),
                                                                manager=self.manager,
                                                                text='Начать новую игру')
        self.buttons["Load game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 140), (240, 40)),
                                                                 manager=self.manager,
                                                                 text='Загрузить игру')
        self.buttons["Exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 210), (240, 40)),
                                                            manager=self.manager,
                                                            text='Выход на рабочий стол')
        self.buttons["Save game"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 70), (240, 40)),
                                                                 manager=self.manager,
                                                                 text='Сохранить игру')
        self.buttons["Menu exit"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((75, 210), (240, 40)),
                                                                 manager=self.manager,
                                                                 text='Выход в главное меню')
        self.buttons["Do save"] = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((345, 210), (240, 40)),
                                                               manager=self.manager,
                                                               text='Сохранить')
        self.enter_line = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((345, 140), (240, 40)),
                                                              manager=self.manager, )
        self.text_tip_for_save = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 70), (330, 40)),
                                                             manager=self.manager,
                                                             text='Введите название для сохранения')
        self.text_tip_for_load = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((300, 70), (330, 40)),
                                                             manager=self.manager,
                                                             text='Выберите сохранение')
        self.load_front_view()

    def change_menu(self):
        if self.type == 'start':
            self.type = 'ingame'
        else:
            self.type = 'start'
        self.load_front_view()

    def load_saves(self):
        k = 0
        for i in os.listdir('data/saves'):
            if os.path.isfile(f'data/saves/{i}') and k < 5:
                if self.type != 'dead':
                    self.saves.append(
                        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((345, 115 + k * 70), (240, 40)),
                                                     manager=self.manager,
                                                     text=f'{i.split(".")[0]}'))
                else:
                    self.saves.append(
                        pygame_gui.elements.UIButton(relative_rect=pygame.Rect((360, 140 + k * 70), (240, 40)),
                                                     manager=self.manager,
                                                     text=f'{i.split(".")[0]}'))
                k += 1

    def draw(self, screen):
        font = pygame.font.Font('data/font/font.ttf', 64)
        if self.type == 'start':
            screen.blit(load_image('GUI/background.png')[0], (0, 0))
        else:
            screen.blit(load_image('GUI/blackout.png')[0], (0, 0))
        if self.type == 'dead':
            text = font.render("Вы проиграли", True, [220, 220, 220])
            screen.blit(text, (354, 0))
        if self.type != 'dead':
            text = font.render("A nightmare about the past", True, [220, 220, 220])
            screen.blit(text, (60, 0))
            tips_font = pygame.font.Font('data/font/font.ttf', 32)
            screen.blit(tips_font.render("Стрелочки влево/вправо - передвижение", True, [220, 220, 220]),(10,380))
            screen.blit(tips_font.render("F - атака", True, [220, 220, 220]), (10, 410))
            screen.blit(tips_font.render("Пробел - прыжок", True, [220, 220, 220]), (10, 440))

    def button_activity(self, pressed_button):
        if pressed_button == self.buttons['Exit']:
            pygame.quit()
        elif pressed_button == self.buttons['New game']:
            self.game.start_new_game()
            self.type = 'start'
            self.change_menu()
            self.game.inMenu = False
        elif pressed_button == self.buttons['Load game']:
            self.inFrontView = False
            self.buttons["New game"].hide()
            self.buttons["Load game"].hide()
            self.buttons["Exit"].hide()
            self.buttons["Save game"].hide()
            self.buttons["Menu exit"].hide()
            self.text_tip_for_load.show()
            self.load_saves()
        elif pressed_button in self.saves:
            self.game.load_game(pressed_button.text)
            global Game
            self.game = Game
            Game.inMenu = False
            if self.type != 'ingame':
                self.change_menu()
        elif pressed_button == self.buttons["Menu exit"]:
            self.game.unload_game()
            self.change_menu()
        elif pressed_button == self.buttons['Save game']:
            self.inFrontView = False
            self.buttons["Save game"].hide()
            self.buttons["Load game"].hide()
            self.buttons["Menu exit"].hide()
            self.buttons["Exit"].hide()
            self.text_tip_for_save.show()
            self.enter_line.show()
            self.buttons["Do save"].show()
        elif pressed_button == self.buttons['Do save']:
            self.game.save_game(self.enter_line.text)
            self.load_front_view()


size = width, height = 960, 480
screen = pygame.display.set_mode(size)
player_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
numbers_group = pygame.sprite.Group()
vendor_group = pygame.sprite.Group()
clock = pygame.time.Clock()
running = True
update_anims_player = pygame.USEREVENT + 1
pygame.time.set_timer(update_anims_player, 60)
update_anims_enemy = pygame.USEREVENT + 2
pygame.time.set_timer(update_anims_enemy, 80)
update_anims_vendor = pygame.USEREVENT + 3
pygame.time.set_timer(update_anims_vendor, 160)
background = load_image('map/background1.png')[0]
minimap_back = load_image('map/minimap/back.png')[0]
map_back = load_image('map/minimap/full_map_back.png')[0]
manager = pygame_gui.UIManager((960, 480), 'data/GUI/gui.json')
Shop = shop()
Game = game()
pygame.mixer.music.load('data/music/loop_scene.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)
menu = Menu(Game, manager)
menu.load_menu()
while running:
    time_delta = clock.tick(FPS) / 1000
    for event in pygame.event.get():
        if Game.player.hp == 0 and Game.player.cur_frame > Game.player.coun_of_frames_of_anims[
            'dead'] - 2 and Game.player.cur_anim_id == 3 and not Game.playerIsDead:
            Game.playerIsDead = True
            Game.inMenu = True
            menu.type = 'dead'
            menu.load_front_view()
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if Game.inShop and not Game.inMenu:
                Shop.open_shop()
            else:
                if not menu.inFrontView:
                    menu.load_front_view()
                elif Game.gameIsStarted and not Game.playerIsDead:
                    Game.inMenu = not Game.inMenu
        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED and Game.inMenu:
                menu.button_activity(event.ui_element)
            elif event.user_type == pygame_gui.UI_BUTTON_PRESSED and Game.inShop:
                Shop.button_activity(event.ui_element)
        manager.process_events(event)
        if Game.inShop:
            Shop.manager.process_events(event)
        if True not in [Game.inMenu, Game.inShop, Game.playerIsDead]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                Game.MapIsOpen = not Game.MapIsOpen
            if not Game.MapIsOpen:
                if event.type == update_anims_player:
                    numbers_group.update()
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
                if event.type == update_anims_vendor:
                    if Game.inVendorRoom:
                        vendor_group.update()
                if Game.player.knockback_time == 0 and Game.player.hp > 0:
                    if pygame.key.get_pressed()[pygame.K_SPACE]:
                        Game.player.jump()
                    if pygame.key.get_pressed()[pygame.K_RIGHT]:
                        Game.player.move_right()
                    if pygame.key.get_pressed()[pygame.K_LEFT]:
                        Game.player.move_left()
                    if pygame.key.get_pressed()[pygame.K_f]:
                        Game.player.attack()
                    if pygame.key.get_pressed()[pygame.K_DOWN]:
                        Game.player.jump_off()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        for tip in Game.tips:
                            if len(tip) > 1:
                                if tip[2](Game) and tip[-1]:
                                    tip[3]()
    screen.blit(background, (0, 0))
    if not Game.inMenu or menu.type != 'start':
        if Game.player.is_in_exit_tile() and not Game.isLevelChanging:
            Game.change_level(Game.player.is_in_exit_tile())
        Game.levels[Game.cur_level_x][Game.cur_level_y].render(screen)
        player_group.draw(screen)
        Game.levels[Game.cur_level_x][Game.cur_level_y].enemies_group.draw(screen)
        Game.levels[Game.cur_level_x][Game.cur_level_y].gui_group.draw(screen)
        if not Game.levels[Game.cur_level_x][Game.cur_level_y].isCleared:
            Game.levels[Game.cur_level_x][Game.cur_level_y].check_is_cleared()
            Game.levels[Game.cur_level_x][Game.cur_level_y].check_for_stacked_enemies()
        numbers_group.draw(screen)
        if Game.inVendorRoom:
            vendor_group.draw(screen)
        Game.draw_tips(screen)
        Game.draw_gui(screen)
        if not Game.MapIsOpen:
            screen.blit(minimap_back, (816, 16))
        else:
            screen.blit(map_back, (32, 32))
        Game.load_minimap(screen)
    if Game.inShop:
        screen.blit(load_image('GUI/shop.png')[0], (120, 120))
        font = pygame.font.Font('data/font/font.ttf', 24)
        screen.blit(font.render('Увеличить максимальное здоровье', True, [255, 255, 255]), (150, 130))
        screen.blit(font.render(f'Цена: {Game.prices[0]}', True, [255, 255, 255]), (230, 170))
        screen.blit(font.render(f'Текущее максимальное здоровье: {Game.player.max_hp}', True, [255, 255, 255]),
                    (150, 280))
        screen.blit(font.render('Увеличить силу атаки', True, [255, 255, 255]), (630, 130))
        screen.blit(font.render(f'Цена: {Game.prices[1]}', True, [255, 255, 255]), (675, 170))
        screen.blit(font.render(f'Текущая сила атаки: {Game.player.max_attack_strength}', True, [255, 255, 255]),
                    (630, 280))
        Shop.manager.update(time_delta)
        Shop.manager.draw_ui(screen)
    if Game.inMenu:
        menu.draw(screen)
        manager.update(time_delta)
        manager.draw_ui(screen)
    clock.tick(FPS)
    pygame.display.flip()
