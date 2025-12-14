import pygame, random, math
from settings import *
from .projectiles import Bullet, Missile, Grenade

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, color, hp, type_name, score_val, hit_score):
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
        self.hit_score = hit_score      
        self.shoot_timer = random.randint(0, 100)

    def check_bounds(self):
        if self.rect.y > SCREEN_HEIGHT + 50:
            self.kill()

class Soldier(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 30, 'soldier', 100, 10)
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
        super().__init__(x, y, DARK_GREEN, 120, 'tank', 300, 30)
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
        super().__init__(x, y, GREY, 60, 'heli', 500, 50)

        self.start_y = y
        self.phase = 0
        self.pos_x = float(x)

        self.width = 100
        self.height = 50

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.rotor_angle = 0

    def draw_helicopter(self):
        self.image.fill((0, 0, 0, 0))

        # BODY
        pygame.draw.ellipse(
            self.image,
            (120, 120, 120),
            (20, 30, 70, 25)
        )

        # COCKPIT
        pygame.draw.ellipse(
            self.image,
            (180, 180, 200),
            (55, 32, 30, 20)
        )

        # TAIL
        pygame.draw.rect(
            self.image,
            (100, 100, 100),
            (85, 38, 30, 6)
        )

        # MAIN ROTOR
        cx, cy = 55, 18
        length = 50
        angle = self.rotor_angle

        x1 = cx + math.cos(angle) * length
        y1 = cy + math.sin(angle) * length
        x2 = cx - math.cos(angle) * length
        y2 = cy - math.sin(angle) * length

        pygame.draw.line(
            self.image,
            (30, 30, 30),
            (x1, y1),
            (x2, y2),
            5
        )

        # ROTOR HUB
        pygame.draw.circle(self.image, (50, 50, 50), (cx, cy), 4)

        # TAIL ROTOR
        pygame.draw.line(
            self.image,
            (50, 50, 50),
            (112, 41),
            (118, 41),
            3
        )


    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.phase += 0.05 * DT
        self.rect.y = self.start_y + math.sin(self.phase) * 30

        if self.rect.x < player.rect.x - 200:
            self.pos_x += 2 * DT
        elif self.rect.x > player.rect.x + 200:
            self.pos_x -= 2 * DT

        self.rect.x = int(self.pos_x)

        self.rotor_angle += 0.4 * DT

        self.draw_helicopter()

        # Shooting
        self.shoot_timer += 1 * DT
        if self.shoot_timer > 70 and abs(player.rect.x - self.rect.x) < 1000:
            dx = player.rect.centerx - self.rect.centerx
            dy = player.rect.centery - self.rect.centery
            angle = math.atan2(dy, dx)

            vel_x = math.cos(angle)
            vel_y = math.sin(angle)

            b = Bullet(
                self.rect.centerx,
                self.rect.bottom,
                vel_x,
                vel_y,
                damage=20,
                is_enemy=True,
                bullet_img=bullet_img
            )
            bullets.add(b)
            all_sprites.add(b)
            self.shoot_timer = 0

class BossHelicopter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, PURPLE, 5000, 'boss_heli', 10000, 100)
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
        self.state = "move"
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
