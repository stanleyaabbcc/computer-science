import pygame
import random
import os

FPS = 60
WIDTH = 500
HEIGHT = 600

# 顏色定義
GREEN = (0, 255, 0)
REALWHITE = (255, 255, 255)
WHITE = (253, 245, 230)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
GOLD = (255, 193, 37)
GRAY = (192, 192, 192)
DARK_GRAY = (100, 100, 100)

# 遊戲初始化
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("計概專題遊戲")
running = True

# 載入圖片 (請確保 img 資料夾與圖片存在)
# 使用 try-except 避免如果沒有圖片時程式直接崩潰，方便測試
try:
    player_img = pygame.image.load(os.path.join("img", "player.png")).convert()
    bullet_img = pygame.image.load(os.path.join("img", "bullet.png")).convert()
    player_mini_img = pygame.image.load(os.path.join("img", "player_mini_img.png")).convert()
    player_mini_img.set_colorkey(REALWHITE)
    rock_imgs = []
    for i in range(5):
        rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
    
    expl_anim = {'lg': [], 'sm': [], 'player': []}
    for i in range(9):
        expl_img = pygame.image.load(os.path.join("img", f"expl{i}.png")).convert()
        expl_img.set_colorkey(BLACK)
        expl_anim['lg'].append(pygame.transform.scale(expl_img, (75, 75)))
        expl_anim['sm'].append(pygame.transform.scale(expl_img, (30, 30)))
        player_expl_img = pygame.image.load(os.path.join("img", f"player_expl{i}.png")).convert()
        player_expl_img.set_colorkey(BLACK)
        expl_anim['player'].append(player_expl_img)
    
    power_imgs = {}
    power_imgs['shield'] = pygame.image.load(os.path.join("img", "shield.png")).convert()
    power_imgs['gun'] = pygame.image.load(os.path.join("img", "gun.png")).convert()

    # 載入音樂
    shoot_sound = pygame.mixer.Sound(os.path.join("sound", "shoot.wav"))
    die_sound = pygame.mixer.Sound(os.path.join("sound", "rumble.ogg"))
    gun_sound = pygame.mixer.Sound(os.path.join("sound", "pow1.wav"))
    shield_sound = pygame.mixer.Sound(os.path.join("sound", "pow0.wav"))
    expl_sounds = [
        pygame.mixer.Sound(os.path.join("sound", "expl0.wav")),
        pygame.mixer.Sound(os.path.join("sound", "expl1.wav"))
    ]
    pygame.mixer.music.load(os.path.join("sound", "background.mp3"))
    pygame.mixer.music.set_volume(0.5) # 音量稍微調小一點
except Exception as e:
    print(f"Loading assets failed: {e}")
    # 這裡可以做一些錯誤處理，或者讓它崩潰

font_name = pygame.font.match_font('microsoftjhenghei') 
if not font_name:
    font_name = pygame.font.match_font('mingliu') # 如果找不到正黑體，嘗試細明體
if not font_name:
    font_name = pygame.font.match_font('arial') # 最後才退回 arial (不支援中文)

# --- 排行榜功能 ---
LEADERBOARD_FILE = "leaderboard.txt"

def get_high_scores():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    scores = []
    for line in lines:
        try:
            name, score = line.strip().split(",")
            scores.append((name, int(score)))
        except ValueError:
            continue
    # 根據分數排序 (高到低)
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:5] # 只回傳前5名

def save_high_score(name, score):
    scores = get_high_scores()
    scores.append((name, score))
    scores.sort(key=lambda x: x[1], reverse=True)
    scores = scores[:5] # 只保留前5名
    with open(LEADERBOARD_FILE, "w", encoding="utf-8") as f:
        for name, score in scores:
            f.write(f"{name},{score}\n")

