import pygame
import random
import os

FPS = 60
WIDTH = 500
HEIGHT = 600

GREEN = (0,255,0)
REALWHITE = (255,255,255)
WHITE = (253,245,230)
RED = (255,0,0)
YELLOW = (255,255,0)
BLACK = (0,0,0)

#遊戲初始化,遊戲視窗
pygame.init()
screen = pygame.display.set_mode((WIDTH,HEIGHT)) #視窗大小
clock = pygame.time.Clock()
pygame.display.set_caption("計概專題遊戲") #視窗命名
running = True

#載入圖片
player_img = pygame.image.load(os.path.join("img","player.png")).convert()
rock_img = pygame.image.load(os.path.join("img","rock.png")).convert()
bullet_img = pygame.image.load(os.path.join("img","bullet.png")).convert()
boss_img = pygame.image.load(os.path.join("img","boss.png")).convert()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img,(43,65))
        self.image.set_colorkey(REALWHITE)
        self.rect = self.image.get_rect() #定位物件
        self.radius = 21
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
    def update(self):
        key_pressed = pygame.key.get_pressed() #檢視按鍵有沒有被按
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0 

    def shoot(self):    
        bullet = Bullet(self.rect.centerx,self.rect.top)
        all_sprites.add(bullet)    
        bullets.add(bullet)

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = pygame.transform.scale(rock_img,(65,59))
        #self.image = pygame.transform.scale(rock_img,(65,59))
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect() #定位物件
        self.image_ori.set_colorkey(REALWHITE)
        
        self.radius = 25
        self.rect.x = random.randrange(0 , WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100 , -40)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = 3

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori,self.total_degree)

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0 , WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100 , -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img,(18,34))
        self.image.set_colorkey(REALWHITE)
        self.rect = self.image.get_rect() #定位物件
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        
    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(8):
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

#建立遊戲迴圈
while running:
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()    
    #更新遊戲

    all_sprites.update()
    hits = pygame.sprite.groupcollide(rocks,bullets,True,True) #true判斷前面的rocks和bullets碰撞後要不要刪除
    for hit in hits:
        r = Rock()
        all_sprites.add(r)
        rocks.add(r)

    hits = pygame.sprite.spritecollide(player,rocks,False,pygame.sprite.collide_circle)    
    if hits:
        running = False

    #畫面顯示
    screen.fill(WHITE) #改變遊戲顏色(後面是rgb值)
    all_sprites.draw(screen) #畫出所有在all_sprites裡的東西
    pygame.display.update() #更新畫面

pygame.quit()            