import pygame
import sys
import random
import math
import os 

# --- Konfigurasi ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8

# Warna
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

# --- Projectiles ---

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage=10, is_enemy=False, is_hmg=False, bullet_img=None):
        super().__init__()
        if bullet_img:
            self.image = bullet_img
        else:
            size = (14, 8) if is_hmg else (10, 8)
            color = GOLD if is_hmg else (RED if is_enemy else YELLOW)
            self.image = pygame.Surface(size)
            self.image.fill(color)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        speed = 10 if is_enemy else (20 if is_hmg else 15)
        self.vel_x = dx * speed
        self.vel_y = dy * speed
        self.damage = damage
        self.is_enemy = is_enemy

    def update(self):
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        if self.rect.right < -100 or self.rect.left > 100000:
            self.kill()
        if self.rect.y > SCREEN_HEIGHT + 100 or self.rect.y < -100:
            self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((12, 12))
        self.image.fill(ORANGE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_x = direction * 9
        self.vel_y = -11
        self.timer = 50

    def update(self):
        self.vel_y += GRAVITY
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y
        self.timer -= 1
        if self.timer <= 0:
            self.kill()

# --- Items & Effects ---

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, color, type_name):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.vel_y = -5
        self.type_name = type_name

    def update(self, platforms):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0

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
        # Visual sabetan (lingkaran putih tipis)
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.arc(self.image, (255, 255, 255), (0,0,60,60), 0, 3.14, 5)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 15 # Muncul selama 15 frame (0.25 detik)

    def update(self):
        # Timer berkurang setiap frame
        self.timer -= 1
        if self.timer <= 0:
            self.kill() # Menghapus diri sendiri dari semua grup

# --- Actors ---

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.topleft = (100, 100)
        
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
        
        self.grenade_cd = 0
        self.shield_regen_timer = 0
        
        # Stats Melee
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
            self.rect.x -= self.speed
            self.facing = -1
            if self.rect.x < camera_x: self.rect.x = camera_x
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing = 1
            if is_locked and self.rect.right > right_boundary: self.rect.right = right_boundary

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        if keys[pygame.K_g] and self.grenade_cd == 0 and not self.is_shielding:
            g = Grenade(self.rect.centerx, self.rect.centery, self.facing)
            all_sprites.add(g)
            grenades.add(g)
            self.grenade_cd = 60

        if keys[pygame.K_f] and self.weapon_type == "hmg" and not self.is_shielding:
            if self.shoot_delay == 0:
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

    # --- PERBAIKAN: Menambah parameter 'effects_group' ---
    def check_auto_melee(self, enemies, all_sprites, effects_group, spawn_loot_callback):
        if self.melee_cd > 0 or self.is_shielding:
            return

        for e in enemies:
            dist_x = abs(self.rect.centerx - e.rect.centerx)
            dist_y = abs(self.rect.centery - e.rect.centery)

            if dist_x < self.melee_range and dist_y < self.melee_range:
                # Kena Hit!
                e.hp -= self.melee_dmg
                
                # Visual
                slash = MeleeEffect(e.rect.centerx, e.rect.centery)
                all_sprites.add(slash)   # Masukkan ke grup gambar
                effects_group.add(slash) # Masukkan ke grup update (PENTING AGAR HILANG)
                
                self.melee_cd = 40 
                
                if e.hp <= 0:
                    spawn_loot_callback(e) 
                    e.kill()
                
                break # Hanya hit 1 musuh per frame

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
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        self.on_ground = False
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0 and self.rect.bottom < p.rect.bottom:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0 and self.rect.top > p.rect.top:
                 self.rect.top = p.rect.bottom
                 self.vel_y = 0

        if self.rect.y > SCREEN_HEIGHT + 200: self.hp = 0
        
        if self.grenade_cd > 0: self.grenade_cd -= 1
        if self.shoot_delay > 0: self.shoot_delay -= 1
        
        if self.melee_cd > 0: self.melee_cd -= 1
        
        if self.is_shielding:
            self.shield -= 0.3 
            self.shield_regen_timer = 120
            if self.shield <= 0:
                self.shield = 0
                self.is_shielding = False
        else:
            if self.shield_regen_timer > 0:
                self.shield_regen_timer -= 1
            elif self.shield < self.max_shield:
                self.shield += 0.5

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color, hp, type_name):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        self.hp = hp
        self.max_hp = hp
        self.type_name = type_name
        self.shoot_timer = random.randint(0, 100)

    def check_bounds(self):
        if self.rect.y > SCREEN_HEIGHT + 50:
            self.kill()