# --- 繪圖輔助函式 ---
def draw_text(surf, text, size, x, y, color=BLACK):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def draw_button(surf, text, x, y, w, h, inactive_color, active_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    # 判斷滑鼠是否在按鈕上
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(surf, active_color, (x, y, w, h))
        if click[0] == 1 and action is not None:
            return action # 回傳動作
    else:
        pygame.draw.rect(surf, inactive_color, (x, y, w, h))

    # 按鈕文字
    small_text = pygame.font.Font(font_name, 20)
    text_surf = small_text.render(text, True, BLACK)
    text_rect = text_surf.get_rect()
    text_rect.center = ((x + (w / 2)), (y + (h / 2)))
    surf.blit(text_surf, text_rect)
    return None

def draw_health(surf, hp, x, y):
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (hp / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    if hp > 45:
        pygame.draw.rect(surf, GREEN, fill_rect)
    elif hp > 25:
        pygame.draw.rect(surf, GOLD, fill_rect)
    else:
        pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, BLACK, outline_rect, 2)

def draw_lives(surf, lives, img, x, y):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 32 * i
        img_rect.y = y
        surf.blit(img, img_rect)

# --- 遊戲物件類別 (Sprite Classes) ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (43, 65))
        self.image.set_colorkey(REALWHITE)
        self.rect = self.image.get_rect()
        self.radius = 21
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 8
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self):
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000:
            self.gun -= 1
            self.gun_time = now

        if self.hidden and now - self.hide_time > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10

        key_pressed = pygame.key.get_pressed()
        if key_pressed[pygame.K_RIGHT] or key_pressed[pygame.K_d]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT] or key_pressed[pygame.K_a]:
            self.rect.x -= self.speedx
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self):
        if not(self.hidden):
            if self.gun == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 500)

    def gunup(self):
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs)
        self.image = self.image_ori.copy()
        self.rect = self.image.get_rect()
        self.image_ori.set_colorkey(REALWHITE)
        self.radius = 25
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(2, 10)
        self.speedx = random.randrange(-3, 3)
        self.total_degree = 0
        self.rot_degree = random.randrange(-3, 3)

    def rotate(self):
        self.total_degree += self.rot_degree
        self.total_degree = self.total_degree % 360
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(2, 10)
            self.speedx = random.randrange(-3, 3)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(bullet_img, (18, 34))
        self.image.set_colorkey(REALWHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]):
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(REALWHITE)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom > HEIGHT:
            self.kill()

# --- 遊戲狀態管理 ---
# game_state 可能值: 'menu', 'game', 'instructions', 'leaderboard', 'game_over', 'input_name'
game_state = 'menu' 

all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powers = pygame.sprite.Group()
player = None # 先宣告，在 start_game 中初始化
score = 0
input_name = ""

def start_new_game():
    global all_sprites, rocks, bullets, powers, player, score
    all_sprites = pygame.sprite.Group()
    rocks = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    powers = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    for i in range(8):
        r = Rock()
        all_sprites.add(r)
        rocks.add(r)
    score = 0
    pygame.mixer.music.play(-1)

