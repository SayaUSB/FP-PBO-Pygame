import json
import pygame
from .Entity import Entity
from .AttackHitbox import AttackHitbox

def load_config():
    filename = "config/config.json"
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

CONFIG = load_config() 

class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 40, 60, "TODO: ASSETS", (0, 0, 255))
        self.speed = 5
        self.jump_power = -15
        self.gravity = 0.8
        self.on_ground = False
        
        self.is_stunned = False     
        self.stun_timer = 0         
        self.invulnerable = False   
        self.invul_timer = 0        
        self.last_attack_time = 0
        self.attack_cooldown = 500

    def take_damage(self, source_rect):
        if self.invulnerable:
            return

        if source_rect.centerx > self.rect.centerx:
            self.vel_x = -10  
        else:
            self.vel_x = 10   
        self.vel_y = -10      
        
        self.is_stunned = True
        self.stun_timer = pygame.time.get_ticks()
        
        self.invulnerable = True
        self.invul_timer = pygame.time.get_ticks()
        
        self.image.fill((255, 0, 0)) 

    def attack(self, all_sprites, attack_group):
        now = pygame.time.get_ticks()

        if now - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = now
            attack = AttackHitbox(self)
            all_sprites.add(attack)
            attack_group.add(attack)

    def update(self, platforms, all_sprites, attack_group):
        current_time = pygame.time.get_ticks()

        if self.is_stunned:
            if current_time - self.stun_timer > 300:
                self.is_stunned = False
        
        if self.invulnerable:
            if current_time - self.invul_timer > 1000:
                self.invulnerable = False
                self.image.fill((0, 0, 255)) 

        if not self.is_stunned: 
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.vel_x = -self.speed
                self.direction = -1
            elif keys[pygame.K_RIGHT]:
                self.vel_x = self.speed
                self.direction = 1
            else:
                self.vel_x = 0

            if keys[pygame.K_UP] and self.on_ground:
                self.vel_y = self.jump_power
                self.on_ground = False

            if keys[pygame.K_z] and not self.is_stunned:
                self.attack(all_sprites, attack_group)
        
        self.vel_y += self.gravity
        
        self.rect.x += self.vel_x
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.vel_x > 0: self.rect.right = platform.rect.left
            elif self.vel_x < 0: self.rect.left = platform.rect.right

        self.rect.y += self.vel_y
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = platform.rect.bottom
                self.vel_y = 0
        
        if self.rect.top > CONFIG.get("SCREEN_HEIGHT"):
            self.rect.x = 100
            self.rect.y = 100
            self.vel_y = 0