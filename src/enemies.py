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

        # Chains
        pygame.draw.rect(
            self.image,
            (40, 40, 40),
            (20, 90, 200, 36),
            border_radius=18
        )

        # Wheels
        for i in range(8):
            pygame.draw.circle(
                self.image,
                (90, 90, 90),
                (40 + i * 22, 108),
                12
            )

        # Upper body
        pygame.draw.rect(
            self.image,
            DARK_GREEN,
            (35, 50, 170, 50),
            border_radius=18
        )

        # Panel detail
        pygame.draw.rect(
            self.image,
            (60, 120, 60),
            (55, 60, 60, 30),
            border_radius=8
        )

        # Turret Base
        turret_base_center = (120, 50)
        pygame.draw.circle(
            self.image,
            (70, 130, 70),
            turret_base_center,
            26
        )

        # Turret
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        self.turret_angle = math.atan2(dy, dx)

        barrel_length = 80
        end_x = turret_base_center[0] + math.cos(self.turret_angle) * barrel_length
        end_y = turret_base_center[1] + math.sin(self.turret_angle) * barrel_length

        pygame.draw.line(
            self.image,
            (30, 30, 30),
            turret_base_center,
            (end_x, end_y),
            12
        )

        pygame.draw.circle(
            self.image,
            (20, 20, 20),
            (int(end_x), int(end_y)),
            6
        )

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

        # =====================
        # UKURAN LEBIH BESAR
        # =====================
        self.width = 200
        self.height = 100

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.rotor_angle = 0

    def draw_helicopter(self):
        self.image.fill((0, 0, 0, 0))

        # Main Body
        pygame.draw.ellipse(
            self.image,
            (120, 120, 120),
            (30, 45, 120, 40)
        )

        # Cockpit
        pygame.draw.ellipse(
            self.image,
            (190, 190, 210),
            (95, 48, 50, 32)
        )

        # Frame cockpit
        pygame.draw.ellipse(
            self.image,
            (90, 90, 90),
            (95, 48, 50, 32),
            2
        )

        # Tail boom
        pygame.draw.rect(
            self.image,
            (100, 100, 100),
            (145, 58, 55, 10)
        )

        # Main rotor
        cx, cy = 100, 30
        length = 90
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
            8
        )

        # Second rotor blade
        x3 = cx + math.cos(angle + math.pi / 2) * length
        y3 = cy + math.sin(angle + math.pi / 2) * length
        x4 = cx - math.cos(angle + math.pi / 2) * length
        y4 = cy - math.sin(angle + math.pi / 2) * length

        pygame.draw.line(
            self.image,
            (40, 40, 40),
            (x3, y3),
            (x4, y4),
            6
        )

        # Rotor hub
        pygame.draw.circle(self.image, (60, 60, 60), (cx, cy), 8)

        # Tail rotor
        pygame.draw.line(
            self.image,
            (50, 50, 50),
            (188, 63),
            (198, 63),
            5
        )

        pygame.draw.circle(self.image, (60, 60, 60), (193, 63), 4)

    def update(self, platforms, player, bullets, all_sprites, missiles_group, grenades_group, bullet_img=None):

        # Up and down motion
        self.phase += 0.05 * DT
        self.rect.y = self.start_y + math.sin(self.phase) * 30

        # Follow player
        if self.rect.x < player.rect.x - 200:
            self.pos_x += 2 * DT
        elif self.rect.x > player.rect.x + 200:
            self.pos_x -= 2 * DT

        self.rect.x = int(self.pos_x)

        # Rotor Spin
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