# 主迴圈
try:
    while running:
        clock.tick(FPS)
        
        # 取得輸入
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            
            # 只有在遊戲進行中才偵測發射
            if game_state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.shoot()

            # 名字輸入偵測
            if game_state == 'input_name':
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # 儲存分數並回到選單
                        final_name = input_name if input_name else "Player"
                        save_high_score(final_name, score)
                        input_name = ""
                        game_state = 'leaderboard'
                    elif event.key == pygame.K_BACKSPACE:
                        input_name = input_name[:-1]
                    else:
                        # 限制名字長度
                        if len(input_name) < 10:
                            input_name += event.unicode

        # --- 畫面繪製邏輯 (根據狀態) ---
        screen.fill(WHITE) # 統一背景

        if game_state == 'menu':
            draw_text(screen, '計算機概論 射擊遊戲', 40, WIDTH / 2, HEIGHT / 4)
            
            # 繪製三個按鈕
            btn_w, btn_h = 150, 50
            start_btn = draw_button(screen, "Start Game", WIDTH/2 - btn_w/2, 250, btn_w, btn_h, GRAY, DARK_GRAY, 'game')
            inst_btn = draw_button(screen, "Controls", WIDTH/2 - btn_w/2, 320, btn_w, btn_h, GRAY, DARK_GRAY, 'instructions')
            rank_btn = draw_button(screen, "Leaderboard", WIDTH/2 - btn_w/2, 390, btn_w, btn_h, GRAY, DARK_GRAY, 'leaderboard')
            
            if start_btn == 'game':
                start_new_game()
                game_state = 'game'
            elif inst_btn == 'instructions':
                game_state = 'instructions'
            elif rank_btn == 'leaderboard':
                game_state = 'leaderboard'

        elif game_state == 'instructions':
            draw_text(screen, '操作說明', 40, WIDTH / 2, HEIGHT / 5)
            draw_text(screen, 'A / D 或 左/右 鍵移動', 22, WIDTH / 2, HEIGHT / 2 - 40)
            draw_text(screen, '空白鍵發射子彈', 22, WIDTH / 2, HEIGHT / 2 + 10)
            
            back_btn = draw_button(screen, "Back", WIDTH/2 - 75, 450, 150, 50, GRAY, DARK_GRAY, 'menu')
            if back_btn == 'menu':
                game_state = 'menu'

        elif game_state == 'leaderboard':
            draw_text(screen, '排行榜 (Top 5)', 40, WIDTH / 2, 50)
            scores = get_high_scores()
            for idx, (name, s) in enumerate(scores):
                draw_text(screen, f"{idx+1}. {name} : {s}", 25, WIDTH / 2, 120 + idx * 40)
            
            if not scores:
                draw_text(screen, "尚無紀錄", 20, WIDTH/2, 150)

            back_btn = draw_button(screen, "Back", WIDTH/2 - 75, 500, 150, 50, GRAY, DARK_GRAY, 'menu')
            if back_btn == 'menu':
                game_state = 'menu'

        elif game_state == 'input_name':
            draw_text(screen, 'Game Over!', 48, WIDTH / 2, HEIGHT / 4)
            draw_text(screen, f'Score: {score}', 30, WIDTH / 2, HEIGHT / 4 + 60)
            draw_text(screen, 'Enter Your Name:', 22, WIDTH / 2, HEIGHT / 2)
            
            # 繪製輸入框
            input_rect = pygame.Rect(WIDTH / 2 - 100, HEIGHT / 2 + 30, 200, 40)
            pygame.draw.rect(screen, BLACK, input_rect, 2)
            draw_text(screen, input_name, 28, WIDTH / 2, HEIGHT / 2 + 35)
            
            draw_text(screen, 'Press Enter to Confirm', 18, WIDTH / 2, HEIGHT * 3/4)

        elif game_state == 'game':
            # 遊戲邏輯更新
            all_sprites.update()
            
            # 子彈打石頭
            hits = pygame.sprite.groupcollide(rocks, bullets, True, True)
            for hit in hits:
                random.choice(expl_sounds).play()
                score += hit.radius
                expl = Explosion(hit.rect.center, 'lg')
                all_sprites.add(expl)
                r = Rock()
                all_sprites.add(r)
                rocks.add(r)
                if random.random() > 0.95:
                    pow = Power(hit.rect.center)
                    all_sprites.add(pow)
                    powers.add(pow)

            # 飛船撞石頭
            hits = pygame.sprite.spritecollide(player, rocks, True, pygame.sprite.collide_circle)
            for hit in hits:
                r = Rock()
                all_sprites.add(r)
                rocks.add(r)
                player.health -= hit.radius
                expl = Explosion(hit.rect.center, 'sm')
                all_sprites.add(expl)
                if player.health <= 0:
                    death_expl = Explosion(player.rect.center, 'player')
                    all_sprites.add(death_expl)
                    die_sound.play()
                    player.lives -= 1
                    player.health = 100
                    player.hide()

            # 飛船吃寶物
            hits = pygame.sprite.spritecollide(player, powers, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.health += 20
                    if player.health > 100:
                        player.health = 100
                    shield_sound.play()
                elif hit.type == 'gun':
                    player.gunup()
                    gun_sound.play()

            if player.lives == 0 and not(death_expl.alive()):
                game_state = 'input_name' # 遊戲結束，跳轉到輸入名字

            # 繪製遊戲畫面
            all_sprites.draw(screen)
            draw_text(screen, str(score), 18, WIDTH / 2, 10)
            draw_health(screen, player.health, 5, 15)
            draw_lives(screen, player.lives, player_mini_img, WIDTH - 100, 15)

        pygame.display.update()

except Exception as e:
    print(f"Error in main loop: {e}")

pygame.quit()