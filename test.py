import pygame
import sys
import random
import math
import os 

# Config
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 144
GRAVITY = 0.8
DT = 60 / FPS 

# Color
WHITE = (255, 255, 255)
BLACK = (20, 20, 30)
RED = (200, 50, 50)
GREEN = (100, 100, 100)
BLUE = (50, 100, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
DARK_GREEN = (50, 100, 50)
GREY = (150, 150, 150)
ORANGE = (255, 140, 0)
PINK = (255, 105, 180)
PURPLE = (128, 0, 128)
SEMI_TRANSPARENT_BLACK = (0, 0, 0, 180)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 10
        self.max_radius = 150 
        self.growth_rate = 15
        self.pos_x = x
        self.pos_y = y
        
        self.image = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.timer = 20

    def update(self):
        self.timer -= 1 * DT
        
        if self.radius < self.max_radius:
            self.radius += self.growth_rate * DT
        
        if self.timer < 10:
            self.alpha -= 25 * DT
            if self.alpha < 0: self.alpha = 0
            
        self.image.fill((0,0,0,0)) 
        
        pygame.draw.circle(self.image, (*ORANGE, int(self.alpha)), 
                           (self.max_radius, self.max_radius), int(self.radius))
        
        pygame.draw.circle(self.image, (*YELLOW, int(self.alpha)), 
                           (self.max_radius, self.max_radius), int(self.radius * 0.7))
        
        if self.timer <= 0:
            self.kill()

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage=10, is_enemy=False, is_hmg=False, bullet_img=None):
        super().__init__()
        if bullet_img:
            self.image = bullet_img
        else:
            size = (14, 8) if is_hmg else (12, 12)
            color = GOLD if is_hmg else (RED if is_enemy else YELLOW)
            self.image = pygame.Surface(size)
            self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.speed = 10 if is_enemy else (20 if is_hmg else 15)
        self.vel_x = dx * self.speed
        self.vel_y = dy * self.speed
        
        self.damage = damage
        self.is_enemy = is_enemy

    def update(self):
        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        if self.rect.right < -100 or self.rect.left > 100000:
            self.kill()
        if self.rect.y > SCREEN_HEIGHT + 100 or self.rect.y < -100:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.original_image = pygame.Surface((24, 12), pygame.SRCALPHA)
        pygame.draw.polygon(self.original_image, CYAN, [(0,0), (24,6), (0,12)])
        pygame.draw.circle(self.original_image, RED, (2, 6), 3) 
        
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.target = target
        self.speed = 3.5    
        self.damage = 40    
        self.hp = 1
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.timer = 0
        self.tracking_limit = 90
        self.fuel_limit = 200 
        
        self.vel_x = 0
        self.vel_y = 0

    def update(self):
        self.timer += 1 * DT
        
        if self.timer < self.tracking_limit:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            
            self.vel_x = math.cos(angle_rad) * self.speed
            self.vel_y = math.sin(angle_rad) * self.speed
            
            self.image = pygame.transform.rotate(self.original_image, -angle_deg)
            self.rect = self.image.get_rect(center=self.rect.center)

        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        if self.timer >= self.fuel_limit:
            self.kill() 

        if self.rect.x < -200 or self.rect.x > 100000:
            self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_enemy=False):
        super().__init__()
        self.image = pygame.Surface((16, 16))
        color = RED if is_enemy else ORANGE
        self.image.fill(color)
        pygame.draw.rect(self.image, WHITE, (4,4,8,8)) 
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.vel_x = direction * (0 if is_enemy else 12) 
        self.vel_y = 5 if is_enemy else -14 
        self.timer = 60 
        self.explode_now = False
        self.is_enemy = is_enemy

    def update(self):
        self.vel_y += GRAVITY * DT
        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        self.timer -= 1 * DT
        
        if self.timer <= 0:
            self.explode_now = True

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, color, type_name):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_y = -5
        self.type_name = type_name

    def update(self, platforms):
        self.vel_y += GRAVITY * DT
        self.pos_y += self.vel_y * DT
        self.rect.centery = int(self.pos_y)
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.pos_y = float(self.rect.centery)

