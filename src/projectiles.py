import pygame, math, os
from settings import *

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, damage=10, is_enemy=False, is_hmg=False, bullet_img=None, miss_callback=None):
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
    def __init__(self, x, y, direction, is_enemy=False, miss_callback=None):
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
        self.miss_callback = miss_callback # Grenade penalty miss

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
