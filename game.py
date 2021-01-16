import pygame
import sys
import os

pygame.init()
FPS = 60

def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

class Mountain(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image("mountains.png")
        self.rect = self.image.get_rect()
        # вычисляем маску для эффективного сравнения
        self.mask = pygame.mask.from_surface(self.image)
        # располагаем горы внизу
        self.rect.bottom = height

class Character(pygame.sprite.Sprite):
    def __init__(self, anims_folder_name, x, y):
        super().__init__(player_group)
        self.frames = []
        self.cur_frame = 0
        self.crush = True
        self.mirror = False
        self.hp = 100
        self.x_step, self.y_step = 0, 0
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.all_anims_names = ['idle','run','attack','dead','jump','jump-landing']
        self.coun_of_frames_of_anims = {'idle':6,'run':7,'attack':6,'dead':4,'jump':2,'jump-landing':3}
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
        path = self.anims_folder_name + '/'+self.all_anims_names[id]+'/'+self.all_anims_names[id]+'-0'
        for i in range(self.coun_of_frames_of_anims[self.all_anims_names[id]]):
            self.frames.append(load_image(path + str(i + 1)+'.png'))
            if self.mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)

    def move_right(self):
        if self.cur_anim_id == 5 and not pygame.sprite.collide_mask(self,mountain):
            self.choose_anim(5)
            self.x_step = 5
        elif self.cur_anim_id != 1 or self.mirror is True:
            self.choose_anim(1)
            self.x_step = 5
        else:
            self.x_step = 5


    def move_left(self):
        if self.cur_anim_id == 5 and not pygame.sprite.collide_mask(self,mountain):
            self.choose_anim(5, True)
            self.x_step = -5
        elif self.cur_anim_id != 1 or self.mirror is False:
            self.choose_anim(1, True)
            self.x_step = -5
        else:
            self.x_step = -5

    def jump(self):
        if self.cur_anim_id != 4 and not self.crush:
            self.choose_anim(4)
            self.crush = False
            self.jumping = 3
            self.y_step = -10

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2, self.mirror)


    def clear_move(self):
        self.y_step = 0
        self.x_step = 0

    def update(self):
        if self.cur_anim_id == 3:
            if self.cur_frame < 2:
                self.cur_frame += 1
        else:
            self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        if not pygame.sprite.collide_mask(self,mountain) and self.crush:
            if self.cur_anim_id not in [2,5] or (self.cur_anim_id == 2 and self.cur_frame > 6):
                if self.hp > 0:
                    self.choose_anim(5)
            self.y_step = 5
        else:
            self.crush = False
        if self.jumping > 0 and self.crush is False:
            self.jumping -= 1
            self.y_step = -10
        elif self.jumping < 1 and self.crush is False and not pygame.sprite.collide_mask(self,mountain):
            self.crush = True
        self.rect = self.rect.move(self.x_step, self.y_step)
        self.x += self.x_step
        self.y += self.y_step


size = width, height = 500, 500
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
clock = pygame.time.Clock()
player = Character('Character',50, 50)
running = True
update_anims = pygame.USEREVENT + 1
pygame.time.set_timer(update_anims, 80)
mountain = Mountain()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == update_anims:
            player_group.update()
            if player.x_step == 0 and player.y_step == 0 and player.cur_anim_id not in [0,3] and player.cur_frame > 3 and player.crush is False:
                player.choose_anim(0,player.mirror)
            player.clear_move()
        if player.hp == 0 and player.cur_anim_id != 3:
            player.choose_anim(3)
        if pygame.key.get_pressed()[pygame.K_SPACE] and player.hp > 0:
            player.jump()
        elif pygame.key.get_pressed()[pygame.K_RIGHT] and player.hp > 0:
            player.move_right()
        elif pygame.key.get_pressed()[pygame.K_LEFT] and player.hp > 0:
            player.move_left()
        elif pygame.key.get_pressed()[pygame.K_f] and player.hp > 0:
            player.attack()
        elif pygame.key.get_pressed()[pygame.K_z] and player.hp > 0:
            player.hp -= 100

    screen.fill(pygame.Color("black"))
    player_group.draw(screen)
    all_sprites.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