class HealthPack(Item):
    def __init__(self, x, y):
        super().__init__(x, y, PINK, 'heal')
        pygame.draw.rect(self.image, WHITE, (8, 4, 9, 17))
        pygame.draw.rect(self.image, WHITE, (4, 8, 17, 9))
        pygame.draw.rect(self.image, RED, (10, 6, 5, 13))
        pygame.draw.rect(self.image, RED, (6, 10, 13, 5))

class MachineGunPickup(Item):
    def __init__(self, x, y):
        super().__init__(x, y, GOLD, 'mg')
        font = pygame.font.SysFont("Arial", 20, bold=True)
        txt = font.render("M", True, BLACK)
        self.image.blit(txt, (5, 2))

class MeleeEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.arc(self.image, (255, 255, 255), (0,0,60,60), 0, 3.14, 5)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 15 

    def update(self):
        self.timer -= 1 * DT
        if self.timer <= 0:
            self.kill()

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (100, 100)
        
        self.pos_x = 100.0
        self.pos_y = 100.0
        
        self.vel_y = 0
        self.speed = 5
        self.jump_power = -15
        self.facing = 1
        self.on_ground = False
        
        self.max_hp = 100
        self.hp = 100
        self.max_shield = 100
        self.shield = 100
        self.is_shielding = False
        
        self.weapon_type = "pistol"
        self.ammo = 0
        self.shoot_delay = 0
        
        self.max_grenade_cd = 120
        self.grenade_cd = 0
        self.shield_regen_timer = 0
        
        self.melee_cd = 0     
        self.melee_range = 70 
        self.melee_dmg = 50   

    def get_input(self, all_sprites, bullets, grenades, is_locked, camera_x):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_c] and self.shield > 0:
            self.is_shielding = True
        else:
            self.is_shielding = False
            
        right_boundary = camera_x + SCREEN_WIDTH - 40 
        
        if keys[pygame.K_LEFT]:
            self.pos_x -= self.speed * DT
            self.facing = -1
            if self.pos_x < camera_x: self.pos_x = camera_x

        if keys[pygame.K_RIGHT]:
            self.pos_x += self.speed * DT
            self.facing = 1
            if is_locked and self.pos_x + self.rect.width > right_boundary: 
                self.pos_x = right_boundary - self.rect.width

        self.rect.x = int(self.pos_x)

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        if keys[pygame.K_g] and self.grenade_cd <= 0 and not self.is_shielding:
            g = Grenade(self.rect.centerx, self.rect.centery, self.facing)
            all_sprites.add(g)
            grenades.add(g)
            self.grenade_cd = self.max_grenade_cd 

        if keys[pygame.K_f] and self.weapon_type == "hmg" and not self.is_shielding:
            if self.shoot_delay <= 0:
                self.fire_bullet(bullets, all_sprites)
                self.shoot_delay = 5

    def fire_bullet(self, bullets, all_sprites):
        keys = pygame.key.get_pressed()
        dx, dy = self.facing, 0
        if keys[pygame.K_UP]: 
            dy = -1
            dx = 0 if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) else dx
        elif keys[pygame.K_DOWN] and not self.on_ground: 
            dy = 1
            dx = 0
        
        is_hmg = (self.weapon_type == "hmg")
        dmg = 25 if is_hmg else 20
        
        b = Bullet(self.rect.centerx, self.rect.centery, dx, dy, damage=dmg, is_hmg=is_hmg)
        all_sprites.add(b)
        bullets.add(b)

        if is_hmg:
            self.ammo -= 1
            if self.ammo <= 0:
                self.weapon_type = "pistol"
                print("WEAPON: PISTOL")

    def check_auto_melee(self, enemies, all_sprites, effects_group, spawn_loot_callback, add_score_callback):
        if self.melee_cd > 0 or self.is_shielding:
            return

        for e in enemies:
            dist_x = abs(self.rect.centerx - e.rect.centerx)
            dist_y = abs(self.rect.centery - e.rect.centery)

            if dist_x < self.melee_range and dist_y < self.melee_range:
                e.hp -= self.melee_dmg
                slash = MeleeEffect(e.rect.centerx, e.rect.centery)
                all_sprites.add(slash)
                effects_group.add(slash)
                
                self.melee_cd = 40 
                if e.hp <= 0:
                    spawn_loot_callback(e) 
                    add_score_callback(e)
                    e.kill()
                break 

    def take_damage(self, amount):
        self.shield_regen_timer = 180 
        if self.is_shielding:
            self.shield -= amount
            if self.shield < 0:
                self.hp -= abs(self.shield)
                self.shield = 0
                self.is_shielding = False
        else:
            self.hp -= amount

    def update(self, platforms):
        self.vel_y += GRAVITY * DT
        self.pos_y += self.vel_y * DT
        self.rect.y = int(self.pos_y)
        
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, platforms, False)

        for p in hits:
            if self.vel_y > 0 and self.rect.bottom < p.rect.bottom:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.pos_y = float(self.rect.y)
                self.on_ground = True

            elif self.vel_y < 0 and self.rect.top > p.rect.top:
                 self.rect.top = p.rect.bottom
                 self.vel_y = 0
                 self.pos_y = float(self.rect.y)

        self.rect.x = int(self.pos_x)

        if self.rect.y > SCREEN_HEIGHT + 200: self.hp = 0 
        
        if self.grenade_cd > 0: self.grenade_cd -= 1 * DT
        if self.shoot_delay > 0: self.shoot_delay -= 1 * DT
        if self.melee_cd > 0: self.melee_cd -= 1 * DT
        
        if self.is_shielding:
            self.shield -= 0.3 * DT
            self.shield_regen_timer = 120
            if self.shield <= 0:
                self.shield = 0
                self.is_shielding = False
        else:
            if self.shield_regen_timer > 0:
                self.shield_regen_timer -= 1 * DT
            elif self.shield < self.max_shield:
                self.shield += 0.5 * DT

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color, hp, type_name, score_val):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(self.rect.y)
        
        self.hp = hp
        self.max_hp = hp
        self.type_name = type_name
        self.score_val = score_val 
        self.shoot_timer = random.randint(0, 100)

    def check_bounds(self):
        if self.rect.y > SCREEN_HEIGHT + 50:
            self.kill()

