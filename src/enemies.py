import pygame, random, math
from settings import *
from .projectiles import Bullet, Missile, Grenade
from .items import HealthPack

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
        self.width = 48
        self.height = 82
        self.facing = -1
        self.walk_timer = 0
        self.walk_index = 0
        self.shoot_anim_timer = 0
        self.frames = {
            1: {
                'idle': self._draw_soldier_frame(1, 0, False),
                'walk': [self._draw_soldier_frame(1, i, False) for i in range(4)],
                'shoot': self._draw_soldier_frame(1, 1, True),
            },
            -1: {
                'idle': self._draw_soldier_frame(-1, 0, False),
                'walk': [self._draw_soldier_frame(-1, i, False) for i in range(4)],
                'shoot': self._draw_soldier_frame(-1, 1, True),
            },
        }
        self.image = self.frames[self.facing]['idle']
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.vel_y = 0
        self.speed = 2

    def _draw_soldier_frame(self, facing, step, shooting):
        w = self.width
        h = self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        skin = (220, 180, 140)
        uniform = (70, 110, 70)
        uniform_dark = (45, 75, 45)
        helmet = (55, 70, 60)
        helmet_dark = (35, 45, 40)
        backpack = (60, 60, 60)
        backpack_dark = (40, 40, 40)
        boots = (30, 30, 30)
        gun = (25, 25, 25)
        visor = (120, 170, 190)

        head_r = max(7, int(h * 0.10))
        head_c = (int(w * 0.52), int(h * 0.18))
        pygame.draw.circle(surf, skin, head_c, head_r)
        pygame.draw.circle(surf, helmet, (head_c[0], head_c[1] - 1), head_r + 1)
        pygame.draw.circle(surf, helmet_dark, (head_c[0] - 2, head_c[1] - 2), head_r + 1, 2)
        pygame.draw.rect(surf, visor, (head_c[0] - head_r + 2, head_c[1] - 1, head_r * 2 - 4, max(3, head_r // 2)), border_radius=2)

        torso = pygame.Rect(int(w * 0.34), int(h * 0.28), int(w * 0.38), int(h * 0.30))
        pygame.draw.rect(surf, uniform, torso, border_radius=4)
        pygame.draw.rect(surf, uniform_dark, (torso.x, torso.y + torso.h // 2, torso.w, torso.h // 2), border_radius=4)

        pack = pygame.Rect(int(w * 0.22), int(h * 0.32), int(w * 0.16), int(h * 0.22))
        pygame.draw.rect(surf, backpack, pack, border_radius=3)
        pygame.draw.rect(surf, backpack_dark, (pack.x, pack.y + pack.h // 2, pack.w, pack.h // 2), border_radius=3)

        pelvis = pygame.Rect(int(w * 0.35), int(h * 0.58), int(w * 0.34), int(h * 0.10))
        pygame.draw.rect(surf, uniform_dark, pelvis, border_radius=3)

        walk = [
            (-3, 3, 2, -2),
            (2, -2, -3, 3),
            (3, -3, -2, 2),
            (-2, 2, 3, -3),
        ][step % 4]

        shoulder_y = int(h * 0.38)
        left_shoulder = (int(w * 0.36), shoulder_y)
        right_shoulder = (int(w * 0.66), shoulder_y)
        left_hand = (int(w * 0.28), int(h * 0.52) + walk[0])
        right_hand = (int(w * 0.80), int(h * 0.44) + walk[1])

        if shooting:
            right_hand = (int(w * 0.80), int(h * 0.42))

        pygame.draw.line(surf, uniform, left_shoulder, left_hand, 5)
        pygame.draw.line(surf, uniform, right_shoulder, right_hand, 5)

        hip_y = int(h * 0.70)
        left_hip = (int(w * 0.46), hip_y)
        right_hip = (int(w * 0.58), hip_y)
        left_foot = (int(w * 0.42) + walk[2], int(h * 0.96))
        right_foot = (int(w * 0.62) + walk[3], int(h * 0.96))
        pygame.draw.line(surf, uniform, left_hip, left_foot, 6)
        pygame.draw.line(surf, uniform, right_hip, right_foot, 6)
        pygame.draw.rect(surf, boots, (left_foot[0] - 7, left_foot[1] - 3, 14, 6), border_radius=2)
        pygame.draw.rect(surf, boots, (right_foot[0] - 7, right_foot[1] - 3, 14, 6), border_radius=2)

        recoil = -3 if shooting else 0
        gun_rect = pygame.Rect(int(w * 0.66) + recoil, int(h * 0.41), int(w * 0.30), max(5, int(h * 0.055)))
        pygame.draw.rect(surf, gun, gun_rect, border_radius=2)
        pygame.draw.rect(surf, (60, 60, 60), (gun_rect.x + int(w * 0.04), gun_rect.y + 1, int(w * 0.10), gun_rect.h - 2), border_radius=2)
        pygame.draw.rect(surf, gun, (gun_rect.right - 3, gun_rect.y + 1, 3, gun_rect.h - 2))

        if shooting:
            muzzle_x = gun_rect.right + 2
            muzzle_y = gun_rect.centery
            pygame.draw.polygon(surf, (255, 200, 60), [(muzzle_x, muzzle_y), (muzzle_x + 10, muzzle_y - 5), (muzzle_x + 10, muzzle_y + 5)])
            pygame.draw.circle(surf, (255, 240, 180), (muzzle_x + 6, muzzle_y), 3)

        if facing == -1:
            surf = pygame.transform.flip(surf, True, False)
        return surf

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
        moving = 5 < abs(dist_x) < 1000
        if moving:
            self.walk_timer += 0.14 * DT
            self.walk_index = int(self.walk_timer) % 4
        else:
            self.walk_timer = 0
            self.walk_index = 0

        if self.shoot_anim_timer > 0:
            self.shoot_anim_timer -= 1 * DT

        bl = self.rect.bottomleft
        if self.shoot_anim_timer > 0:
            self.image = self.frames[self.facing]['shoot']
        elif moving:
            self.image = self.frames[self.facing]['walk'][self.walk_index]
        else:
            self.image = self.frames[self.facing]['idle']
        self.rect = self.image.get_rect(bottomleft=bl)
        self.shoot_timer += 1 * DT

        if self.shoot_timer > 90 and abs(dist_x) < 800:
            if (self.facing == 1 and dist_x > 0) or (self.facing == -1 and dist_x < 0):
                b = Bullet(self.rect.centerx, self.rect.centery, self.facing, 0, damage=10, is_enemy=True)
                bullets.add(b)
                all_sprites.add(b)
                self.shoot_timer = 0
                self.shoot_anim_timer = 10

class TurretSoldier(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, (110, 110, 110), 85, 'turret', 220, 12)
        self.width = 54
        self.height = 78
        self.facing = 1

        self.image = self._draw_gunner_frame(self.facing, firing=False)
        self.rect = self.image.get_rect(bottomleft=(x, y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.vel_y = 0

        self.burst_left = 0
        self.burst_cd = 0
        self.shoot_timer = random.randint(20, 90)
        self.shoot_anim_timer = 0

    def _draw_gunner_frame(self, facing, firing=False):
        w = self.width
        h = self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        skin = (220, 180, 140)
        uniform = (70, 110, 70)
        uniform_dark = (45, 75, 45)
        helmet = (55, 70, 60)
        helmet_dark = (35, 45, 40)
        boots = (30, 30, 30)
        gun = (22, 22, 22)
        gun_dark = (60, 60, 60)
        heat = (255, 200, 60)
        visor = (120, 170, 190)

        head_r = 8
        head = (int(w * 0.50), int(h * 0.20))
        pygame.draw.circle(surf, skin, head, head_r)
        pygame.draw.circle(surf, helmet, (head[0], head[1] - 2), head_r + 3)
        pygame.draw.circle(surf, helmet_dark, (head[0] - 2, head[1] - 4), head_r + 3, 2)
        pygame.draw.rect(surf, visor, (head[0] - 7, head[1] - 3, 14, 5), border_radius=2)

        torso = pygame.Rect(int(w * 0.30), int(h * 0.32), int(w * 0.40), int(h * 0.30))
        pygame.draw.rect(surf, uniform, torso, border_radius=6)
        pygame.draw.rect(surf, uniform_dark, (torso.x, torso.y + torso.h // 2, torso.w, torso.h // 2), border_radius=6)

        hip_y = int(h * 0.68)
        left_hip = (int(w * 0.40), hip_y)
        right_hip = (int(w * 0.58), hip_y)
        left_foot = (int(w * 0.38), int(h * 0.96))
        right_foot = (int(w * 0.62), int(h * 0.96))
        pygame.draw.line(surf, uniform, left_hip, left_foot, 7)
        pygame.draw.line(surf, uniform, right_hip, right_foot, 7)
        pygame.draw.rect(surf, boots, (left_foot[0] - 6, left_foot[1] - 3, 14, 7), border_radius=2)
        pygame.draw.rect(surf, boots, (right_foot[0] - 6, right_foot[1] - 3, 14, 7), border_radius=2)

        shoulder_y = int(h * 0.44)
        left_shoulder = (int(w * 0.36), shoulder_y)
        right_shoulder = (int(w * 0.64), shoulder_y)
        left_hand = (int(w * 0.34), int(h * 0.56))
        right_hand = (int(w * 0.78), int(h * 0.50))
        pygame.draw.line(surf, uniform, left_shoulder, left_hand, 6)
        pygame.draw.line(surf, uniform, right_shoulder, right_hand, 6)

        recoil = -3 if firing else 0
        gun_y = int(h * 0.47)

        body_w = int(w * 0.34)
        body_h = 14
        body_x = int(w * 0.50) + recoil
        body_rect = pygame.Rect(body_x, gun_y - 3, body_w, body_h)
        pygame.draw.rect(surf, gun, body_rect, border_radius=4)
        pygame.draw.rect(surf, gun_dark, body_rect, 2, border_radius=4)
        pygame.draw.rect(surf, gun_dark, (body_rect.x + 6, body_rect.y + 3, 10, 6), border_radius=2)

        ammo_box = pygame.Rect(body_rect.x - 12, body_rect.y + 3, 12, 12)
        pygame.draw.rect(surf, (35, 35, 35), ammo_box, border_radius=2)
        pygame.draw.rect(surf, (15, 15, 15), ammo_box, 2, border_radius=2)
        pygame.draw.line(surf, (85, 85, 85), (ammo_box.right, ammo_box.centery), (body_rect.x + 2, body_rect.y + 2), 2)
        pygame.draw.line(surf, (85, 85, 85), (ammo_box.right, ammo_box.centery), (body_rect.x + 2, body_rect.bottom - 2), 2)

        cluster_len = int(w * 0.22)
        barrel_spacing = 2
        barrel_count = 6
        cluster_x = body_rect.right - 4
        cluster_y = body_rect.centery - ((barrel_count - 1) * barrel_spacing) // 2
        for i in range(barrel_count):
            by = cluster_y + i * barrel_spacing
            pygame.draw.line(surf, gun_dark, (cluster_x, by), (cluster_x + cluster_len, by), 2)
        pygame.draw.circle(surf, gun_dark, (cluster_x, body_rect.centery), 6, 2)
        pygame.draw.circle(surf, (90, 90, 90), (cluster_x, body_rect.centery), 4)

        grip = pygame.Rect(body_rect.x + 8, body_rect.bottom - 1, 10, 12)
        pygame.draw.rect(surf, (25, 25, 25), grip, border_radius=3)
        pygame.draw.rect(surf, (10, 10, 10), grip, 2, border_radius=3)

        if firing:
            mx = cluster_x + cluster_len + 2
            my = body_rect.centery
            for k in (-4, 0, 4):
                pygame.draw.polygon(surf, heat, [(mx, my + k), (mx + 12, my + k - 5), (mx + 12, my + k + 5)])
            pygame.draw.circle(surf, (255, 240, 180), (mx + 6, my), 3)

        if facing == -1:
            surf = pygame.transform.flip(surf, True, False)
        return surf

    def update(self, platforms, player, bullets, all_sprites, missiles_group=None, grenades_group=None, bullet_img=None):
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

        dist_x = player.rect.centerx - self.rect.centerx
        dist_y = player.rect.centery - self.rect.centery
        self.facing = 1 if dist_x >= 0 else -1

        if self.shoot_anim_timer > 0:
            self.shoot_anim_timer -= 1 * DT

        if self.burst_cd > 0:
            self.burst_cd -= 1 * DT

        self.shoot_timer += 1 * DT
        in_range = abs(dist_x) < 950

        if in_range and self.burst_left <= 0 and self.shoot_timer > 70:
            self.burst_left = random.randint(4, 7)
            self.burst_cd = 0
            self.shoot_timer = 0

        if in_range and self.burst_left > 0 and self.burst_cd <= 0:
            mag = math.hypot(dist_x, dist_y)
            if mag > 0.001:
                vx = dist_x / mag
                vy = dist_y / mag
                vx += random.uniform(-0.06, 0.06)
                vy += random.uniform(-0.05, 0.05)
                mag2 = math.hypot(vx, vy)
                if mag2 > 0.001:
                    vx /= mag2
                    vy /= mag2
                if hasattr(player, 'game_ref') and hasattr(player.game_ref, 'play_sfx'):
                    player.game_ref.play_sfx('gunshot_gatling_gun', cooldown_ms=1)
                b = Bullet(self.rect.centerx, self.rect.centery, vx, vy, damage=10, is_enemy=True, bullet_img=bullet_img)
                bullets.add(b)
                all_sprites.add(b)

            self.burst_left -= 1
            self.burst_cd = 6
            self.shoot_anim_timer = 6

        bl = self.rect.bottomleft
        firing = (self.shoot_anim_timer > 0)
        self.image = self._draw_gunner_frame(self.facing, firing=firing)
        self.rect = self.image.get_rect(bottomleft=bl)

class Paratrooper(Enemy):
    def __init__(self, game_ref, x, y):
        super().__init__(x, y, PINK, 35, 'paratrooper', 180, 12)
        self.game_ref = game_ref

        self.width = 56
        self.height = 96

        self.facing = random.choice([-1, 1])
        self.vel_y = 0.0
        self.fall_gravity = GRAVITY * 0.22
        self.max_fall_speed = 5.5
        self.drift_speed = 0.35

        self.shoot_timer = random.randint(0, 60)
        self.shot_mode = 0

        self.image = self._draw_paratrooper_frame(self.facing)
        self.rect = self.image.get_rect(midtop=(x, y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

    def _draw_paratrooper_frame(self, facing):
        w = self.width
        h = self.height
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        chute = (210, 210, 220)
        chute_dark = (160, 160, 175)
        cord = (70, 70, 70)
        skin = (220, 180, 140)
        uniform = (70, 110, 70)
        uniform_dark = (45, 75, 45)
        helmet = (55, 70, 60)
        gun = (25, 25, 25)

        canopy_rect = pygame.Rect(int(w * 0.08), 0, int(w * 0.84), int(h * 0.34))
        pygame.draw.ellipse(surf, chute, canopy_rect)
        pygame.draw.ellipse(surf, chute_dark, (canopy_rect.x + 8, canopy_rect.y + 10, canopy_rect.w - 16, canopy_rect.h - 18))
        pygame.draw.ellipse(surf, (40, 40, 55), canopy_rect, 2)

        harness_y = int(h * 0.44)
        left_attach = (int(w * 0.28), int(h * 0.30))
        right_attach = (int(w * 0.72), int(h * 0.30))
        body_center = (int(w * 0.50), harness_y)
        pygame.draw.line(surf, cord, left_attach, (body_center[0] - 10, body_center[1] - 8), 2)
        pygame.draw.line(surf, cord, right_attach, (body_center[0] + 10, body_center[1] - 8), 2)
        pygame.draw.line(surf, cord, (body_center[0] - 10, body_center[1] - 8), (body_center[0] - 16, body_center[1] + 8), 2)
        pygame.draw.line(surf, cord, (body_center[0] + 10, body_center[1] - 8), (body_center[0] + 16, body_center[1] + 8), 2)

        head_r = max(7, int(h * 0.08))
        head_c = (int(w * 0.50), int(h * 0.42))
        pygame.draw.circle(surf, skin, head_c, head_r)
        pygame.draw.circle(surf, helmet, (head_c[0], head_c[1] - 1), head_r + 1)
        pygame.draw.circle(surf, (35, 45, 40), (head_c[0] - 2, head_c[1] - 2), head_r + 1, 2)

        torso = pygame.Rect(int(w * 0.34), int(h * 0.50), int(w * 0.32), int(h * 0.22))
        pygame.draw.rect(surf, uniform, torso, border_radius=5)
        pygame.draw.rect(surf, uniform_dark, (torso.x, torso.y + torso.h // 2, torso.w, torso.h // 2), border_radius=5)
        pygame.draw.rect(surf, (60, 60, 60), (torso.x + 4, torso.y + 10, torso.w - 8, 6), border_radius=3)

        leg_y1 = int(h * 0.74)
        pygame.draw.line(surf, uniform, (int(w * 0.46), int(h * 0.70)), (int(w * 0.40), leg_y1), 6)
        pygame.draw.line(surf, uniform, (int(w * 0.54), int(h * 0.70)), (int(w * 0.60), leg_y1), 6)
        pygame.draw.rect(surf, (30, 30, 30), (int(w * 0.35), leg_y1 - 2, 14, 6), border_radius=2)
        pygame.draw.rect(surf, (30, 30, 30), (int(w * 0.56), leg_y1 - 2, 14, 6), border_radius=2)

        gun_w = int(w * 0.26)
        gun_h = max(5, int(h * 0.05))
        gun_x = int(w * 0.56)
        gun_y = int(h * 0.58)
        pygame.draw.rect(surf, gun, (gun_x, gun_y, gun_w, gun_h), border_radius=2)
        pygame.draw.rect(surf, (60, 60, 60), (gun_x + 6, gun_y + 1, 10, gun_h - 2), border_radius=2)

        if facing == -1:
            surf = pygame.transform.flip(surf, True, False)
        return surf

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        self.facing = 1 if player.rect.centerx >= self.rect.centerx else -1

        self.vel_y += self.fall_gravity * DT
        if self.vel_y > self.max_fall_speed:
            self.vel_y = self.max_fall_speed
        self.pos_y += self.vel_y * DT

        drift_dir = self.facing
        self.pos_x += (self.drift_speed * drift_dir) * DT

        self.rect.x = int(self.pos_x)
        self.rect.y = int(self.pos_y)

        ground_hits = [p for p in pygame.sprite.spritecollide(self, platforms, False) if getattr(p, 'is_ground', False) or p.rect.height >= 160]
        if ground_hits and self.vel_y > 0:
            ground = min(ground_hits, key=lambda p: p.rect.top)
            land_bottomleft = (self.rect.x, ground.rect.top)
            s = Soldier(land_bottomleft[0], land_bottomleft[1])
            self.game_ref.enemies.add(s)
            all_sprites.add(s)
            self.kill()
            return

        self.image = self._draw_paratrooper_frame(self.facing)
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.shoot_timer += 1 * DT
        if self.shoot_timer > 75 and abs(player.rect.centerx - self.rect.centerx) < 1200:
            inv = 1.0 / math.sqrt(2)
            if self.shot_mode == 0:
                b = Bullet(self.rect.centerx, self.rect.centery + 10, 0, 1, damage=10, is_enemy=True)
                bullets.add(b)
                all_sprites.add(b)
                self.shot_mode = 1
            else:
                b = Bullet(self.rect.centerx, self.rect.centery + 10, self.facing * inv, inv, damage=10, is_enemy=True)
                bullets.add(b)
                all_sprites.add(b)
                self.shot_mode = 0
            self.shoot_timer = 0

class Tank(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, DARK_GREEN, 120, 'tank', 300, 30)
        self.width = 240
        self.height = 140

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)

        self.vel_y = 0
        self.speed = 1
        self.turret_angle = 0

    def draw_tank(self, player):
        self.image.fill((0, 0, 0, 0))

        base = (30, 30, 30)
        steel = (80, 80, 80)
        tread = (35, 35, 35)
        tread_dark = (20, 20, 20)
        armor = (25, 90, 35)
        armor_dark = (18, 60, 24)
        armor_light = (50, 140, 65)
        warning = (200, 60, 60)

        pygame.draw.rect(self.image, tread, (14, 92, 212, 38), border_radius=18)
        pygame.draw.rect(self.image, tread_dark, (18, 98, 204, 26), border_radius=14)

        for i in range(9):
            cx = 32 + i * 22
            pygame.draw.circle(self.image, steel, (cx, 111), 12)
            pygame.draw.circle(self.image, (55, 55, 55), (cx, 111), 7)
            pygame.draw.circle(self.image, (25, 25, 25), (cx, 111), 3)

        pygame.draw.rect(self.image, tread_dark, (22, 102, 196, 4), border_radius=2)
        pygame.draw.rect(self.image, tread_dark, (22, 116, 196, 4), border_radius=2)

        hull = pygame.Rect(28, 54, 184, 44)
        pygame.draw.rect(self.image, armor, hull, border_radius=14)
        pygame.draw.rect(self.image, armor_dark, (hull.x + 6, hull.y + 18, hull.w - 12, hull.h - 22), border_radius=12)

        glacis = [(40, 58), (120, 44), (192, 56), (170, 74), (52, 74)]
        pygame.draw.polygon(self.image, armor_light, glacis)
        pygame.draw.polygon(self.image, armor_dark, [(x, y + 6) for (x, y) in glacis])

        for x in range(46, 200, 18):
            pygame.draw.circle(self.image, (15, 35, 18), (x, 76), 2)
            pygame.draw.circle(self.image, (15, 35, 18), (x, 92), 2)

        vent = pygame.Rect(60, 62, 52, 18)
        pygame.draw.rect(self.image, (18, 45, 22), vent, border_radius=4)
        for i in range(5):
            pygame.draw.line(self.image, (10, 20, 10), (vent.x + 6 + i * 9, vent.y + 4), (vent.x + 6 + i * 9, vent.y + vent.h - 4), 2)

        pygame.draw.rect(self.image, warning, (150, 70, 38, 10), border_radius=3)
        for i in range(4):
            pygame.draw.line(self.image, (30, 30, 30), (152 + i * 9, 70), (152 + i * 9 - 6, 80), 2)

        turret_base_center = (132, 54)
        pygame.draw.circle(self.image, armor_dark, turret_base_center, 30)
        pygame.draw.circle(self.image, armor, turret_base_center, 26)
        pygame.draw.circle(self.image, (12, 30, 14), turret_base_center, 10)

        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        self.turret_angle = math.atan2(dy, dx)

        barrel_length = 94
        end_x = turret_base_center[0] + math.cos(self.turret_angle) * barrel_length
        end_y = turret_base_center[1] + math.sin(self.turret_angle) * barrel_length
        mid_x = turret_base_center[0] + math.cos(self.turret_angle) * 34
        mid_y = turret_base_center[1] + math.sin(self.turret_angle) * 34

        pygame.draw.line(self.image, base, turret_base_center, (end_x, end_y), 14)
        pygame.draw.line(self.image, (55, 55, 55), turret_base_center, (end_x, end_y), 8)
        pygame.draw.circle(self.image, (25, 25, 25), (int(mid_x), int(mid_y)), 9)

        brake_x = turret_base_center[0] + math.cos(self.turret_angle) * (barrel_length - 8)
        brake_y = turret_base_center[1] + math.sin(self.turret_angle) * (barrel_length - 8)
        perp = self.turret_angle + math.pi / 2
        bx1 = brake_x + math.cos(perp) * 8
        by1 = brake_y + math.sin(perp) * 8
        bx2 = brake_x - math.cos(perp) * 8
        by2 = brake_y - math.sin(perp) * 8
        pygame.draw.line(self.image, (20, 20, 20), (bx1, by1), (bx2, by2), 4)
        pygame.draw.circle(self.image, (10, 10, 10), (int(end_x), int(end_y)), 7)

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        # Gravity
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

        # Move to player
        dist_x = player.rect.x - self.rect.x
        if 200 < abs(dist_x) < 1200:
            self.pos_x += self.speed * DT if dist_x > 0 else -self.speed * DT

        self.rect.x = int(self.pos_x)
        self.draw_tank(player)

        # Fire missile
        self.shoot_timer += 1 * DT
        if self.shoot_timer > 180 and abs(dist_x) < 1200:
            m = Missile(
                self.rect.centerx,
                self.rect.centery - 40,
                player
            )
            all_sprites.add(m)
            missiles_group.add(m)
            self.shoot_timer = 0

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
            if dist_x > 0:
                self.pos_x += self.speed * DT
            else:
                self.pos_x -= self.speed * DT

        self.rect.x = int(self.pos_x)
        self.draw_tank(player)

        # Missile
        self.shoot_timer += 1 * DT
        if self.shoot_timer > 180 and abs(dist_x) < 1200:
            m = Missile(
                self.rect.centerx,
                self.rect.centery - 30,
                player
            )
            all_sprites.add(m)
            missiles_group.add(m)
            self.shoot_timer = 0

class Helicopter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, GREY, 60, 'heli', 500, 50)

        self.start_y = y
        self.phase = 0
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_y = 0
        self.facing = 1

        self.crashing = False
        self.crash_vx = 0.0
        self.crash_angle = 0.0
        self.crash_spin = 0.0
        self.crash_impact = False
        self.crash_impact_pos = None

        self.width = 200
        self.height = 100

        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image = self.base_image
        self.rect = self.image.get_rect(topleft=(x, y))

        self.rotor_angle = 0

    def begin_crash(self):
        if self.crashing:
            return
        self.crashing = True
        self.crash_vx = (-1.2 if self.facing < 0 else 1.2) + random.uniform(-0.4, 0.4)
        self.crash_spin = (-2.5 if self.facing < 0 else 2.5) + random.uniform(-1.2, 1.2)
        self.vel_y = 0
        self.pos_x = float(self.rect.x)
        self.pos_y = float(self.rect.y)
        self.crash_angle = 0.0
        self.crash_impact = False
        self.crash_impact_pos = None

    def draw_helicopter(self):
        self.base_image.fill((0, 0, 0, 0))

        surf = self.base_image
        w, h = self.width, self.height
        body = (75, 85, 92)
        body_dark = (50, 58, 64)
        panel = (95, 105, 112)
        glass = (150, 200, 220)
        glass_dark = (110, 150, 170)
        metal = (35, 35, 35)

        fuselage = pygame.Rect(int(w * 0.16), int(h * 0.44), int(w * 0.56), int(h * 0.30))
        pygame.draw.ellipse(surf, body, fuselage)
        pygame.draw.ellipse(surf, body_dark, pygame.Rect(fuselage.x + 8, fuselage.y + 10, fuselage.w - 18, fuselage.h - 16))

        nose = [
            (int(w * 0.62), int(h * 0.48)),
            (int(w * 0.78), int(h * 0.56)),
            (int(w * 0.62), int(h * 0.74)),
        ]
        pygame.draw.polygon(surf, body, nose)
        pygame.draw.polygon(surf, body_dark, [(nose[0][0] - 6, nose[0][1] + 6), (nose[1][0] - 10, nose[1][1] + 6), (nose[2][0] - 6, nose[2][1] - 6)])

        cockpit = [
            (int(w * 0.56), int(h * 0.50)),
            (int(w * 0.73), int(h * 0.56)),
            (int(w * 0.69), int(h * 0.70)),
            (int(w * 0.54), int(h * 0.66)),
        ]
        pygame.draw.polygon(surf, glass, cockpit)
        pygame.draw.polygon(surf, glass_dark, [(p[0], p[1] + 5) for p in cockpit])
        pygame.draw.polygon(surf, metal, cockpit, 2)

        tail = pygame.Rect(int(w * 0.02), int(h * 0.56), int(w * 0.26), int(h * 0.10))
        pygame.draw.rect(surf, body, tail, border_radius=4)
        pygame.draw.rect(surf, body_dark, (tail.x + 8, tail.y + 3, tail.w - 12, tail.h - 6), border_radius=4)

        fin = [
            (int(w * 0.06), int(h * 0.56)),
            (int(w * 0.12), int(h * 0.36)),
            (int(w * 0.16), int(h * 0.58)),
        ]
        pygame.draw.polygon(surf, panel, fin)

        skid_col = (40, 40, 40)
        pygame.draw.rect(surf, skid_col, (int(w * 0.24), int(h * 0.76), int(w * 0.44), 6), border_radius=3)
        pygame.draw.rect(surf, skid_col, (int(w * 0.20), int(h * 0.70), 6, int(h * 0.12)))
        pygame.draw.rect(surf, skid_col, (int(w * 0.62), int(h * 0.70), 6, int(h * 0.12)))

        pod = pygame.Rect(int(w * 0.34), int(h * 0.70), int(w * 0.16), int(h * 0.10))
        pygame.draw.rect(surf, (80, 60, 60), pod, border_radius=6)
        for i in range(3):
            pygame.draw.circle(surf, (140, 55, 55), (pod.x + 10 + i * 12, pod.centery), 4)

        mast = pygame.Rect(int(w * 0.40), int(h * 0.30), int(w * 0.06), int(h * 0.16))
        pygame.draw.rect(surf, metal, mast, border_radius=3)

        cx, cy = int(w * 0.43), int(h * 0.28)
        if self.crashing:
            pygame.draw.circle(surf, (0, 0, 0, 50), (cx, cy), int(w * 0.20))
            pygame.draw.circle(surf, metal, (cx, cy), 10)
        else:
            length = int(w * 0.30)
            angle = self.rotor_angle
            for i in range(3):
                a = angle + (i * math.pi / 3)
                x1 = cx + math.cos(a) * length
                y1 = cy + math.sin(a) * length
                x2 = cx - math.cos(a) * length
                y2 = cy - math.sin(a) * length
                pygame.draw.line(surf, metal, (x1, y1), (x2, y2), 6)
            pygame.draw.circle(surf, (70, 70, 70), (cx, cy), 10)

        tr_x, tr_y = int(w * 0.02), int(h * 0.61)
        pygame.draw.circle(surf, (30, 30, 30), (tr_x, tr_y), 10)
        pygame.draw.line(surf, (60, 60, 60), (tr_x - 8, tr_y), (tr_x + 8, tr_y), 3)
        pygame.draw.line(surf, (60, 60, 60), (tr_x, tr_y - 8), (tr_x, tr_y + 8), 3)

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):
        if self.crashing:
            self.vel_y += (GRAVITY * 1.4) * DT
            self.pos_y += self.vel_y * DT
            self.pos_x += self.crash_vx * DT
            self.crash_angle += self.crash_spin * DT

            self.rect.x = int(self.pos_x)
            self.rect.y = int(self.pos_y)

            hits = pygame.sprite.spritecollide(self, platforms, False)
            ground_hits = [p for p in hits if getattr(p.rect, 'height', 0) >= 160]
            if ground_hits and self.vel_y > 0:
                ground = min(ground_hits, key=lambda p: p.rect.top)
                self.rect.bottom = ground.rect.top
                self.pos_y = float(self.rect.y)
                self.crash_impact = True
                self.crash_impact_pos = (self.rect.centerx, self.rect.centery)

            self.rotor_angle += 0.12 * DT
            self.draw_helicopter()
            center = self.rect.center
            rotated = pygame.transform.rotate(self.base_image, self.crash_angle)
            self.image = rotated
            self.rect = self.image.get_rect(center=center)
            self.check_bounds()
            return

        self.facing = 1 if player.rect.centerx >= self.rect.centerx else -1

        # Up and down motion
        self.phase += 0.05 * DT
        self.rect.y = self.start_y + math.sin(self.phase) * 30
        self.pos_y = float(self.rect.y)

        # Follow player
        if self.rect.x < player.rect.x - 200:
            self.pos_x += 2 * DT
        elif self.rect.x > player.rect.x + 200:
            self.pos_x -= 2 * DT

        self.rect.x = int(self.pos_x)

        # Rotor Spin
        self.rotor_angle += 0.4 * DT
        self.draw_helicopter()

        self.image = self.base_image

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
    """Boss helicopter with varied attacks """
    
    def __init__(self, x, y):
        super().__init__(x, y, PURPLE, 5000, 'boss_heli', 10000, 100)
        sky_height = SCREEN_HEIGHT - 200
        base_height = max(120, int(sky_height * 0.75))
        base_width = max(200, int(base_height * 2.4))
        self.width = base_width
        self.height = base_height
        self.base_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image = self.base_image
        self.rect = self.image.get_rect()
        min_center_y = self.height // 2
        max_center_y = max(min_center_y, sky_height - (self.height // 2))
        clamped_y = max(min_center_y, min(int(y), max_center_y))
        self.rect.center = (x, clamped_y)
        self.pos_x = float(x)
        self.pos_y = float(clamped_y)
        self.start_y = clamped_y
        self.phase = 0
        self.attack_cooldown = 0
        self.state_timer = 0
        self.max_hp = 5000
        self.rotor_angle = 0
        
        # Track HP thresholds for health pack drops (75%, 50%, 25%)
        self.hp_thresholds = [0.75, 0.50, 0.25]
        self.dropped_at_threshold = [False, False, False]
        
        # Attack pattern tracking
        self.attack_pattern = 0
        self.burst_count = 0
        self.sweep_angle = 0
        self.carpet_bomb_count = 0
        
        self.draw_boss_helicopter()

        sky_height = SCREEN_HEIGHT - 200
        self.min_center_y = self.rect.height // 2
        self.max_center_y = max(self.min_center_y, sky_height - (self.rect.height // 2))
        self.rect.centery = max(self.min_center_y, min(self.rect.centery, self.max_center_y))
        self.pos_y = float(self.rect.centery)
        self.start_y = self.rect.centery
    
    def _trim_to_alpha(self):
        bbox = self.base_image.get_bounding_rect()
        if bbox.width <= 0 or bbox.height <= 0:
            return
        center = self.rect.center
        self.image = self.base_image.subsurface(bbox).copy()
        self.rect = self.image.get_rect(center=center)

    def draw_boss_helicopter(self):
        """Draw a massive military helicopter."""
        self.base_image.fill((0, 0, 0, 0))

        w = self.width
        h = self.height
        body_color = (70, 85, 75)
        shade_color = (45, 55, 50)
        panel_color = (95, 110, 100)
        dark = (20, 20, 20)

        surf = self.base_image

        fuselage = pygame.Rect(int(w * 0.12), int(h * 0.35), int(w * 0.75), int(h * 0.28))
        pygame.draw.ellipse(surf, body_color, fuselage)

        nose = [
            (int(w * 0.82), int(h * 0.38)),
            (int(w * 0.95), int(h * 0.47)),
            (int(w * 0.82), int(h * 0.60)),
        ]
        pygame.draw.polygon(surf, body_color, nose)

        pygame.draw.ellipse(
            surf,
            shade_color,
            pygame.Rect(int(w * 0.18), int(h * 0.40), int(w * 0.58), int(h * 0.18))
        )

        wing = [
            (int(w * 0.36), int(h * 0.47)),
            (int(w * 0.18), int(h * 0.24)),
            (int(w * 0.52), int(h * 0.40)),
            (int(w * 0.62), int(h * 0.47)),
        ]
        pygame.draw.polygon(surf, panel_color, wing)
        pygame.draw.polygon(surf, shade_color, [(p[0], p[1] + int(h * 0.03)) for p in wing])

        wing2 = [
            (int(w * 0.36), int(h * 0.53)),
            (int(w * 0.18), int(h * 0.76)),
            (int(w * 0.52), int(h * 0.60)),
            (int(w * 0.62), int(h * 0.53)),
        ]
        pygame.draw.polygon(surf, panel_color, wing2)
        pygame.draw.polygon(surf, shade_color, [(p[0], p[1] - int(h * 0.03)) for p in wing2])

        tail = pygame.Rect(int(w * 0.06), int(h * 0.42), int(w * 0.18), int(h * 0.14))
        pygame.draw.rect(surf, body_color, tail)

        v_fin = [
            (int(w * 0.08), int(h * 0.42)),
            (int(w * 0.14), int(h * 0.24)),
            (int(w * 0.18), int(h * 0.42)),
        ]
        pygame.draw.polygon(surf, panel_color, v_fin)

        h_tail_top = [
            (int(w * 0.10), int(h * 0.44)),
            (int(w * 0.00), int(h * 0.34)),
            (int(w * 0.16), int(h * 0.40)),
        ]
        pygame.draw.polygon(surf, panel_color, h_tail_top)

        h_tail_bottom = [
            (int(w * 0.10), int(h * 0.54)),
            (int(w * 0.00), int(h * 0.66)),
            (int(w * 0.16), int(h * 0.60)),
        ]
        pygame.draw.polygon(surf, panel_color, h_tail_bottom)

        cockpit = [
            (int(w * 0.70), int(h * 0.37)),
            (int(w * 0.82), int(h * 0.40)),
            (int(w * 0.84), int(h * 0.48)),
            (int(w * 0.72), int(h * 0.48)),
        ]
        pygame.draw.polygon(surf, (120, 135, 125), cockpit)
        pygame.draw.polygon(surf, (150, 200, 220), [
            (int(w * 0.73), int(h * 0.39)),
            (int(w * 0.81), int(h * 0.41)),
            (int(w * 0.82), int(h * 0.46)),
            (int(w * 0.74), int(h * 0.46)),
        ])

        engine1 = pygame.Rect(int(w * 0.44), int(h * 0.54), int(w * 0.09), int(h * 0.10))
        engine2 = pygame.Rect(int(w * 0.44), int(h * 0.36), int(w * 0.09), int(h * 0.10))
        pygame.draw.ellipse(surf, shade_color, engine1)
        pygame.draw.ellipse(surf, shade_color, engine2)
        pygame.draw.circle(surf, dark, (engine1.right - int(w * 0.01), engine1.centery), int(h * 0.03))
        pygame.draw.circle(surf, dark, (engine2.right - int(w * 0.01), engine2.centery), int(h * 0.03))

        gun = pygame.Rect(int(w * 0.88), int(h * 0.52), int(w * 0.10), int(h * 0.02))
        pygame.draw.rect(surf, dark, gun)

        for i in range(6):
            x = int(w * (0.22 + i * 0.085))
            pygame.draw.line(surf, shade_color, (x, int(h * 0.40)), (x, int(h * 0.58)), 2)

        self._trim_to_alpha()
    
    def check_hp_threshold_drop(self, all_sprites, items_group):
        """Check if HP crossed a threshold and drop health pack."""
        current_hp_pct = self.hp / self.max_hp
        for i, threshold in enumerate(self.hp_thresholds):
            if current_hp_pct <= threshold and not self.dropped_at_threshold[i]:
                self.dropped_at_threshold[i] = True
                hp_pack = HealthPack(self.rect.centerx, self.rect.centery + 50)
                all_sprites.add(hp_pack)
                items_group.add(hp_pack)
    
    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None, items_group=None):
        self.phase += 0.03 * DT
        hover_offset = math.sin(self.phase) * 50
        
        self.state_timer += 1 * DT
        
        # Follow player horizontally
        target_x = player.rect.centerx 
        if self.pos_x < target_x - 100:
            self.pos_x += 3 * DT
        elif self.pos_x > target_x + 100:
            self.pos_x -= 3 * DT
            
        self.rect.centerx = int(self.pos_x)
        target_y = int(self.start_y + hover_offset)
        self.rect.centery = max(self.min_center_y, min(target_y, self.max_center_y))
        
        # Check HP threshold for health pack drops
        if items_group is not None:
            self.check_hp_threshold_drop(all_sprites, items_group)
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1 * DT
        else:
            # Varied attack patterns based on HP percentage
            hp_pct = self.hp / self.max_hp
            
            if hp_pct > 0.75:
                # Phase 1: Basic attacks
                attack_roll = random.choice(['mg_burst', 'missile', 'bomb'])
            elif hp_pct > 0.50:
                # Phase 2: More aggressive
                attack_roll = random.choice(['mg_sweep', 'missile_barrage', 'carpet_bomb', 'mg_burst'])
            elif hp_pct > 0.25:
                # Phase 3: Desperate attacks
                attack_roll = random.choice(['mg_sweep', 'missile_barrage', 'carpet_bomb', 'combo_attack'])
            else:
                # Phase 4: Rage mode - all attacks faster
                attack_roll = random.choice(['rage_mg', 'rage_missiles', 'carpet_bomb', 'combo_attack'])
            
            if attack_roll == 'mg_burst':
                # Standard burst fire
                for i in range(5):
                    spread = random.uniform(-0.2, 0.2)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx) + spread
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, damage=15, is_enemy=True, bullet_img=bullet_img)
                    bullets.add(b)
                    all_sprites.add(b)
                self.attack_cooldown = 60
                
            elif attack_roll == 'mg_sweep':
                # Sweeping machine gun fire
                for i in range(8):
                    angle = -0.5 + (i * 0.15)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    base_angle = math.atan2(dy, dx)
                    vx = math.cos(base_angle + angle)
                    vy = math.sin(base_angle + angle)
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, damage=12, is_enemy=True, bullet_img=bullet_img)
                    bullets.add(b)
                    all_sprites.add(b)
                self.attack_cooldown = 80
                
            elif attack_roll == 'missile':
                # Standard missile attack
                for i in range(3):
                    offset_x = (i - 1) * 40
                    m = Missile(self.rect.centerx + offset_x, self.rect.centery, player)
                    all_sprites.add(m)
                    missiles_group.add(m)
                self.attack_cooldown = 180
                
            elif attack_roll == 'missile_barrage':
                # Heavy missile barrage
                for i in range(5):
                    offset_x = (i - 2) * 30
                    m = Missile(self.rect.centerx + offset_x, self.rect.centery, player)
                    all_sprites.add(m)
                    missiles_group.add(m)
                self.attack_cooldown = 200
                
            elif attack_roll == 'bomb':
                # Single bomb drop
                g = Grenade(self.rect.centerx, self.rect.bottom, 0, is_enemy=True)
                all_sprites.add(g)
                grenades_group.add(g)
                self.attack_cooldown = 40
                
            elif attack_roll == 'carpet_bomb':
                # Carpet bombing - multiple bombs in a line
                for i in range(5):
                    offset_x = (i - 2) * 50
                    g = Grenade(self.rect.centerx + offset_x, self.rect.bottom, 0, is_enemy=True)
                    all_sprites.add(g)
                    grenades_group.add(g)
                self.attack_cooldown = 120
                
            elif attack_roll == 'combo_attack':
                # Combined attack: missiles + bullets
                for i in range(2):
                    offset_x = (i * 2 - 1) * 50
                    m = Missile(self.rect.centerx + offset_x, self.rect.centery, player)
                    all_sprites.add(m)
                    missiles_group.add(m)
                for i in range(4):
                    spread = random.uniform(-0.3, 0.3)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx) + spread
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, damage=15, is_enemy=True, bullet_img=bullet_img)
                    bullets.add(b)
                    all_sprites.add(b)
                self.attack_cooldown = 150
                
            elif attack_roll == 'rage_mg':
                # Rage mode: faster, more bullets
                for i in range(10):
                    spread = random.uniform(-0.4, 0.4)
                    dx = player.rect.centerx - self.rect.centerx
                    dy = player.rect.centery - self.rect.centery
                    angle = math.atan2(dy, dx) + spread
                    vx = math.cos(angle)
                    vy = math.sin(angle)
                    b = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, damage=18, is_enemy=True, bullet_img=bullet_img)
                    bullets.add(b)
                    all_sprites.add(b)
                self.attack_cooldown = 40
                
            elif attack_roll == 'rage_missiles':
                # Rage mode: more missiles, faster cooldown
                for i in range(4):
                    offset_x = (i - 1.5) * 35
                    m = Missile(self.rect.centerx + offset_x, self.rect.centery, player)
                    all_sprites.add(m)
                    missiles_group.add(m)
                self.attack_cooldown = 100
