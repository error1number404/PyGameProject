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

class Character:
    def __init__(self, x, y, anims_folder_name):
        self.x, self.y = x, y
        self.cur_anim_id = 0
        self.anims_folder_name = anims_folder_name
        self.all_anims_names = ['idle','run','attack','dead','jump','jump-landing']
        self.coun_of_frames_of_anims = {'idle':6,'run':7,'attack':6,'dead':4,'jump':2,'jump-landing':3}
        self.sprite = AnimatedSpriteChar(anims_folder_name + '/idle/idle-0', '.png', 6, x, y,self)
        self.jumping = 0

    def choose_anim(self,id,mirror=False):
        self.cur_anim_id = id
        player_group.empty()
        path = self.anims_folder_name + '/'+self.all_anims_names[id]+'/'+self.all_anims_names[id]+'-0'
        self.sprite = AnimatedSpriteChar(path, '.png', self.coun_of_frames_of_anims[self.all_anims_names[id]], self.x, self.y,self,mirror)

    def move_right(self):
        if self.cur_anim_id == 5:
            self.choose_anim(5)
            self.sprite.x = 5
        elif self.cur_anim_id != 1 or self.sprite.mirror is True:
            self.choose_anim(1)
        else:
            self.sprite.x = 5

    def move_left(self):
        if self.cur_anim_id == 5:
            self.choose_anim(5, True)
            self.sprite.x = -5
        elif self.cur_anim_id != 1 or self.sprite.mirror is False:
            self.choose_anim(1, True)
        else:
            self.sprite.x = -5

    def jump(self):
        if self.cur_anim_id != 4 and not self.sprite.crush:
            self.choose_anim(4)
            self.sprite.crush = False
            self.jumping = 3
            self.sprite.y = -10

    def attack(self):
        if self.cur_anim_id != 2:
            self.choose_anim(2,self.sprite.mirror)


    def clear_move(self):
        self.sprite.y = 0
        self.sprite.x = 0

class AnimatedSpriteChar(pygame.sprite.Sprite):
    def __init__(self, first_name, extension, amount, x, y,person,mirror=False):
        super().__init__(player_group)
        self.frames = []
        self.crush = True
        self.person = person
        self.mirror = mirror
        self.x = 0
        self.y = 0
        for i in range(amount):
            self.frames.append(load_image(first_name+str(i+1)+extension))
            if mirror:
                self.frames[i] = pygame.transform.flip(self.frames[i], True, False)
        self.rect = pygame.Rect(0, 0, self.frames[0].get_width(),self.frames[0].get_height())
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def update(self):
        self.cur_frame += 1
        self.image = self.frames[self.cur_frame % len(self.frames)]
        if not pygame.sprite.collide_mask(self,mountain) and self.crush:
            if self.person.cur_anim_id not in [2,5] or (self.person.cur_anim_id == 2 and self.cur_frame > 6):
                self.person.choose_anim(5)
            self.y = 5
        else:
            self.crush = False
        if self.person.jumping > 0 and self.crush is False:
            self.person.jumping -= 1
            self.y = -10
        self.rect = self.rect.move(self.x, self.y)
        self.person.x += self.x
        self.person.y += self.y

size = width, height = 500, 500
screen = pygame.display.set_mode(size)
all_sprites = pygame.sprite.Group()
player_group = pygame.sprite.Group()
clock = pygame.time.Clock()
player = Character(50, 50, 'Character')
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
            if player.sprite.x == 0 and player.sprite.y == 0 and player.cur_anim_id != 0 and player.sprite.cur_frame > 5 and player.sprite.crush is False:
                player.choose_anim(0,player.sprite.mirror)
            player.clear_move()
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            player.jump()
        elif pygame.key.get_pressed()[pygame.K_RIGHT]:
            player.move_right()
        elif pygame.key.get_pressed()[pygame.K_LEFT]:
            player.move_left()
        elif pygame.key.get_pressed()[pygame.K_f]:
            player.attack()
    screen.fill(pygame.Color("black"))
    player_group.draw(screen)
    all_sprites.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()
