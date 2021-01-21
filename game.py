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
        self.levels = [[0] * 4 for i in range(4)]
        self.cur_level_x = 2
        self.cur_level_y = 2
        self.isLevelChanging = False

    def change_level(self, exit):
        self.isLevelChanging = True
        if exit == 1:
            self.cur_level_y += 1
            self.player.teleport_self(416,68)
        elif exit == 2:
            self.cur_level_y -= 1
            self.player.teleport_self(416,340)
        elif exit == 3:
            self.cur_level_x -= 1
            self.player.teleport_self(835, 372)
        elif exit == 4:
            self.cur_level_x += 1
            self.player.teleport_self(0, 372)
        self.player.update_cur_level()
        self.levels[self.cur_level_x][self.cur_level_y].load_level()
        self.levels[self.cur_level_x][self.cur_level_y].spawn_enemies()
        self.isLevelChanging = False

class level:
    def __init__(self,filename,player):
        self.filename = filename
        self.player = player
        self.enemies = []
        self.isLoaded = False
        self.isCleared = False
        self.isSpawned = False
        self.enemies_group = pygame.sprite.Group()
        self.gui_group = pygame.sprite.Group()
        self.drop = []

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

    def get_tile_properties(self,position,layer):
        return self.map.get_tile_properties(*position,layer)

    def check_is_cleared(self):
        if self.enemies != []:
            for enemy in self.enemies:
                if enemy.hp == 0 and enemy.cur_anim_id == 3 and enemy.is_dead_for > 35:
                    self.enemies_group.remove(enemy)
                    self.gui_group.remove(enemy.hp_sprite[0])
                    del self.enemies[self.enemies.index(enemy)]
        else:
            self.isCleared = True

    def spawn_enemies(self):
        if not self.isSpawned:
            for y in range(self.height):
                for x in range(self.width):
                    if self.get_tile_properties((x,y),3)['spawner'] == 1:
                        self.enemies.append(Enemy('Enemy_',x * self.tile_width - 4*16, y * self.tile_height-6*16,self,self.player))
            self.isSpawned = True

class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, hp,group):
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

    def update(self,x=0,y=0):
        self.image = self.frames[self.hp]
        self.rect = self.rect.move(x, y)