class Soldier(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 30, 'soldier', 100)
        self.vel_y = 0
        self.facing = -1
        self.speed = 2

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.vel_y += GRAVITY * DT
        self.pos_y += self.vel_y * DT
        self.rect.y = int(self.pos_y)
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.pos_y = float(self.rect.y)
        self.check_bounds()

        dist_x = player.rect.x - self.rect.x
        
        if 5 < abs(dist_x) < 1000:
            if dist_x > 0: 
                self.pos_x += self.speed * DT
                self.facing = 1
            else: 
                self.pos_x -= self.speed * DT
                self.facing = -1
        
        self.rect.x = int(self.pos_x)
        self.shoot_timer += 1 * DT

        if self.shoot_timer > 90 and abs(dist_x) < 800:
            if (self.facing == 1 and dist_x > 0) or (self.facing == -1 and dist_x < 0):
                b = Bullet(self.rect.centerx, self.rect.centery, self.facing, 0, damage=10, is_enemy=True)
                bullets.add(b)
                all_sprites.add(b)
                self.shoot_timer = 0

class Tank(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, DARK_GREEN, 120, 'tank', 500) 
        self.image = pygame.Surface((90, 60))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        self.pos_x = float(x)
        self.pos_y = float(self.rect.y)
        
        self.vel_y = 0
        self.speed = 1

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.vel_y += GRAVITY * DT
        self.pos_y += self.vel_y * DT
        self.rect.y = int(self.pos_y)
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.pos_y = float(self.rect.y)

        self.check_bounds()
        dist_x = player.rect.x - self.rect.x

        if 200 < abs(dist_x) < 1200:
            if dist_x > 0: self.pos_x += self.speed * DT
            else: self.pos_x -= self.speed * DT
        
        self.rect.x = int(self.pos_x)

        self.shoot_timer += 1 * DT

        if self.shoot_timer > 180 and abs(dist_x) < 1200: 
            m = Missile(self.rect.centerx, self.rect.centery - 20, player)
            all_sprites.add(m)
            missiles_group.add(m) 
            self.shoot_timer = 0

