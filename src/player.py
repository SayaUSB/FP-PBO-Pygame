import pygame
from settings import *
from .projectiles import Bullet, Grenade
from .effects import MeleeEffect, SoldierDeath

class Player(pygame.sprite.Sprite):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref
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
        
        self.max_hp = 200
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

        self.hazard_iframes = 0

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
            g = Grenade(self.rect.centerx, self.rect.centery, self.facing, miss_callback=self.game_ref.apply_miss_penalty)
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
        
        b = Bullet(self.rect.centerx, self.rect.centery, dx, dy, damage=dmg, is_hmg=is_hmg, miss_callback=self.game_ref.apply_miss_penalty)
        all_sprites.add(b)
        bullets.add(b)

        if is_hmg:
            self.ammo -= 1
            if self.ammo <= 0:
                self.weapon_type = "pistol"

    def check_auto_melee(self, enemies, all_sprites, effects_group, spawn_loot_callback, add_score_callback):
        if self.melee_cd > 0 or self.is_shielding:
            return

        for e in enemies:
            if e.type_name == 'tank' or e.type_name == 'heli': continue
            dist_x = abs(self.rect.centerx - e.rect.centerx)
            dist_y = abs(self.rect.centery - e.rect.centery)

            if dist_x < self.melee_range and dist_y < self.melee_range:
                e.hp -= self.melee_dmg
                slash = MeleeEffect(e.rect.centerx, e.rect.centery)
                all_sprites.add(slash)
                effects_group.add(slash)
                
                self.melee_cd = 40 
                
                add_score_callback(50) 
                
                if e.hp <= 0:
                    if e.type_name in ('soldier', 'paratrooper'):
                        death = SoldierDeath(e.rect.centerx, e.rect.bottom - 15, facing=getattr(e, 'facing', 1))
                        all_sprites.add(death)
                        effects_group.add(death)
                    spawn_loot_callback(e) 
                    add_score_callback(e.score_val) # Kill Bonus
                    e.kill()
                break 

    def take_damage(self, amount):
        self.shield_regen_timer = 180 
        if self.is_shielding:
            blocked_amount = amount
            if self.shield < amount:
                blocked_amount = self.shield 

            block_bonus = int(blocked_amount * 5)
            self.game_ref.add_score(block_bonus)

            self.shield -= amount
            if self.shield < 0:
                self.hp -= abs(self.shield)
                self.shield = 0
                self.is_shielding = False
        else:
            self.hp -= amount
            self.game_ref.apply_damage_penalty(50) # Damage penalty

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

            if self.hazard_iframes <= 0 and getattr(p, 'damage', 0) > 0:
                self.take_damage(getattr(p, 'damage', 0))
                self.hazard_iframes = 30

        self.rect.x = int(self.pos_x)

        if self.rect.y > SCREEN_HEIGHT + 200: self.hp = 0 
        
        # cooldowns
        if self.grenade_cd > 0: self.grenade_cd -= 1 * DT
        if self.shoot_delay > 0: self.shoot_delay -= 1 * DT
        if self.melee_cd > 0: self.melee_cd -= 1 * DT
        if self.hazard_iframes > 0: self.hazard_iframes -= 1 * DT
        
        # shield logic
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