class drop(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, group,type):
        super().__init__(group)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.x = x
        self.y = y
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)
        self.type = type

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y, level, player):
        super().__init__(level.enemies_group)
        self.level = level
        self.player = player
        self.frames = []
        self.react = 0
        self.is_dead_for = 0
        self.cur_frame = 0
        self.crush = True
        self.mirror = False
        self.hp = 2
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        num = random.randint(0,1)
        self.anims_folder_name = anims_folder_name + str(num)
        line = list(map(lambda x: int(x),open('data/enemy_prop.txt','r').readlines()[num].split(',')))
        self.all_anims_names = ['idle','run','attack','dead','landing']
        self.coun_of_frames_of_anims = {}
        for i in range(len(self.all_anims_names)):
            self.coun_of_frames_of_anims[self.all_anims_names[i]] = line[i]
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x, y)
        self.image = self.frames[self.cur_frame]
        self.hp_sprite = [HP(load_image('GUI/Heart.png'), 3, 1, self.x, self.y, 2,self.level.gui_group)]

    def choose_anim(self,id,mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = self.anims_folder_name + '/'+self.all_anims_names[id]+'/'+self.all_anims_names[id]+'_'
        for i in range(self.coun_of_frames_of_anims[self.all_anims_names[id]]):
            self.frames.append(load_image(path + str(i + 1)+'.png'))
            if self.mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def idle_if_need(self):
        if self.x_step == 0 and self.y_step == 0 and self.cur_anim_id not in [0,3] and self.cur_frame > 3 and self.crush is False and self.hp > 0:
            self.choose_anim(0, self.mirror)

    def play_dead_if_need(self):
        if self.hp == 0 and self.cur_anim_id != 3:
            self.choose_anim(3, self.mirror)

    def move(self, k=True,f=1):
        if k:
            if self.cur_anim_id == 4 and self.level.get_tile_properties((self.x//16+4,self.y//16+6),2)['air'] == 1:
                self.choose_anim(4)
                self.x_step = 8 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 8 * f
            else:
                self.x_step = 8 * f
        else:
            if self.cur_anim_id == 4 and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1:
                self.choose_anim(4, True)
                self.x_step = -8 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -8 * f
            else:
                self.x_step = -8 * f

    def move_right(self):
        if self.level.get_tile_properties((self.x // 16 + 5, self.y // 16 + 5), 2)['wall'] == 1:
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if self.level.get_tile_properties((self.x // 16 + 3, self.y // 16 + 5), 2)['wall'] == 1:
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            self.player.hp -= 1

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def drop_items(self):
        if random.randint(0, 10) < 7:
            self.level.drop.append(drop(load_image('drop/hp.png'), 3, 3, self.x + 64, self.y + 80, self.level.gui_group, 'hp'))

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
        if self.player.hp > 0 and self.hp > 0 and self.y // 16 + 4 > self.player.y // 16 and self.y // 16 - 4 < self.player.y // 16 and (self.x // 16 + 16 > self.player.x // 16 and self.x // 16 - 16 < self.player.x // 16):
            self.react += 1
            if self.x // 16 + 1 > self.player.x // 16 and self.x // 16 - 1 < self.player.x // 16 and self.react // 15 > 0:
                self.attack()
                self.react = 0
            elif self.x // 16 + 1 > self.player.x // 16 and self.x // 16 - 1 < self.player.x // 16:
                pass
            elif self.x < self.player.x:
                self.move_right()
            else:
                self.move_left()
        if self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1 and self.crush:
            if self.cur_anim_id not in [2,4] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(4)
            self.y_step = 16
        else:
            self.crush = False
        if self.crush is False and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1:
            self.crush = True
        self.hp_sprite[0].hp = 2 - self.hp
        self.hp_sprite[0].update(self.x_step,self.y_step)
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
        self.crush = True
        self.mirror = False
        self.hp = 4
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.all_anims_names = ['idle','run','attack','dead','jump','landing']
        self.coun_of_frames_of_anims = {'idle':6,'run':8,'attack':6,'dead':6,'jump':4,'landing':1}
        self.jumping = 0
        self.choose_anim(0)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(), self.frames[0].get_height())
        self.rect = self.rect.move(x, y)
        self.image = self.frames[self.cur_frame]
        self.hp_sprite = [HP(load_image('GUI/Heart.png'), 3, 1, 32, 16, 2,player_gui_group),
                          HP(load_image('GUI/Heart.png'), 3, 1, 48, 16, 2,player_gui_group)]

    def update_cur_level(self):
        self.level = self.game.levels[self.game.cur_level_x][self.game.cur_level_y]

    def teleport_self(self,x,y):
        self.rect = pygame.Rect(x, y, self.frames[0].get_width(), self.frames[0].get_height())
        self.x = x
        self.y = y

    def choose_anim(self,id,mirror=False):
        self.mirror = mirror
        self.frames = []
        self.cur_frame = 0
        self.cur_anim_id = id
        path = self.anims_folder_name + '/'+self.all_anims_names[id]+'/'+self.all_anims_names[id]+'_'
        for i in range(self.coun_of_frames_of_anims[self.all_anims_names[id]]):
            self.frames.append(load_image(path + str(i + 1)+'.png'))
            if self.mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def idle_if_need(self):
        if self.x_step == 0 and self.y_step == 0 and self.cur_anim_id not in [0,3] and self.cur_frame > 3 and self.crush is False and self.hp > 0:
            self.choose_anim(0, self.mirror)

    def play_dead_if_need(self):
        if self.hp == 0 and self.cur_anim_id != 3:
            self.choose_anim(3,self.mirror)

    def move(self, k=True,f=1):
        if k:
            if self.cur_anim_id == 5 and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1:
                self.choose_anim(5)
                self.x_step = 16 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 16 * f
            else:
                self.x_step = 16 * f
        else:
            if self.cur_anim_id == 5 and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 +  5), 2)['air'] == 1:
                self.choose_anim(5, True)
                self.x_step = -16 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -16 * f
            else:
                self.x_step = -16 * f

    def move_right(self):
        if self.level.get_tile_properties((self.x // 16 + 6, self.y // 16 + 4), 2)['wall'] == 1 or (not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 6, self.y // 16 + 4), 4)['wall']):
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if self.level.get_tile_properties((self.x // 16 + 2, self.y // 16 + 4), 2)['wall'] == 1 or (not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 2, self.y // 16 + 4), 4)['wall'] == 1):
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)


    def jump(self):
        if self.cur_anim_id not in [4,5] and not self.crush and self.jumping == 0 and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 - 4), 2)['celling'] == 0 and (self.level.isCleared or (not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 - 4), 4)['celling'] == 0)):
            self.choose_anim(4)
            self.crush = True
            self.jumping = 4
            self.y_step = -32

    def jump_off(self):
        if self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['exit'] == 1 and self.level.isCleared:
            self.game.change_level(1)
        elif self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['solid'] == 2 and (self.level.isCleared or (not self.level.isCleared and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 4)['floor'] != 1)):
            self.y_step = 16
            self.choose_anim(4)

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            for enemy in self.level.enemies:
                if enemy.hp != 0:
                    if self.y // 16 + 2 > enemy.y // 16 and self.y // 16 - 2 < enemy.y // 16:
                        if self.x // 16 +1 > enemy.x // 16 and self.x // 16 - 1 < enemy.x // 16:
                            enemy.hp -= 1

    def pickup_drop(self):
        for drop in self.level.drop:
            if self.y // 16 + 6 > drop.y // 16 and self.y // 16 + 2 < drop.y // 16:
                if self.x // 16 + 6 > drop.x // 16 and self.x // 16 + 2 < drop.x // 16:
                    if drop.type == 'hp':
                        if self.hp < 4:
                            self.hp += 1
                            self.level.gui_group.remove(drop)
                            del self.level.drop[self.level.drop.index(drop)]
    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def is_in_exit_tile(self):
        if self.level.isCleared:
            if self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['exit'] != -1:
                return self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['exit']
            if self.level.get_tile_properties((self.x // 16 + 5, self.y // 16 + 4), 2)['exit'] != -1:
                return self.level.get_tile_properties((self.x // 16 + 5, self.y // 16 + 4), 2)['exit']
            elif self.level.get_tile_properties((self.x // 16 + 3, self.y // 16 + 4), 2)['exit'] != -1:
                return self.level.get_tile_properties((self.x // 16 + 3, self.y // 16 + 4), 2)['exit']

    def update(self):
        if self.cur_anim_id == 3:
            if self.cur_frame < 5:
                self.cur_frame += 1
        else:
            self.cur_frame += 1
        self.pickup_drop()
        self.image = self.frames[self.cur_frame % len(self.frames)]
        if self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1 and self.crush:
            if self.cur_anim_id not in [2,5] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(5)
            self.y_step = 16
        else:
            self.crush = False
        if self.jumping > 0 and self.crush:
            self.jumping = 0
        if self.jumping > 0 and self.crush is False:
            self.jumping -= 1
            self.y_step = -32
        elif self.jumping < 1 and self.crush is False and self.level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1:
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
Game.levels[2][2] = (level('data/map/standart_map',Game.player))
Game.levels[3][2] = (level('data/map/standart_map',Game.player))
Game.levels[1][2] = (level('data/map/standart_map',Game.player))
Game.levels[2][3] = (level('data/map/standart_map',Game.player))
Game.levels[2][1] = (level('data/map/standart_map',Game.player))
Game.levels[2][2].load_level()
Game.levels[2][2].spawn_enemies()
Game.player.update_cur_level()
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
        if event.type == update_anims_player:
            player_group.update()
            Game.player.idle_if_need()
            Game.player.play_dead_if_need()
            Game.player.clear_move()
        if event.type == update_anims_enemy:
            Game.levels[Game.cur_level_x][Game.cur_level_y].enemies_group.update()
            for enemy in Game.levels[Game.cur_level_x][Game.cur_level_y].enemies:
                enemy.idle_if_need()
                enemy.play_dead_if_need()
                enemy.clear_move()
        if pygame.key.get_pressed()[pygame.K_SPACE] and Game.player.hp > 0:
            Game.player.jump()
        if pygame.key.get_pressed()[pygame.K_RIGHT] and Game.player.hp > 0:
            Game.player.move_right()
        if pygame.key.get_pressed()[pygame.K_LEFT] and Game.player.hp > 0:
            Game.player.move_left()
        if pygame.key.get_pressed()[pygame.K_f] and Game.player.hp > 0:
            Game.player.attack()
        if pygame.key.get_pressed()[pygame.K_DOWN] and Game.player.hp > 0:
            Game.player.jump_off()
    if Game.player.is_in_exit_tile() and not Game.isLevelChanging:
        Game.change_level(Game.player.is_in_exit_tile())
    screen.blit(background,(0,0))
    Game.levels[Game.cur_level_x][Game.cur_level_y].render(screen)
    player_group.draw(screen)
    Game.levels[Game.cur_level_x][Game.cur_level_y].enemies_group.draw(screen)
    Game.levels[Game.cur_level_x][Game.cur_level_y].gui_group.draw(screen)
    if not Game.levels[Game.cur_level_x][Game.cur_level_y].isCleared:
        Game.levels[Game.cur_level_x][Game.cur_level_y].check_is_cleared()
    player_gui_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()