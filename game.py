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

class level:
    def __init__(self,filename):
        self.map = pytmx.load_pygame(f'{filename}''.tmx')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_width = self.map.tilewidth
        self.tile_height = self.map.tileheight
        self.layers = []

    def render(self, screen):
        for i in range(4):
            for y in range(self.height):
                for x in range(self.width):
                    image=self.map.get_tile_image(x, y, i)
                    if image is not None:
                        image = image.convert_alpha()
                        screen.blit(image, (x * self.tile_width, y * self.tile_height))

    def get_tile_id(self, position,layer):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position,layer)]

    def get_tile_properties(self,position,layer):
        return self.map.get_tile_properties(*position,layer)

class HP(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y, hp):
        super().__init__(gui_group)
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

    def update(self):
        self.image = self.frames[self.hp]

class Enemy(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y):
        super().__init__(enemies_group)
        self.frames = []
        self.react = 0
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

    def move(self, k=True,f=1):
        if k:
            if self.cur_anim_id == 4 and level.get_tile_properties((self.x//16+4,self.y//16+6),2)['air'] == 1:
                self.choose_anim(4)
                self.x_step = 10 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 10 * f
            else:
                self.x_step = 10 * f
        else:
            if self.cur_anim_id == 4 and level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1:
                self.choose_anim(4, True)
                self.x_step = -10 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -10 * f
            else:
                self.x_step = -10 * f

    def move_right(self):
        if level.get_tile_properties((self.x // 16 + 6, self.y // 16 + 5), 2)['wall'] == 1:
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if level.get_tile_properties((self.x // 16 + 2, self.y // 16 + 5), 2)['wall'] == 1:
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            player.hp -= 1

    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def update(self):
        if self.cur_anim_id == 3:
            if self.cur_frame < self.coun_of_frames_of_anims['dead'] - 1:
                self.cur_frame += 1
        else:
            self.cur_frame += 1
        self.react += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        if self.y // 16 + 4 > player.y // 16 and self.y // 16 - 4 < player.y // 16 and player.hp > 0 and self.hp > 0:
            if self.x // 16 + 1 > player.x // 16 and self.x // 16 - 1 < player.x // 16 and self.react // 10 > 0:
                self.attack()
                self.react = 0
            elif self.x // 16 + 1 > player.x // 16 and self.x // 16 - 1 < player.x // 16:
                pass
            elif self.x < player.x:
                self.move_right()
            else:
                self.move_left()
        if level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1 and self.crush:
            if self.cur_anim_id not in [2,4] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(4)
            self.y_step = 10
        else:
            self.crush = False
        if self.crush is False and level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 6), 2)['air'] == 1:
            self.crush = True
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step

class Hero(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y):
        super().__init__(player_group)
        self.frames = []
        self.cur_frame = 0
        self.crush = True
        self.mirror = False
        self.hp = 4
        self.hp_sprite = [HP(load_image('GUI/Heart.png'),3,1,32,16,2),HP(load_image('GUI/Heart.png'),3,1,48,16,2)]
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

    def move(self, k=True,f=1):
        if k:
            if self.cur_anim_id == 5 and level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1:
                self.choose_anim(5)
                self.x_step = 15 * f
            elif self.cur_anim_id != 1 or self.mirror is True:
                self.choose_anim(1)
                self.x_step = 15 * f
            else:
                self.x_step = 15 * f
        else:
            if self.cur_anim_id == 5 and level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1:
                self.choose_anim(5, True)
                self.x_step = -15 * f
            elif self.cur_anim_id != 1 or self.mirror is False:
                self.choose_anim(1, True)
                self.x_step = -15 * f
            else:
                self.x_step = -15 * f

    def move_right(self):
        if level.get_tile_properties((self.x // 16 + 6, self.y // 16 + 4), 2)['wall'] == 1:
            self.move(True, 0)
        elif self.cur_anim_id != 2:
            self.move()

    def move_left(self):
        if level.get_tile_properties((self.x // 16 + 2, self.y // 16 + 4), 2)['wall'] == 1:
            self.move(False, 0)
        elif self.cur_anim_id != 2:
            self.move(False)

    def jump(self):
        if self.cur_anim_id not in [4,5] and not self.crush and self.jumping == 0:
            self.choose_anim(4)
            self.crush = True
            self.jumping = 4
            self.y_step = -30

    def jump_off(self):
        if level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['solid'] == 2:
            self.y_step = 10

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)
            if self.y // 16 + 2 > enemy.y // 16 and self.y // 16 - 2 < enemy.y // 16:
                if self.x // 16 +1 > enemy.x // 16 and self.x // 16 - 1 < enemy.x // 16:
                    enemy.hp -= 1


    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def update(self):
        if self.cur_anim_id == 3:
            if self.cur_frame < 5:
                self.cur_frame += 1
        else:
            self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        if level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1 and self.crush:
            if self.cur_anim_id not in [2,5] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(5)
            self.y_step = 10
        else:
            self.crush = False
        if self.jumping > 0 and self.crush:
            self.jumping = 0
        if self.jumping > 0 and self.crush is False:
            self.jumping -= 1
            self.y_step = -30
        elif self.jumping < 1 and self.crush is False and level.get_tile_properties((self.x // 16 + 4, self.y // 16 + 5), 2)['air'] == 1:
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
gui_group = pygame.sprite.Group()
clock = pygame.time.Clock()
player = Hero('Hero', 400, 50)
enemy = Enemy('Enemy_',50,50)
running = True
update_anims_player = pygame.USEREVENT + 1
pygame.time.set_timer(update_anims_player, 60)
update_anims_enemy = pygame.USEREVENT + 2
pygame.time.set_timer(update_anims_enemy, 80)
background = load_image('map/background1.png')
level = level('data/map/standart_map')
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == update_anims_player:
            player_group.update()
            if player.x_step == 0 and player.y_step == 0 and player.cur_anim_id not in [0, 3] and player.cur_frame > 3 and player.crush is False and player.hp > 0:
                player.choose_anim(0, player.mirror)
            player.clear_move()
            print(enemy.hp, player.hp)
        if event.type == update_anims_enemy:
            enemies_group.update()
            if enemy.x_step == 0 and enemy.y_step == 0 and enemy.cur_anim_id not in [0,
                                                                                     3] and enemy.cur_frame > 3 and enemy.crush is False and enemy.hp > 0:
                enemy.choose_anim(0, enemy.mirror)
            enemy.clear_move()
        if player.hp == 0 and player.cur_anim_id != 3:
            player.choose_anim(3,player.mirror)
        if enemy.hp == 0 and enemy.cur_anim_id != 3:
            enemy.choose_anim(3,enemy.mirror)
        if pygame.key.get_pressed()[pygame.K_SPACE] and player.hp > 0:
            player.jump()
        if pygame.key.get_pressed()[pygame.K_RIGHT] and player.hp > 0:
            player.move_right()
        if pygame.key.get_pressed()[pygame.K_LEFT] and player.hp > 0:
            player.move_left()
        if pygame.key.get_pressed()[pygame.K_f] and player.hp > 0:
            player.attack()
        if pygame.key.get_pressed()[pygame.K_DOWN] and player.hp > 0:
            player.jump_off()
        if pygame.key.get_pressed()[pygame.K_z] and player.hp > 0:
            enemy.hp -= 100
    screen.blit(background,(0,0))
    level.render(screen)
    player_group.draw(screen)
    enemies_group.draw(screen)
    gui_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
