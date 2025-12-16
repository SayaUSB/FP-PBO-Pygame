import pygame
from settings import *
from .projectiles import Bullet, Grenade, Rocket
from .effects import MeleeEffect, SoldierDeath

class Player(pygame.sprite.Sprite):
    def __init__(self, game_ref):
        super().__init__()
        self.game_ref = game_ref
        self.width = 44
        self.height = 64
        self.frames = self._build_frames()
        self.aim_pose = 'side'
        self.shoot_pose = 'side'
        self.shoot_anim_timer = 0
        self.walk_timer = 0
        self.walk_index = 0

        self.image = self.frames[1]['idle']
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

    def _draw_player_frame(self, facing, pose, step=0):
        w = self.width
        h = self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        skin = (220, 180, 140)
        helmet = (50, 70, 95)
        helmet_dark = (35, 50, 70)
        visor = (140, 200, 220)
        suit = (45, 110, 210)
        suit_dark = (25, 70, 150)
        suit_light = (90, 165, 245)
        vest = (30, 45, 65)
        vest_dark = (20, 30, 45)
        backpack = (35, 35, 35)
        backpack_dark = (25, 25, 25)
        gloves = (22, 22, 22)
        boots = (25, 25, 25)
        gun = (20, 20, 20)
        gun_dark = (70, 70, 70)

        bob = 0
        leg = 0
        arm = 0
        if pose == 'run':
            bob = [0, -1, 0, 1][step % 4]
            leg = [-2, 1, 2, -1][step % 4]
            arm = [1, -1, 0, 0][step % 4]

        head_r = 8
        head = (int(w * 0.40), int(h * 0.18) + bob)
        pygame.draw.circle(surf, skin, head, head_r)
        pygame.draw.circle(surf, helmet, (head[0], head[1] - 2), head_r + 3)
        pygame.draw.circle(surf, helmet_dark, (head[0] - 2, head[1] - 4), head_r + 3, 2)
        pygame.draw.rect(surf, visor, (head[0] - 7, head[1] - 3, 14, 5), border_radius=2)
        pygame.draw.circle(surf, (20, 20, 20), head, head_r + 2, 1)

        torso = pygame.Rect(int(w * 0.26), int(h * 0.28) + bob, int(w * 0.34), int(h * 0.28))
        pack = pygame.Rect(torso.x - 8, torso.y + 6, 10, int(torso.h * 0.75))
        pygame.draw.rect(surf, backpack, pack, border_radius=3)
        pygame.draw.rect(surf, backpack_dark, (pack.x, pack.y + pack.h // 2, pack.w, pack.h // 2), border_radius=3)

        pygame.draw.rect(surf, suit, torso, border_radius=6)
        pygame.draw.rect(surf, suit_dark, (torso.x, torso.y + torso.h // 2, torso.w, torso.h // 2), border_radius=6)
        pygame.draw.rect(surf, suit_light, (torso.x + 4, torso.y + 4, torso.w - 8, 6), border_radius=3)

        vest_rect = pygame.Rect(torso.x + 2, torso.y + 4, torso.w - 4, torso.h - 2)
        pygame.draw.rect(surf, vest, vest_rect, border_radius=5)
        pygame.draw.rect(surf, vest_dark, (vest_rect.x, vest_rect.y + vest_rect.h // 2, vest_rect.w, vest_rect.h // 2), border_radius=5)
        pygame.draw.line(surf, (90, 95, 105), (vest_rect.centerx, vest_rect.y + 4), (vest_rect.centerx, vest_rect.bottom - 4), 2)
        pygame.draw.circle(surf, (170, 170, 170), (vest_rect.centerx - 4, vest_rect.y + 10), 2)
        pygame.draw.circle(surf, (170, 170, 170), (vest_rect.centerx + 4, vest_rect.y + 10), 2)

        hip_y = int(h * 0.58) + bob
        left_hip = (int(w * 0.34), hip_y)
        right_hip = (int(w * 0.48), hip_y)
        left_foot = (int(w * 0.30) + leg, int(h * 0.92))
        right_foot = (int(w * 0.52) - leg, int(h * 0.92))
        pygame.draw.line(surf, suit, left_hip, left_foot, 7)
        pygame.draw.line(surf, suit, right_hip, right_foot, 7)
        pygame.draw.rect(surf, boots, (left_foot[0] - 6, left_foot[1] - 3, 14, 7), border_radius=2)
        pygame.draw.rect(surf, boots, (right_foot[0] - 6, right_foot[1] - 3, 14, 7), border_radius=2)

        pygame.draw.circle(surf, vest_dark, (left_foot[0], int(h * 0.76) + bob), 4)
        pygame.draw.circle(surf, vest_dark, (right_foot[0], int(h * 0.76) + bob), 4)

        shoulder_y = int(h * 0.38) + bob
        left_shoulder = (int(w * 0.30), shoulder_y)
        right_shoulder = (int(w * 0.52), shoulder_y)

        left_hand = (int(w * 0.22), int(h * 0.48) + bob + arm)
        right_hand = (int(w * 0.66), int(h * 0.44) + bob - arm)

        if pose.startswith('shoot'):
            if pose == 'shoot_up':
                right_hand = (int(w * 0.54), int(h * 0.22) + bob)
            elif pose == 'shoot_down':
                right_hand = (int(w * 0.54), int(h * 0.62) + bob)
            elif pose == 'shoot_down_diag':
                right_hand = (int(w * 0.66), int(h * 0.58) + bob)
            else:
                right_hand = (int(w * 0.66), int(h * 0.42) + bob)

        pygame.draw.line(surf, suit, left_shoulder, left_hand, 6)
        pygame.draw.line(surf, suit, right_shoulder, right_hand, 6)

        pygame.draw.circle(surf, gloves, left_hand, 3)
        pygame.draw.circle(surf, gloves, right_hand, 3)

        if pose.startswith('shoot'):
            if pose == 'shoot_up':
                gun_rect = pygame.Rect(right_hand[0] - 4, right_hand[1] - 20, 8, 26)
                pygame.draw.rect(surf, gun, gun_rect, border_radius=2)
                pygame.draw.rect(surf, gun_dark, (gun_rect.x + 1, gun_rect.y + 4, gun_rect.w - 2, 6), border_radius=2)
                pygame.draw.circle(surf, (255, 220, 80), (gun_rect.centerx, gun_rect.y - 2), 3)
            elif pose == 'shoot_down':
                gun_rect = pygame.Rect(right_hand[0] - 4, right_hand[1] - 2, 8, 26)
                pygame.draw.rect(surf, gun, gun_rect, border_radius=2)
                pygame.draw.rect(surf, gun_dark, (gun_rect.x + 1, gun_rect.y + 10, gun_rect.w - 2, 6), border_radius=2)
                pygame.draw.circle(surf, (255, 220, 80), (gun_rect.centerx, gun_rect.bottom + 2), 3)
            elif pose == 'shoot_down_diag':
                pts = [(right_hand[0] - 2, right_hand[1] - 2), (right_hand[0] + 18, right_hand[1] + 12), (right_hand[0] + 14, right_hand[1] + 16), (right_hand[0] - 6, right_hand[1] + 2)]
                pygame.draw.polygon(surf, gun, pts)
                pygame.draw.polygon(surf, gun_dark, [(pts[0][0] + 1, pts[0][1] + 3), (pts[1][0] - 2, pts[1][1] + 2), (pts[2][0] - 2, pts[2][1] + 2), (pts[3][0] + 1, pts[3][1] + 2)])
                pygame.draw.circle(surf, (255, 220, 80), (right_hand[0] + 20, right_hand[1] + 14), 3)
            else:
                gun_rect = pygame.Rect(int(w * 0.56), int(h * 0.41) + bob, int(w * 0.30), 6)
                pygame.draw.rect(surf, gun, gun_rect, border_radius=2)
                pygame.draw.rect(surf, gun_dark, (gun_rect.x + 6, gun_rect.y + 1, 9, 4), border_radius=2)
                pygame.draw.circle(surf, (255, 220, 80), (gun_rect.right + 2, gun_rect.centery), 3)
        else:
            gun_rect = pygame.Rect(int(w * 0.56), int(h * 0.43) + bob, int(w * 0.26), 6)
            pygame.draw.rect(surf, gun, gun_rect, border_radius=2)
            pygame.draw.rect(surf, gun_dark, (gun_rect.x + 6, gun_rect.y + 1, 8, 4), border_radius=2)

        if facing == -1:
            surf = pygame.transform.flip(surf, True, False)
        return surf

    def _build_frames(self):
        frames = {
            1: {
                'idle': self._draw_player_frame(1, 'idle', 0),
                'run': [self._draw_player_frame(1, 'run', i) for i in range(4)],
                'shoot_side': self._draw_player_frame(1, 'shoot_side', 0),
                'shoot_up': self._draw_player_frame(1, 'shoot_up', 0),
                'shoot_down': self._draw_player_frame(1, 'shoot_down', 0),
                'shoot_down_diag': self._draw_player_frame(1, 'shoot_down_diag', 0),
            },
            -1: {
                'idle': self._draw_player_frame(-1, 'idle', 0),
                'run': [self._draw_player_frame(-1, 'run', i) for i in range(4)],
                'shoot_side': self._draw_player_frame(-1, 'shoot_side', 0),
                'shoot_up': self._draw_player_frame(-1, 'shoot_up', 0),
                'shoot_down': self._draw_player_frame(-1, 'shoot_down', 0),
                'shoot_down_diag': self._draw_player_frame(-1, 'shoot_down_diag', 0),
            },
        }
        return frames

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

        if keys[pygame.K_UP]:
            self.aim_pose = 'up'
        elif keys[pygame.K_DOWN] and not self.on_ground:
            if keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:
                self.aim_pose = 'down_diag'
            else:
                self.aim_pose = 'down'
        else:
            self.aim_pose = 'side'

        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        if keys[pygame.K_g] and self.grenade_cd <= 0 and not self.is_shielding:
            g = Grenade(self.rect.centerx, self.rect.centery, self.facing, miss_callback=self.game_ref.apply_miss_penalty)
            all_sprites.add(g)
            grenades.add(g)
            self.grenade_cd = self.max_grenade_cd 

        if keys[pygame.K_f] and self.weapon_type in ("hmg", "rocket") and not self.is_shielding:
            if self.shoot_delay <= 0:
                self.fire_bullet(bullets, all_sprites)
                self.shoot_delay = 5 if self.weapon_type == "hmg" else 18

    def fire_bullet(self, bullets, all_sprites):
        if self.weapon_type == "rocket":
            target = None
            best_d = None
            try:
                for e in getattr(self.game_ref, 'enemies', []):
                    if getattr(e, 'hp', 1) <= 0:
                        continue
                    dx = e.rect.centerx - self.rect.centerx
                    dy = e.rect.centery - self.rect.centery
                    d = dx * dx + dy * dy
                    if best_d is None or d < best_d:
                        best_d = d
                        target = e
                for e in getattr(self.game_ref, 'boss_group', []):
                    if getattr(e, 'hp', 1) <= 0:
                        continue
                    dx = e.rect.centerx - self.rect.centerx
                    dy = e.rect.centery - self.rect.centery
                    d = dx * dx + dy * dy
                    if best_d is None or d < best_d:
                        best_d = d
                        target = e
            except Exception:
                target = None

            r = Rocket(self.rect.centerx, self.rect.centery, target=target, dx=self.facing, dy=0)
            all_sprites.add(r)
            if hasattr(self.game_ref, 'rockets'):
                self.game_ref.rockets.add(r)
            self.shoot_pose = 'side'
            self.shoot_anim_timer = 10

            self.ammo -= 1
            if self.ammo <= 0:
                self.weapon_type = "pistol"
                self.ammo = 0
            return

        keys = pygame.key.get_pressed()
        dx, dy = self.facing, 0
        if keys[pygame.K_UP]: 
            dy = -1
            dx = 0 if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) else dx
        elif keys[pygame.K_DOWN] and not self.on_ground: 
            dy = 1
            if keys[pygame.K_LEFT]:
                dx = -1
            elif keys[pygame.K_RIGHT]:
                dx = 1
            else:
                dx = 0

        if dx != 0 and dy != 0:
            inv = 1.0 / (2 ** 0.5)
            dx *= inv
            dy *= inv

        if dy < 0:
            self.shoot_pose = 'up'
        elif dy > 0 and dx == 0:
            self.shoot_pose = 'down'
        elif dy > 0 and dx != 0:
            self.shoot_pose = 'down_diag'
        else:
            self.shoot_pose = 'side'
        self.shoot_anim_timer = 10
        
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
                    if e.type_name == 'turret':
                        if hasattr(self.game_ref, 'trigger_turret_death_explosion'):
                            self.game_ref.trigger_turret_death_explosion(e)
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

        if self.shoot_anim_timer > 0:
            self.shoot_anim_timer -= 1 * DT

        moving = pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_RIGHT]
        if moving:
            self.walk_timer += 0.18 * DT
            self.walk_index = int(self.walk_timer) % 4
        else:
            self.walk_timer = 0
            self.walk_index = 0

        if self.shoot_anim_timer > 0:
            key = 'shoot_side'
            if self.shoot_pose == 'up':
                key = 'shoot_up'
            elif self.shoot_pose == 'down':
                key = 'shoot_down'
            elif self.shoot_pose == 'down_diag':
                key = 'shoot_down_diag'
            self.image = self.frames[self.facing][key]
        elif moving:
            self.image = self.frames[self.facing]['run'][self.walk_index]
        else:
            self.image = self.frames[self.facing]['idle']
        
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