class Soldier(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 30, 'soldier')
        self.vel_y = 0
        self.facing = -1
        self.speed = 2

    def update(self, platforms, player, bullets, all_sprites, bullet_img=None):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
        self.check_bounds()

        dist_x = player.rect.x - self.rect.x
        if 5 < abs(dist_x) < 500:
            if dist_x > 0: self.rect.x += self.speed; self.facing = 1
            else: self.rect.x -= self.speed; self.facing = -1
        
        self.shoot_timer += 1
        if self.shoot_timer > 90 and abs(dist_x) < 400:
            if (self.facing == 1 and dist_x > 0) or (self.facing == -1 and dist_x < 0):
                b = Bullet(self.rect.centerx, self.rect.centery, self.facing, 0, damage=10, is_enemy=True)
                bullets.add(b)
                all_sprites.add(b)
                self.shoot_timer = 0

class Tank(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, DARK_GREEN, 120, 'tank')
        self.image = pygame.Surface((90, 60))
        self.image.fill(DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        self.vel_y = 0
        self.speed = 1

    def update(self, platforms, player, bullets, all_sprites, bullet_img=None):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
        self.check_bounds()

        dist_x = player.rect.x - self.rect.x
        if 200 < abs(dist_x) < 700:
            if dist_x > 0: self.rect.x += self.speed
            else: self.rect.x -= self.speed

        self.shoot_timer += 1
        if self.shoot_timer > 150 and abs(dist_x) < 700:
            dx = 1 if dist_x > 0 else -1
            b = Bullet(self.rect.centerx, self.rect.centery - 10, dx, 0, damage=35, is_enemy=True)
            bullets.add(b)
            all_sprites.add(b)
            self.shoot_timer = 0

class Helicopter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, GREY, 60, 'heli')
        self.start_y = y
        self.phase = 0

    def update(self, platforms, player, bullets, all_sprites, bullet_img=None):
        self.phase += 0.05
        self.rect.y = self.start_y + math.sin(self.phase) * 30
        
        if self.rect.x < player.rect.x - 100: self.rect.x += 2
        elif self.rect.x > player.rect.x + 100: self.rect.x -= 2
        
        self.shoot_timer += 1
        if self.shoot_timer > 70 and abs(player.rect.x - self.rect.x) < 500:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)
            vel_x = math.cos(angle)
            vel_y = math.sin(angle)
            
            b = Bullet(self.rect.centerx, self.rect.bottom, vel_x, vel_y, damage=20, is_enemy=True, bullet_img=bullet_img)
            bullets.add(b)
            all_sprites.add(b)
            self.shoot_timer = 0

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
        pygame.display.set_caption("Metal Slug: Complete with Fixes")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)

        # Load Custom Bullet (Ganti dengan path gambar Anda)
        bullet_filename = 'bullet.png' 
        
        if os.path.exists(bullet_filename):
            try:
                raw_image = pygame.image.load(bullet_filename).convert_alpha()
                self.heli_bullet_img = pygame.transform.scale(raw_image, (25, 15))
            except Exception as e:
                self.heli_bullet_img = pygame.Surface((16, 16))
                self.heli_bullet_img.fill((150, 150, 150))
                pygame.draw.circle(self.heli_bullet_img, RED, (8,8), 6)
        else:
            self.heli_bullet_img = pygame.Surface((16, 16))
            self.heli_bullet_img.fill((150, 150, 150))
            pygame.draw.circle(self.heli_bullet_img, RED, (8,8), 6)

        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.grenades = pygame.sprite.Group()
        self.items = pygame.sprite.Group()
        
        # --- PERBAIKAN: Membuat grup untuk effects ---
        self.effects = pygame.sprite.Group() 

        self.player = Player()
        self.all_sprites.add(self.player)
        
        self.camera_x = 0
        self.world_limit = 0
        self.generate_chunk(0, 1000)
        
        self.battle_lock = False
        self.hmg_pickup_msg_timer = 0

    def generate_chunk(self, start_x, width):
        ground_y = SCREEN_HEIGHT - 60
        ground = Platform(start_x, ground_y, width, 100)
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        num_obstacles = width // 300
        for i in range(num_obstacles):
            obs_w = random.randint(80, 180)
            obs_h = random.choice([40, 80, 110])
            obs_x = start_x + random.randint(100, width - 100)
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
        if enemy.type_name == 'soldier':
            if random.random() < 0.10:
                item = HealthPack(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)
        elif enemy.type_name in ['tank', 'heli']:
            if random.random() < 0.25:
                item = MachineGunPickup(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)

    def update(self):
        visible_enemies = [
            e for e in self.enemies 
            if self.camera_x + 20 < e.rect.x < self.camera_x + SCREEN_WIDTH - 20
        ]
        self.battle_lock = len(visible_enemies) > 0

        target_cam = self.player.rect.centerx - SCREEN_WIDTH // 3
        if not self.battle_lock:
            self.camera_x += (target_cam - self.camera_x) * 0.1

        if self.player.rect.right > self.world_limit - 400:
            self.generate_chunk(self.world_limit, 1200)

        # Update Player
        self.player.get_input(self.all_sprites, self.bullets, self.grenades, self.battle_lock, self.camera_x)
        self.player.update(self.platforms)
        
        # --- PERBAIKAN: Memasukkan self.effects ke parameter ---
        self.player.check_auto_melee(self.enemies, self.all_sprites, self.effects, self.spawn_loot)
        
        # Update Groups
        self.bullets.update()
        self.grenades.update()
        self.enemy_bullets.update()
        self.items.update(self.platforms)
        
        # --- PERBAIKAN: Update effects agar timer berjalan ---
        self.effects.update()
        
        for e in self.enemies:
            if -400 < e.rect.x - self.player.rect.x < 1500:
                e.update(self.platforms, self.player, self.enemy_bullets, self.all_sprites, bullet_img=self.heli_bullet_img)

        # Collisions
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for e, b_list in hits.items():
            dmg = sum([b.damage for b in b_list])
            e.hp -= dmg
            if e.hp <= 0: 
                self.spawn_loot(e)
                e.kill()

        g_hits = pygame.sprite.groupcollide(self.enemies, self.grenades, False, False)
        for e, g_list in g_hits.items():
            e.hp -= 40
            for g in g_list: g.kill()
            if e.hp <= 0: 
                self.spawn_loot(e)
                e.kill()

        player_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in player_hit_list:
            self.player.take_damage(bullet.damage)

        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            if item.type_name == 'heal':
                self.player.hp = min(self.player.max_hp, self.player.hp + 30)
            elif item.type_name == 'mg':
                self.player.weapon_type = "hmg"
                self.player.ammo = 100
                self.hmg_pickup_msg_timer = 60

        if self.player.hp <= 0:
            print("GAME OVER")
            self.running = False
        
        if self.hmg_pickup_msg_timer > 0:
            self.hmg_pickup_msg_timer -= 1

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f and self.player.weapon_type == "pistol" and not self.player.is_shielding:
                     self.player.fire_bullet(self.bullets, self.all_sprites)
                
                if event.key == pygame.K_F1:
                    for e in self.enemies: e.kill()

    def draw(self):
        self.screen.fill(BLACK)
        
        for s in self.all_sprites:
            off_x = s.rect.x - int(self.camera_x)
            if (off_x + s.rect.width > -50) and (off_x < SCREEN_WIDTH + 50):
                self.screen.blit(s.image, (off_x, s.rect.y))
                if isinstance(s, Player) and s.is_shielding:
                    pygame.draw.circle(self.screen, CYAN, (off_x + 15, s.rect.y + 25), 40, 2)
        
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
        
        w_txt = "PISTOL"
        w_col = WHITE
        if self.player.weapon_type == "hmg":
            w_txt = f"MACHINE GUN ({self.player.ammo})"
            w_col = GOLD
        
        txt_weapon = self.font.render(w_txt, True, w_col)
        self.screen.blit(txt_weapon, (10, 60))
        
        txt_info = self.font.render("F: Shoot (Hold for MG) | C: Shield | G: Grenade", True, GREY)
        self.screen.blit(txt_info, (220, 10))

        if self.battle_lock:
            warn = self.font.render("LOCKED!", True, RED)
            self.screen.blit(warn, (SCREEN_WIDTH//2 - 40, 50))
            barrier_screen_x = SCREEN_WIDTH - 40
            pygame.draw.line(self.screen, RED, (barrier_screen_x, 0), (barrier_screen_x, SCREEN_HEIGHT), 2)

        if self.hmg_pickup_msg_timer > 0:
            msg = self.big_font.render("HEAVY MACHINE GUN!", True, GOLD)
            self.screen.blit(msg, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))

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