class Helicopter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, GREY, 60, 'heli', 300)
        self.start_y = y
        self.phase = 0
        self.pos_x = float(x)

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.phase += 0.05 * DT
        self.rect.y = self.start_y + math.sin(self.phase) * 30
        
        if self.rect.x < player.rect.x - 200: self.pos_x += 2 * DT
        elif self.rect.x > player.rect.x + 200: self.pos_x -= 2 * DT
        
        self.rect.x = int(self.pos_x)
        
        self.shoot_timer += 1 * DT
        if self.shoot_timer > 70 and abs(player.rect.x - self.rect.x) < 1000:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            vel_x = math.cos(angle)
            vel_y = math.sin(angle)
            
            b = Bullet(self.rect.centerx, self.rect.bottom, vel_x, vel_y, damage=20, is_enemy=True, bullet_img=bullet_img)
            bullets.add(b)
            all_sprites.add(b)
            self.shoot_timer = 0

class BossHelicopter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, PURPLE, 5000, 'boss_heli', 10000)
        self.image = pygame.Surface((200, 100))
        self.image.fill(PURPLE)
        pygame.draw.rect(self.image, DARK_GREEN, (10, 10, 180, 80))
        pygame.draw.rect(self.image, RED, (50, 40, 20, 20)) 
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.start_y = y
        self.phase = 0
        self.state = "move" # move, attack1, attack2, attack3
        self.state_timer = 0
        self.attack_cooldown = 0
        
    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.phase += 0.03 * DT
        hover_offset = math.sin(self.phase) * 50
        self.state_timer += 1 * DT
        
        dist_x = player.rect.centerx - self.rect.centerx
        
        target_x = player.rect.centerx 
        if self.pos_x < target_x - 100:
            self.pos_x += 3 * DT
        elif self.pos_x > target_x + 100:
            self.pos_x -= 3 * DT
            
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.start_y + hover_offset)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1 * DT
        else:
            attack_roll = random.choice(['mg', 'missile', 'bomb'])
            
            if attack_roll == 'mg':
                for i in range(5): 
                    spread = random.uniform(-0.2, 0.2)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx) + spread
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, damage=15, is_enemy=True)
                    bullets.add(b)
                    all_sprites.add(b)
                self.attack_cooldown = 60 
                
            elif attack_roll == 'missile':
                for i in range(3):
                    offset_x = (i - 1) * 40
                    m = Missile(self.rect.centerx + offset_x, self.rect.centery, player)
                    all_sprites.add(m)
                    missiles_group.add(m)
                self.attack_cooldown = 180 
                
            elif attack_roll == 'bomb':
                g = Grenade(self.rect.centerx, self.rect.bottom, 0, is_enemy=True)
                all_sprites.add(g)
                grenades_group.add(g)
                self.attack_cooldown = 40 

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        pygame.draw.rect(self.image, (80, 80, 80), (0,0,w,h), 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Metal Slug: Boss Fight Update")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)

        bullet_filename = 'assets/beras.png' 
        if os.path.exists(bullet_filename):
            try:
                raw_image = pygame.image.load(bullet_filename).convert_alpha()
                self.heli_bullet_img = pygame.transform.scale(raw_image, (50, 50))
            except Exception as e:
                self.heli_bullet_img = None
        else:
            self.heli_bullet_img = None

        self.highscore = self.load_high_score()
        self.new_game()

    def load_high_score(self):
        filename = "highscore.txt"
        if os.path.exists(filename):
            try:
                with open(filename, "r") as f:
                    return int(f.read())
            except:
                return 0
        return 0

    def save_high_score(self):
        filename = "highscore.txt"
        with open(filename, "w") as f:
            f.write(str(self.highscore))

    def new_game(self):
        self.boss_fight_active = False
        self.next_boss_score = 10000
        
        self.score = 0
        self.game_state = "playing"
        self.battle_lock = False
        self.hmg_pickup_msg_timer = 0

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.missiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.boss_group = pygame.sprite.Group() 
        self.grenades = pygame.sprite.Group()
        self.enemy_grenades = pygame.sprite.Group() 
        self.items = pygame.sprite.Group()
        self.effects = pygame.sprite.Group() 
        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.camera_x = 0
        self.world_limit = 0

        self.generate_chunk(0, 1000)

    def generate_chunk(self, start_x, width):
        if self.boss_fight_active:
            ground_y = SCREEN_HEIGHT - 60
            ground = Platform(start_x, ground_y, width, 100)
            self.platforms.add(ground)
            self.all_sprites.add(ground)
            self.world_limit = start_x + width
            return

        ground_y = SCREEN_HEIGHT - 60
        ground = Platform(start_x, ground_y, width, 100)
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        num_obstacles = width // 300
        for i in range(num_obstacles):
            obs_w = random.randint(80, 180)
            obs_h = random.choice([40, 80, 110])
            obs_x = start_x + random.randint(100, width - 400) 
            obs_y = ground_y - obs_h
            
            p = Platform(obs_x, obs_y, obs_w, obs_h)
            self.platforms.add(p)
            self.all_sprites.add(p)

            roll = random.random()
            if roll < 0.4:
                e = Soldier(obs_x + obs_w//2, obs_y - 10)
                self.enemies.add(e)
                self.all_sprites.add(e)
            elif roll < 0.6:
                h = Helicopter(obs_x, 150)
                self.enemies.add(h)
                self.all_sprites.add(h)
            elif roll < 0.8:
                t = Tank(obs_x + 200, ground_y - 10)
                self.enemies.add(t)
                self.all_sprites.add(t)

        self.world_limit = start_x + width

    def spawn_loot(self, enemy):
        if enemy.type_name == 'boss_heli':
            for _ in range(3):
                offset = random.randint(-30, 30)
                if random.random() < 0.5:
                    item = MachineGunPickup(enemy.rect.centerx + offset, enemy.rect.centery)
                else:
                    item = HealthPack(enemy.rect.centerx + offset, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)
        
        elif enemy.type_name == 'soldier':
            if random.random() < 0.25:
                item = HealthPack(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)
        elif enemy.type_name in ['tank', 'heli']:
            if random.random() < 0.25:
                item = MachineGunPickup(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)

    def add_score(self, enemy):
        self.score += enemy.score_val

    def trigger_explosion(self, grenade):
        expl = Explosion(grenade.rect.centerx, grenade.rect.centery)
        self.all_sprites.add(expl)
        self.effects.add(expl)
        EXPLOSION_RADIUS = 300
        EXPLOSION_DAMAGE = 120 

        for e in self.enemies:
            dist = math.hypot(e.rect.centerx - grenade.rect.centerx, e.rect.centery - grenade.rect.centery)
            if dist < EXPLOSION_RADIUS:
                e.hp -= EXPLOSION_DAMAGE
                if e.hp <= 0:
                    self.spawn_loot(e)
                    self.add_score(e)
                    e.kill()
        
        for b in self.boss_group:
            dist = math.hypot(b.rect.centerx - grenade.rect.centerx, b.rect.centery - grenade.rect.centery)
            if dist < EXPLOSION_RADIUS:
                b.hp -= EXPLOSION_DAMAGE
                if b.hp <= 0:
                    self.spawn_loot(b)
                    self.add_score(b)
                    b.kill()
                    self.boss_fight_active = False 
                    self.next_boss_score += 10000

        grenade.kill()

    def update(self):
        if self.game_state == "game_over":
            return
        
        if self.score >= self.next_boss_score and not self.boss_fight_active:
            self.boss_fight_active = True
            boss_spawn_x = self.camera_x + SCREEN_WIDTH - 200
            boss = BossHelicopter(boss_spawn_x, 200)
            self.boss_group.add(boss)
            self.all_sprites.add(boss)
            
            for e in self.enemies:
                e.kill()

        self.battle_lock = self.boss_fight_active

        target_cam = self.player.rect.centerx - SCREEN_WIDTH // 3
        if not self.battle_lock:
            self.camera_x += (target_cam - self.camera_x) * 0.1

        if self.player.rect.right > self.world_limit - SCREEN_WIDTH:
            self.generate_chunk(self.world_limit, 1200)

        self.player.get_input(self.all_sprites, self.bullets, self.grenades, self.battle_lock, self.camera_x)
        self.player.update(self.platforms)
        self.player.check_auto_melee(self.enemies, self.all_sprites, self.effects, self.spawn_loot, self.add_score)
        self.player.check_auto_melee(self.boss_group, self.all_sprites, self.effects, self.spawn_loot, self.add_score) 
        
        self.bullets.update()
        self.grenades.update()
        self.enemy_grenades.update() 
        self.enemy_bullets.update()
        self.missiles.update() 
        self.items.update(self.platforms)
        self.effects.update()
        
        for g in self.grenades:
            if g.explode_now:
                self.trigger_explosion(g)

        g_hits = pygame.sprite.groupcollide(self.enemies, self.grenades, False, False)
        for e, g_list in g_hits.items():
            for g in g_list: self.trigger_explosion(g) 
            
        g_boss_hits = pygame.sprite.groupcollide(self.boss_group, self.grenades, False, False)
        for b, g_list in g_boss_hits.items():
            for g in g_list: self.trigger_explosion(g)

        for g in self.enemy_grenades:
            if g.explode_now:
                expl = Explosion(g.rect.centerx, g.rect.centery)
                self.all_sprites.add(expl)
                self.effects.add(expl)
                
                dist_p = math.hypot(self.player.rect.centerx - g.rect.centerx, self.player.rect.centery - g.rect.centery)
                if dist_p < 150:
                    self.player.take_damage(30)
                g.kill()
        
        bg_hits = pygame.sprite.spritecollide(self.player, self.enemy_grenades, False)
        for g in bg_hits:
            g.explode_now = True

        for e in self.enemies:
            if -SCREEN_WIDTH < e.rect.x - self.player.rect.x < SCREEN_WIDTH * 1.5:
                e.update(self.platforms, self.player, self.enemy_bullets, self.all_sprites, 
                         missiles_group=self.missiles, grenades_group=self.enemy_grenades, bullet_img=self.heli_bullet_img)

        for b in self.boss_group:
            b.update(self.platforms, self.player, self.enemy_bullets, self.all_sprites, 
                     missiles_group=self.missiles, grenades_group=self.enemy_grenades)

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for e, b_list in hits.items():
            dmg = sum([b.damage for b in b_list])
            e.hp -= dmg
            if e.hp <= 0: 
                self.spawn_loot(e)
                self.add_score(e)
                e.kill()

        boss_hits = pygame.sprite.groupcollide(self.boss_group, self.bullets, False, True)
        for b, b_list in boss_hits.items():
            dmg = sum([b.damage for b in b_list])
            b.hp -= dmg
            if b.hp <= 0:
                self.spawn_loot(b)
                self.add_score(b)
                b.kill()
                self.boss_fight_active = False
                self.next_boss_score += 10000
        
        missile_hits = pygame.sprite.groupcollide(self.missiles, self.bullets, True, True)

        player_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in player_hit_list:
            self.player.take_damage(bullet.damage)
            
        missile_hit_player = pygame.sprite.spritecollide(self.player, self.missiles, True)
        for m in missile_hit_player:
            self.player.take_damage(m.damage)

        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            if item.type_name == 'heal':
                self.player.hp = min(self.player.max_hp, self.player.hp + 30)
            elif item.type_name == 'mg':
                self.player.weapon_type = "hmg"
                self.player.ammo = 100
                self.hmg_pickup_msg_timer = 60

        if self.player.hp <= 0:
            self.game_state = "game_over"
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_high_score()
        
        if self.hmg_pickup_msg_timer > 0:
            self.hmg_pickup_msg_timer -= 1 * DT

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "playing":
                    if event.key == pygame.K_f and self.player.weapon_type == "pistol" and not self.player.is_shielding:
                        self.player.fire_bullet(self.bullets, self.all_sprites)
                    if event.key == pygame.K_F1: 
                        for e in self.enemies: e.kill()
                        for b in self.boss_group: b.kill(); self.boss_fight_active = False
                
                elif self.game_state == "game_over":
                    if event.key == pygame.K_r:
                        self.new_game()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

    def draw_game_over_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_BLACK)
        self.screen.blit(overlay, (0,0))
        
        title_surf = self.title_font.render("GAME OVER", True, RED)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
        self.screen.blit(title_surf, title_rect)
        
        score_surf = self.big_font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
        self.screen.blit(score_surf, score_rect)
        
        hs_color = GOLD if self.score >= self.highscore and self.score > 0 else GREY
        hs_surf = self.font.render(f"Best Score: {self.highscore}", True, hs_color)
        hs_rect = hs_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
        self.screen.blit(hs_surf, hs_rect)
        
        restart_surf = self.font.render("Press [R] to Restart  |  Press [ESC] to Exit", True, WHITE)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 80))
        self.screen.blit(restart_surf, restart_rect)

    def draw(self):
        self.screen.fill(BLACK)
        
        for s in self.all_sprites:
            off_x = s.rect.x - int(self.camera_x)
            if (off_x + s.rect.width > -50) and (off_x < SCREEN_WIDTH + 50):
                self.screen.blit(s.image, (off_x, s.rect.y))
                if isinstance(s, Player) and s.is_shielding:
                    pygame.draw.circle(self.screen, CYAN, (off_x + 15, s.rect.y + 25), 40, 2)
        
        if self.game_state == "playing":
            hp_pct = max(0, self.player.hp / self.player.max_hp)
            hp_col = (0, 255, 0) if hp_pct > 0.5 else (255, 0, 0)

            pygame.draw.rect(self.screen, (50,0,0), (10, 10, 200, 20))
            pygame.draw.rect(self.screen, hp_col, (10, 10, 200 * hp_pct, 20))
            pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 20), 2)

            shield_pct = max(0, self.player.shield / self.player.max_shield)
            shield_col = CYAN if self.player.shield > 0 else (50, 50, 50)

            pygame.draw.rect(self.screen, (0,50,50), (10, 35, 150, 10))
            pygame.draw.rect(self.screen, shield_col, (10, 35, 150 * shield_pct, 10))
            pygame.draw.rect(self.screen, WHITE, (10, 35, 150, 10), 1)

            grenade_pct = 1.0 - (max(0, self.player.grenade_cd) / self.player.max_grenade_cd)
            grenade_col = ORANGE if grenade_pct >= 1.0 else (100, 50, 0)
            
            pygame.draw.rect(self.screen, (50, 25, 0), (10, 50, 100, 8))
            pygame.draw.rect(self.screen, grenade_col, (10, 50, 100 * grenade_pct, 8))
            pygame.draw.rect(self.screen, WHITE, (10, 50, 100, 8), 1)

            g_label = self.font.render("G", True, WHITE)
            self.screen.blit(g_label, (115, 45))

            score_txt = self.font.render(f"SCORE: {self.score}", True, WHITE)
            self.screen.blit(score_txt, (SCREEN_WIDTH - 150, 10))
            
            w_txt = "PISTOL"
            w_col = WHITE
            if self.player.weapon_type == "hmg":
                w_txt = f"MACHINE GUN ({self.player.ammo})"
                w_col = GOLD
            
            txt_weapon = self.font.render(w_txt, True, w_col)
            self.screen.blit(txt_weapon, (10, 70))
            
            txt_info = self.font.render("F: Shoot (Hold for MG) | C: Shield | G: Grenade", True, GREY)
            self.screen.blit(txt_info, (220, 10))

            if self.boss_fight_active and len(self.boss_group) > 0:
                boss = self.boss_group.sprites()[0]
                boss_hp_pct = max(0, boss.hp / boss.max_hp)
                
                bar_w = 600
                bar_h = 30
                bar_x = (SCREEN_WIDTH - bar_w) // 2
                bar_y = 50
                
                pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_w, bar_h))
                pygame.draw.rect(self.screen, PURPLE, (bar_x, bar_y, bar_w * boss_hp_pct, bar_h))
                pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
                
                boss_label = self.big_font.render("GIANT HELICOPTER", True, RED)
                self.screen.blit(boss_label, (bar_x, bar_y - 40))

                warn = self.font.render("WARNING: BOSS APPROACHING!", True, RED)
                self.screen.blit(warn, (SCREEN_WIDTH//2 - 120, 90))

            if self.hmg_pickup_msg_timer > 0:
                msg = self.big_font.render("HEAVY MACHINE GUN!", True, GOLD)
                self.screen.blit(msg, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))

        if self.game_state == "game_over":
            self.draw_game_over_screen()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    Game().run()