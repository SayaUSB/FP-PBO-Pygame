import pygame, math, os
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage=10, is_enemy=False, is_hmg=False, bullet_img=None, miss_callback=None):
        super().__init__()
        if bullet_img:
            self.image = bullet_img
        else:
            color = GOLD if is_hmg else (RED if is_enemy else YELLOW)
            dark = (max(0, color[0] - 60), max(0, color[1] - 60), max(0, color[2] - 60))
            glow = (min(255, color[0] + 80), min(255, color[1] + 80), min(255, color[2] + 80))

            w, h = ((20, 8) if is_hmg else (16, 6))
            self.original_image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(self.original_image, (*glow, 140), (0, 1, w - 2, h - 2), border_radius=3)
            pygame.draw.rect(self.original_image, color, (2, 1, w - 6, h - 2), border_radius=3)
            pygame.draw.polygon(self.original_image, color, [(w - 6, 1), (w, h // 2), (w - 6, h - 1)])
            pygame.draw.rect(self.original_image, dark, (2, 1, w - 6, h - 2), 2, border_radius=3)
            pygame.draw.polygon(self.original_image, dark, [(w - 6, 1), (w, h // 2), (w - 6, h - 1)], 2)

            if dx == 0 and dy == 0:
                angle_deg = 0
            else:
                angle_deg = -math.degrees(math.atan2(dy, dx))

            self.image = pygame.transform.rotate(self.original_image, angle_deg)
            
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.speed = 10 if is_enemy else (20 if is_hmg else 15)
        self.vel_x = dx * self.speed
        self.vel_y = dy * self.speed
        
        self.damage = damage
        self.is_enemy = is_enemy
        self.miss_callback = miss_callback 

    def update(self):
        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        # Logic Bullet Miss
        if self.rect.right < -100 or self.rect.left > 100000:
            if self.miss_callback and not self.is_enemy: 
                self.miss_callback(5)
            self.kill()
            
        if self.rect.y > SCREEN_HEIGHT + 100 or self.rect.y < -100:
            if self.miss_callback and not self.is_enemy:
                self.miss_callback(5)
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, target):
        super().__init__()
        self.original_image = pygame.Surface((34, 14), pygame.SRCALPHA)
        body = (80, 170, 190)
        body_dark = (40, 110, 130)
        tip = (210, 60, 60)
        steel = (40, 40, 40)

        pygame.draw.rect(self.original_image, body, (8, 3, 22, 8), border_radius=4)
        pygame.draw.rect(self.original_image, body_dark, (10, 6, 18, 4), border_radius=3)
        pygame.draw.polygon(self.original_image, tip, [(30, 3), (34, 7), (30, 11)])
        pygame.draw.polygon(self.original_image, steel, [(14, 2), (18, 2), (16, 0)])
        pygame.draw.polygon(self.original_image, steel, [(14, 12), (18, 12), (16, 14)])
        pygame.draw.circle(self.original_image, (255, 220, 120), (12, 7), 2)

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
        self.flame_phase = 0
        self.explode_now = False

    def update(self):
        self.timer += 1 * DT
        self.flame_phase += 0.35 * DT
        
        if self.timer < self.tracking_limit:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            
            self.vel_x = math.cos(angle_rad) * self.speed
            self.vel_y = math.sin(angle_rad) * self.speed

            flame_len = 10 + int(4 * math.sin(self.flame_phase))
            flame = pygame.Surface(self.original_image.get_size(), pygame.SRCALPHA)
            flame.blit(self.original_image, (0, 0))
            pygame.draw.polygon(flame, (255, 180, 50, 200), [(8, 7), (max(0, 8 - flame_len), 3), (max(0, 8 - flame_len), 11)])
            pygame.draw.polygon(flame, (255, 240, 180, 160), [(8, 7), (max(0, 8 - (flame_len // 2)), 5), (max(0, 8 - (flame_len // 2)), 9)])

            self.image = pygame.transform.rotate(flame, -angle_deg)
            self.rect = self.image.get_rect(center=self.rect.center)

        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        if self.timer >= self.fuel_limit:
            self.explode_now = True

        if self.rect.x < -200 or self.rect.x > 100000:
            self.kill()

class Rocket(pygame.sprite.Sprite):
    def __init__(self, x, y, target=None, dx=1, dy=0):
        super().__init__()
        self.base_image = pygame.Surface((28, 12), pygame.SRCALPHA)
        body = (95, 100, 110)
        body_dark = (55, 60, 70)
        tip = (220, 70, 70)
        fin = (80, 85, 95)

        pygame.draw.rect(self.base_image, body, (6, 2, 16, 8), border_radius=3)
        pygame.draw.rect(self.base_image, body_dark, (7, 5, 13, 3), border_radius=2)
        pygame.draw.polygon(self.base_image, tip, [(22, 2), (28, 6), (22, 10)])
        pygame.draw.polygon(self.base_image, fin, [(10, 2), (6, 0), (12, 2)])
        pygame.draw.polygon(self.base_image, fin, [(10, 10), (6, 12), (12, 10)])

        self.image = self.base_image
        self.rect = self.image.get_rect(center=(x, y))

        self.target = target
        self.speed = 26.0
        self.damage = 120

        self.pos_x = float(x)
        self.pos_y = float(y)

        self.timer = 0
        self.tracking_limit = 200
        self.fuel_limit = 260

        self.vel_x = float(dx)
        self.vel_y = float(dy)
        self.flame_phase = 0.0
        self.explode_now = False
        self.did_explode = False

    def update(self, platforms=None):
        self.timer += 1 * DT
        self.flame_phase += 0.35 * DT

        desired_x = self.vel_x
        desired_y = self.vel_y

        if self.timer < self.tracking_limit and self.target is not None and getattr(self.target, 'rect', None) is not None:
            dx = self.target.rect.centerx - self.rect.centerx
            dy = self.target.rect.centery - self.rect.centery
            ang = math.atan2(dy, dx)
            desired_x = math.cos(ang)
            desired_y = math.sin(ang)

        if platforms is not None:
            mag = math.hypot(desired_x, desired_y)
            if mag > 0:
                nx = desired_x / mag
                ny = desired_y / mag
            else:
                nx = 1.0
                ny = 0.0

            look = 90
            ahead = pygame.Rect(
                int(self.pos_x + nx * look - 30),
                int(self.pos_y + ny * look - 20),
                60,
                40,
            )

            if pygame.sprite.spritecollideany(self, platforms, collided=lambda s, p: ahead.colliderect(p.rect)):
                desired_y -= 1.15
                desired_x += 0.10 * (1 if nx >= 0 else -1)

        steer = 0.22
        self.vel_x = (1.0 - steer) * self.vel_x + steer * desired_x
        self.vel_y = (1.0 - steer) * self.vel_y + steer * desired_y

        mag = math.hypot(self.vel_x, self.vel_y)
        if mag > 0:
            vx = (self.vel_x / mag) * self.speed
            vy = (self.vel_y / mag) * self.speed
        else:
            vx = self.speed
            vy = 0.0

        self.pos_x += vx * DT
        self.pos_y += vy * DT
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

        angle_deg = -math.degrees(math.atan2(vy, vx)) if (vx != 0 or vy != 0) else 0
        flame_len = 9 + int(4 * math.sin(self.flame_phase))
        flame = pygame.Surface(self.base_image.get_size(), pygame.SRCALPHA)
        flame.blit(self.base_image, (0, 0))
        pygame.draw.polygon(flame, (255, 170, 60, 200), [(6, 6), (max(0, 6 - flame_len), 2), (max(0, 6 - flame_len), 10)])
        pygame.draw.polygon(flame, (255, 240, 200, 150), [(6, 6), (max(0, 6 - (flame_len // 2)), 4), (max(0, 6 - (flame_len // 2)), 8)])

        self.image = pygame.transform.rotate(flame, angle_deg)
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.timer >= self.fuel_limit:
            self.explode_now = True

        if self.rect.right < -300 or self.rect.left > 100000:
            self.kill()
        if self.rect.top > SCREEN_HEIGHT + 400 or self.rect.bottom < -600:
            self.kill()

class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, is_enemy=False, miss_callback=None):
        super().__init__()
        color = RED if is_enemy else ORANGE
        self.original_image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(self.original_image, color, (9, 9), 8)
        pygame.draw.circle(self.original_image, (255, 255, 255, 80), (7, 7), 4)
        pygame.draw.circle(self.original_image, (30, 30, 30), (9, 9), 8, 2)
        pygame.draw.rect(self.original_image, (220, 220, 220), (7, 1, 4, 4), border_radius=2)
        pygame.draw.circle(self.original_image, (220, 220, 220), (9, 1), 2)
        self.image = self.original_image
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.pos_x = float(x)
        self.pos_y = float(y)
        
        self.vel_x = direction * (0 if is_enemy else 12) 
        self.vel_y = 5 if is_enemy else -14
        self.timer = 60 
        self.explode_now = False
        self.is_enemy = is_enemy
        self.miss_callback = miss_callback # Grenade penalty miss
        self.angle = 0
        self.spin = (9 if is_enemy else 12) * direction

    def update(self):
        self.vel_y += GRAVITY * DT
        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
        self.timer -= 1 * DT
        
        if self.timer <= 0:
            self.explode_now = True
            
        if self.rect.y > SCREEN_HEIGHT + 200:
            if self.miss_callback and not self.is_enemy:
                self.miss_callback(20) 
            self.kill()
