import pygame, random, math, os, sys
from settings import *
from src import *
from platforms import Platform
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Metal Slug: Clone")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.SysFont("Arial", 18)
        self.big_font = pygame.font.SysFont("Arial", 40, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 60, bold=True)
        bomb_filename = 'assets/beras.png' 
        if os.path.exists(bomb_filename):
            try:
                raw_image = pygame.image.load(bomb_filename).convert_alpha()
                self.heli_bullet_img = pygame.transform.scale(raw_image, (50, 50))
            except Exception as e:
                self.heli_bullet_img = None
        else:
            self.heli_bullet_img = None

        self.highscore = self.load_high_score()
        self.new_game()
        self.game_state = "menu"
        self.trees = []
        self.next_tree_x = 0

        self.bg_seed = random.randint(0, 2**31 - 1)
        self.bg_layers = {}
        self.birds = []
        self.bird_spawn_timer = 0
        self._build_background_layers()

    def _build_background_layers(self):
        rng = random.Random(self.bg_seed)

        mw = max(SCREEN_WIDTH * 2, 2400)
        mh = SCREEN_HEIGHT
        mountain = pygame.Surface((mw, mh), pygame.SRCALPHA)
        mountain.fill((0, 0, 0, 0))

        horizon_y = int(SCREEN_HEIGHT * 0.64)
        base_y = int(SCREEN_HEIGHT * 0.88)
        step = 40
        phase1 = rng.random() * math.tau
        phase2 = rng.random() * math.tau
        phase3 = rng.random() * math.tau
        ridge = []
        x = 0
        while x <= mw:
            t = (x / mw) * math.tau
            peak_h = (
                220
                + 150 * (0.5 + 0.5 * math.sin(t * 1 + phase1))
                + 90 * (0.5 + 0.5 * math.sin(t * 2 + phase2))
                + 55 * (0.5 + 0.5 * math.sin(t * 3 + phase3))
            )
            y = horizon_y - int(peak_h)
            ridge.append((x, y))
            x += step

        col1 = (90, 110, 150)
        col2 = (65, 85, 120)
        snow = (235, 245, 255)
        snow_shadow = (190, 210, 230)

        poly = ridge + [(mw, base_y), (0, base_y)]
        pygame.draw.polygon(mountain, col1, poly)
        shadow_ridge = [(x, min(base_y, y + 26)) for (x, y) in ridge]
        pygame.draw.polygon(mountain, col2, shadow_ridge + [(mw, base_y), (0, base_y)])

        for i in range(2, len(ridge) - 2):
            x0, y0 = ridge[i]
            if y0 < ridge[i - 1][1] - 10 and y0 < ridge[i + 1][1] - 10:
                cap_w = 90 + int(40 * (0.5 + 0.5 * math.sin((x0 / mw) * math.tau * 2 + phase2)))
                cap_h = 26
                top = (x0, y0)
                cap = [
                    (top[0], top[1] + cap_h),
                    (top[0] - int(cap_w * 0.38), top[1] + int(cap_h * 1.55)),
                    (top[0], top[1]),
                    (top[0] + int(cap_w * 0.34), top[1] + int(cap_h * 1.45)),
                ]
                pygame.draw.polygon(mountain, snow, cap)
                pygame.draw.polygon(mountain, snow_shadow, [(cap[2][0], cap[2][1]), (cap[3][0], cap[3][1]), (cap[0][0], cap[0][1] + 3)])

        pygame.draw.rect(mountain, (70, 95, 120, 80), (0, base_y, mw, SCREEN_HEIGHT - base_y))

        fw = max(SCREEN_WIDTH * 2, 2400)
        fh = SCREEN_HEIGHT
        forest = pygame.Surface((fw, fh), pygame.SRCALPHA)
        forest.fill((0, 0, 0, 0))

        ridge_y = int(SCREEN_HEIGHT * 0.78)
        step = 32
        fphase1 = rng.random() * math.tau
        fphase2 = rng.random() * math.tau
        ridge = []
        rx = 0
        while rx <= fw:
            t = (rx / fw) * math.tau
            dy = (
                10 * math.sin(t * 1 + fphase1)
                + 7 * math.sin(t * 2 + fphase2)
                + 4 * math.sin(t * 3 + (fphase1 * 0.5))
            )
            ridge.append((rx, ridge_y + int(dy)))
            rx += step
        ridge_poly = ridge + [(fw, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
        pygame.draw.polygon(forest, (25, 70, 45, 200), ridge_poly)

        edge_pad = 160
        for _ in range(140):
            tx = rng.randrange(0, fw)
            ty = ridge_y + rng.randint(-10, 70)
            size = rng.uniform(0.55, 1.25)
            th = int(80 * size)
            tw = max(8, int(34 * size))

            for ox in (0,):
                pygame.draw.rect(forest, (35, 60, 35, 220), (tx + ox - tw // 6, ty, max(2, tw // 3), th), border_radius=2)
                pygame.draw.polygon(forest, (20, 90, 40, 230), [(tx + ox, ty - int(40 * size)), (tx + ox - tw, ty + int(10 * size)), (tx + ox + tw, ty + int(10 * size))])
                pygame.draw.polygon(forest, (18, 75, 35, 230), [(tx + ox, ty - int(20 * size)), (tx + ox - int(tw * 0.86), ty + int(28 * size)), (tx + ox + int(tw * 0.86), ty + int(28 * size))])

            if tx < edge_pad:
                ox = fw
                pygame.draw.rect(forest, (35, 60, 35, 220), (tx + ox - tw // 6, ty, max(2, tw // 3), th), border_radius=2)
                pygame.draw.polygon(forest, (20, 90, 40, 230), [(tx + ox, ty - int(40 * size)), (tx + ox - tw, ty + int(10 * size)), (tx + ox + tw, ty + int(10 * size))])
                pygame.draw.polygon(forest, (18, 75, 35, 230), [(tx + ox, ty - int(20 * size)), (tx + ox - int(tw * 0.86), ty + int(28 * size)), (tx + ox + int(tw * 0.86), ty + int(28 * size))])
            elif tx > fw - edge_pad:
                ox = -fw
                pygame.draw.rect(forest, (35, 60, 35, 220), (tx + ox - tw // 6, ty, max(2, tw // 3), th), border_radius=2)
                pygame.draw.polygon(forest, (20, 90, 40, 230), [(tx + ox, ty - int(40 * size)), (tx + ox - tw, ty + int(10 * size)), (tx + ox + tw, ty + int(10 * size))])
                pygame.draw.polygon(forest, (18, 75, 35, 230), [(tx + ox, ty - int(20 * size)), (tx + ox - int(tw * 0.86), ty + int(28 * size)), (tx + ox + int(tw * 0.86), ty + int(28 * size))])

        self.bg_layers = {
            "mountain": {"surf": mountain, "parallax": 0.25, "y": 0},
            "forest": {"surf": forest, "parallax": 0.45, "y": 0},
        }

    def spawn_bird(self):
        rng = random.Random((self.bg_seed + int(self.camera_x) * 31 + len(self.birds) * 17) & 0xFFFFFFFF)
        y = rng.randint(80, int(SCREEN_HEIGHT * 0.35))
        speed = rng.uniform(4.0, 8.0)
        size = rng.uniform(0.8, 1.6)
        self.birds.append({"x": float(self.camera_x + SCREEN_WIDTH + rng.randint(80, 240)), "y": float(y), "vx": -speed, "phase": rng.random() * 6.28, "size": size})

    def draw_bird(self, sx, y, phase, size=1.0):
        col = (30, 30, 30)
        w = int(22 * size)
        h = int(10 * size)
        flap = math.sin(phase) * (4 * size)
        p1 = (sx - w, int(y + flap))
        p2 = (sx, int(y - flap))
        p3 = (sx + w, int(y + flap))
        pygame.draw.lines(self.screen, col, False, [p1, p2, p3], 2)

    def draw_scenery(self):
        for layer in ("mountain", "forest"):
            info = self.bg_layers.get(layer)
            if not info:
                continue
            surf = info["surf"]
            par = info["parallax"]
            y = info["y"]
            w = surf.get_width()
            ox = int(self.camera_x * par) % w
            self.screen.blit(surf, (-ox, y))
            self.screen.blit(surf, (-ox + w, y))

        for b in self.birds:
            sx = int(b["x"] - self.camera_x)
            if -200 <= sx <= SCREEN_WIDTH + 200:
                self.draw_bird(sx, b["y"], b["phase"], b["size"])

    def spawn_tree_near_player(self):
        spacing = random.randint(220, 360)
        self.next_tree_x += spacing

        ground_y = SCREEN_HEIGHT - 200

        tree = {
            "x": self.next_tree_x,
            "y": ground_y,
            "size": random.uniform(0.8, 1.25)
        }
        self.trees.append(tree)

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
        self.next_boss_score = 5*10**4
        
        self.score = 0
        self.game_state = "playing"
        self.battle_lock = False
        self.hmg_pickup_msg_timer = 0
        self.rl_pickup_msg_timer = 0

        self.boss_cooldown = 0 
        
        self.max_distance = 100.0 
        self.distance_accumulator = 0.0

        self.all_sprites   = pygame.sprite.Group()
        self.platforms     = pygame.sprite.Group()
        self.bullets       = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.missiles      = pygame.sprite.Group()
        self.rockets       = pygame.sprite.Group()
        self.enemies       = pygame.sprite.Group()
        self.boss_group    = pygame.sprite.Group() 
        self.grenades      = pygame.sprite.Group()
        self.enemy_grenades= pygame.sprite.Group() 
        self.items         = pygame.sprite.Group()
        self.effects       = pygame.sprite.Group() 

        self.player = Player(self) 
        self.all_sprites.add(self.player)
        self.player_death_spawned = False
        
        self.camera_x = 0
        self.world_limit = 0
        self.generate_chunk(0, 1000)

        self.trees = []
        self.next_tree_x = 0
        self.birds = []
        self.bird_spawn_timer = 60

    def apply_miss_penalty(self, amount):
        if self.game_state == "playing":
            self.score -= amount

    def apply_damage_penalty(self, amount):
        if self.game_state == "playing":
            self.score -= amount

    def add_score(self, amount):
        if self.game_state == "playing":
            self.score += int(amount) 

    def generate_chunk(self, start_x, width):
        if self.boss_fight_active:
            ground_y = SCREEN_HEIGHT - 200
            ground = Platform(start_x, ground_y, width, SCREEN_HEIGHT - ground_y)
            self.platforms.add(ground)
            self.all_sprites.add(ground)
            self.world_limit = start_x + width
            return

        ground_y = SCREEN_HEIGHT - 200
        ground = Platform(start_x, ground_y, width, SCREEN_HEIGHT - ground_y)
        self.platforms.add(ground)
        self.all_sprites.add(ground)

        num_obstacles = width // 300
        for i in range(num_obstacles):
            obs_w = random.randint(80, 180)
            obs_h = random.choice([40, 80, 110])
            obs_x = start_x + random.randint(100, width - 400) 
            obs_y = ground_y - obs_h

            kind_roll = random.random()
            if kind_roll < 0.22:
                kind = "crate"
            elif kind_roll < 0.42:
                kind = "stone"
            elif kind_roll < 0.58:
                kind = "sandbag"
            elif kind_roll < 0.72:
                kind = "metal"
            elif kind_roll < 0.87:
                kind = "barrel"
            else:
                kind = "spikes"

            p = Platform(obs_x, obs_y, obs_w, obs_h, kind=kind)
            self.platforms.add(p)
            self.all_sprites.add(p)

            roll = random.random()
            if roll < 0.25:
                e = Soldier(obs_x + obs_w//2, obs_y - 10)
                self.enemies.add(e)
                self.all_sprites.add(e)
            elif roll < 0.70:
                para_spawn_y = -random.randint(120, 360)
                para = Paratrooper(self, obs_x + obs_w//2, para_spawn_y)
                self.enemies.add(para)
                self.all_sprites.add(para)
            elif roll < 0.82:
                t = Tank(obs_x + 200, ground_y - 10)
                self.enemies.add(t)
                self.all_sprites.add(t)
            elif roll < 0.92:
                h = Helicopter(obs_x, 150)
                self.enemies.add(h)
                self.all_sprites.add(h)
        self.world_limit = start_x + width

    def spawn_loot(self, enemy):
        if enemy.type_name == 'boss_heli':
            for _ in range(3):
                offset = random.randint(-30, 30)
                roll = random.random()
                if roll < 0.34:
                    item = MachineGunPickup(enemy.rect.centerx + offset, enemy.rect.centery)
                elif roll < 0.68:
                    item = RocketLauncherPickup(enemy.rect.centerx + offset, enemy.rect.centery)
                else:
                    item = HealthPack(enemy.rect.centerx + offset, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)
        
        elif enemy.type_name in ('soldier', 'paratrooper'):
            if random.random() < 0.25:
                item = HealthPack(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)
        elif enemy.type_name in ['tank', 'heli']:
            if random.random() < 0.25:
                if random.random() < 0.55:
                    item = MachineGunPickup(enemy.rect.centerx, enemy.rect.centery)
                else:
                    item = RocketLauncherPickup(enemy.rect.centerx, enemy.rect.centery)
                self.items.add(item)
                self.all_sprites.add(item)

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
                self.add_score(e.hit_score) 
            if e.hp <= 0:
                if e.type_name in ('soldier', 'paratrooper'):
                    death = SoldierDeath(e.rect.centerx, e.rect.bottom - 15, facing=getattr(e, 'facing', 1))
                    self.all_sprites.add(death)
                    self.effects.add(death)
                if e.type_name == 'heli':
                    if hasattr(e, 'begin_crash') and not getattr(e, 'crashing', False):
                        e.begin_crash()
                    continue
                if e.type_name == 'tank':
                    expl = Explosion(e.rect.centerx, e.rect.centery)
                    self.all_sprites.add(expl)
                    self.effects.add(expl)
                self.spawn_loot(e)
                self.add_score(e.score_val)
                e.kill()
    
        for b in self.boss_group:
            dist = math.hypot(b.rect.centerx - grenade.rect.centerx, b.rect.centery - grenade.rect.centery)
            if dist < EXPLOSION_RADIUS:
                b.hp -= EXPLOSION_DAMAGE
                self.add_score(b.hit_score)
                if b.hp <= 0:
                    self.spawn_loot(b)
                    self.add_score(b.score_val)
                    b.kill()
                    self.boss_fight_active = False 
                    self.next_boss_score += 5*10**4
                    self.boss_cooldown = 10**6

        grenade.kill()

    def trigger_rocket_explosion(self, rocket):
        if getattr(rocket, 'did_explode', False):
            return
        rocket.did_explode = True

        expl = Explosion(rocket.rect.centerx, rocket.rect.centery)
        self.all_sprites.add(expl)
        self.effects.add(expl)
        EXPLOSION_RADIUS = 300
        EXPLOSION_DAMAGE = 120

        for e in self.enemies:
            dist = math.hypot(e.rect.centerx - rocket.rect.centerx, e.rect.centery - rocket.rect.centery)
            if dist < EXPLOSION_RADIUS:
                e.hp -= EXPLOSION_DAMAGE
                self.add_score(e.hit_score)
            if e.hp <= 0:
                if e.type_name in ('soldier', 'paratrooper'):
                    death = SoldierDeath(e.rect.centerx, e.rect.bottom - 15, facing=getattr(e, 'facing', 1))
                    self.all_sprites.add(death)
                    self.effects.add(death)
                if e.type_name == 'heli':
                    if hasattr(e, 'begin_crash') and not getattr(e, 'crashing', False):
                        e.begin_crash()
                    continue
                if e.type_name == 'tank':
                    expl = Explosion(e.rect.centerx, e.rect.centery)
                    self.all_sprites.add(expl)
                    self.effects.add(expl)
                self.spawn_loot(e)
                self.add_score(e.score_val)
                e.kill()

        for b in self.boss_group:
            dist = math.hypot(b.rect.centerx - rocket.rect.centerx, b.rect.centery - rocket.rect.centery)
            if dist < EXPLOSION_RADIUS:
                b.hp -= EXPLOSION_DAMAGE
                self.add_score(b.hit_score)
                if b.hp <= 0:
                    self.spawn_loot(b)
                    self.add_score(b.score_val)
                    b.kill()
                    self.boss_fight_active = False
                    self.next_boss_score += 10**5
                    self.boss_cooldown = 10**6

        rocket.kill()

    def update(self):
        if self.game_state in ("menu", "paused"):
            return

        if self.game_state == "game_over":
            self.effects.update()
            return
        
        current_x = self.player.rect.centerx
        
        if current_x > self.max_distance:
            diff = current_x - self.max_distance
            self.distance_accumulator += diff
            
            if self.distance_accumulator >= 20.0:
                points = int(self.distance_accumulator / 20.0)
                self.score += points
                self.distance_accumulator -= (points * 20.0)
            
            self.max_distance = float(current_x)
        
        # boss spawn logic
        if self.score >= self.next_boss_score and not self.boss_fight_active and self.boss_cooldown <= 0:
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

        # update semua objek
        self.player.get_input(self.all_sprites, self.bullets, self.grenades, self.battle_lock, self.camera_x)
        self.player.update(self.platforms)
        self.player.check_auto_melee(self.enemies, self.all_sprites, self.effects, self.spawn_loot, self.add_score)
        self.player.check_auto_melee(self.boss_group, self.all_sprites, self.effects, self.spawn_loot, self.add_score)
        
        self.bullets.update()
        self.grenades.update()
        self.enemy_grenades.update() 
        self.enemy_bullets.update()
        self.missiles.update() 
        for m in list(self.missiles):
            if getattr(m, 'explode_now', False):
                expl = MediumExplosion(m.rect.centerx, m.rect.centery)
                self.all_sprites.add(expl)
                self.effects.add(expl)
                m.kill()
        self.rockets.update(self.platforms)
        for r in list(self.rockets):
            if getattr(r, 'explode_now', False):
                self.trigger_rocket_explosion(r)
        self.items.update(self.platforms)
        self.effects.update()

        spawn_limit = self.player.pos_x + SCREEN_WIDTH * 1.5

        while self.next_tree_x < spawn_limit:
            self.spawn_tree_near_player()

        if self.bird_spawn_timer > 0:
            self.bird_spawn_timer -= 1 * DT
        else:
            if random.random() < 0.6:
                self.spawn_bird()
            self.bird_spawn_timer = random.randint(160, 320)

        for b in list(self.birds):
            b["x"] += b["vx"] * DT
            b["phase"] += 0.25 * DT
            if b["x"] < self.camera_x - 400:
                self.birds.remove(b)

        
        # grenade explosions
        for g in self.grenades:
            if g.explode_now:
                self.trigger_explosion(g)

        g_hits = pygame.sprite.groupcollide(self.enemies, self.grenades, False, False)
        for e, g_list in g_hits.items():
            for g in g_list: self.trigger_explosion(g) 
            
        g_boss_hits = pygame.sprite.groupcollide(self.boss_group, self.grenades, False, False)
        for b, g_list in g_boss_hits.items():
            for g in g_list: self.trigger_explosion(g)

        ground_hits = pygame.sprite.groupcollide(self.grenades, self.platforms, False, False)
        for g, plats in ground_hits.items():
            g.explode_now = True

        enemy_ground_hits = pygame.sprite.groupcollide(self.enemy_grenades, self.platforms, False, False)
        for g, plats in enemy_ground_hits.items():
            g.explode_now = True

        enemy_bullet_ground_hits = pygame.sprite.groupcollide(self.enemy_bullets, self.platforms, True, False)
        for b, plats in enemy_bullet_ground_hits.items():
            expl = SmallExplosion(b.rect.centerx, b.rect.centery)
            self.all_sprites.add(expl)
            self.effects.add(expl)

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

        # update musuh yang aktif di layar
        for e in self.enemies:
            if -SCREEN_WIDTH < e.rect.x - self.player.rect.x < SCREEN_WIDTH * 1.5:
                e.update(self.platforms, self.player, self.enemy_bullets, self.all_sprites, 
                        missiles_group=self.missiles, grenades_group=self.enemy_grenades, bullet_img=self.heli_bullet_img)

        for e in list(self.enemies):
            if getattr(e, 'type_name', None) == 'heli' and getattr(e, 'crashing', False) and getattr(e, 'crash_impact', False):
                impact_pos = getattr(e, 'crash_impact_pos', None) or (e.rect.centerx, e.rect.centery)
                expl = Explosion(impact_pos[0], impact_pos[1])
                self.all_sprites.add(expl)
                self.effects.add(expl)
                self.spawn_loot(e)
                self.add_score(e.score_val)
                e.kill()

        for b in self.boss_group:
            b.update(self.platforms, self.player, self.enemy_bullets, self.all_sprites, 
                    missiles_group=self.missiles, grenades_group=self.enemy_grenades)

        # collision: player bullets vs enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for e, b_list in hits.items():
            for b in b_list:
                e.hp -= b.damage
                self.add_score(e.hit_score) 
            
            if e.hp <= 0:
                if e.type_name in ('soldier', 'paratrooper'):
                    death = SoldierDeath(e.rect.centerx, e.rect.bottom - 15, facing=getattr(e, 'facing', 1))
                    self.all_sprites.add(death)
                    self.effects.add(death)
                if e.type_name == 'heli':
                    if hasattr(e, 'begin_crash') and not getattr(e, 'crashing', False):
                        e.begin_crash()
                    continue
                if e.type_name == 'tank':
                    expl = Explosion(e.rect.centerx, e.rect.centery)
                    self.all_sprites.add(expl)
                    self.effects.add(expl)
                self.spawn_loot(e)
                self.add_score(e.score_val)
                e.kill()

        rocket_hits = pygame.sprite.groupcollide(self.enemies, self.rockets, False, False)
        for e, r_list in rocket_hits.items():
            for r in r_list:
                self.trigger_rocket_explosion(r)
        
        # vs boss
        boss_hits = pygame.sprite.groupcollide(self.boss_group, self.bullets, False, True)
        for boss_enemy, bullet_list in boss_hits.items():
            for bullet in bullet_list:
                boss_enemy.hp -= bullet.damage
                self.add_score(boss_enemy.hit_score)
            
            if boss_enemy.hp <= 0:
                self.spawn_loot(boss_enemy)
                self.add_score(boss_enemy.score_val)
                boss_enemy.kill()                
                self.boss_fight_active = False
                self.next_boss_score += 10**5
                self.boss_cooldown = 10**6

        boss_rocket_hits = pygame.sprite.groupcollide(self.boss_group, self.rockets, False, False)
        for boss_enemy, rocket_list in boss_rocket_hits.items():
            for r in rocket_list:
                self.trigger_rocket_explosion(r)
        
        # missile vs bullet
        missile_hits = pygame.sprite.groupcollide(self.missiles, self.bullets, True, True)
        for m in missile_hits.keys():
            expl = MediumExplosion(m.rect.centerx, m.rect.centery)
            self.all_sprites.add(expl)
            self.effects.add(expl)

        # rockets vs platforms
        rocket_ground_hits = pygame.sprite.groupcollide(self.rockets, self.platforms, False, False)
        for r in rocket_ground_hits.keys():
            self.trigger_rocket_explosion(r)

        # player vs enemy bullet / missile
        player_hit_list = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in player_hit_list:
            expl = SmallExplosion(bullet.rect.centerx, bullet.rect.centery)
            self.all_sprites.add(expl)
            self.effects.add(expl)
            self.player.take_damage(bullet.damage)
            
        missile_hit_player = pygame.sprite.spritecollide(self.player, self.missiles, False)
        for m in missile_hit_player:
            expl = MediumExplosion(m.rect.centerx, m.rect.centery)
            self.all_sprites.add(expl)
            self.effects.add(expl)
            self.player.take_damage(m.damage)
            m.kill()

        # items
        item_hits = pygame.sprite.spritecollide(self.player, self.items, True)
        for item in item_hits:
            self.add_score(100)
            
            if item.type_name == 'heal':
                self.player.hp = min(self.player.max_hp, self.player.hp + 30)
            elif item.type_name == 'mg':
                self.player.weapon_type = "hmg"
                self.player.ammo += 100
                self.hmg_pickup_msg_timer = 60
            elif item.type_name == 'rl':
                self.player.weapon_type = "rocket"
                self.player.ammo += 18
                self.rl_pickup_msg_timer = 60

        # game over
        if self.player.hp <= 0:
            if not getattr(self, 'player_death_spawned', False):
                death = PlayerDeath(self.player.rect.centerx, self.player.rect.centery, facing=getattr(self.player, 'facing', 1))
                self.all_sprites.add(death)
                self.effects.add(death)
                self.player.kill()
                self.player_death_spawned = True
            self.game_state = "game_over"
            if self.score > self.highscore:
                self.highscore = self.score
                self.save_high_score()
        
        # timer
        if self.hmg_pickup_msg_timer > 0:
            self.hmg_pickup_msg_timer -= 1 * DT

        if self.rl_pickup_msg_timer > 0:
            self.rl_pickup_msg_timer -= 1 * DT
            
        if self.boss_cooldown > 0:
            self.boss_cooldown -= 1 * DT

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == "menu":
                    if event.key == pygame.K_RETURN:
                        self.new_game()
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.game_state == "paused":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.game_state = "playing"
                    if event.key == pygame.K_m:
                        self.game_state = "menu"
                    if event.key == pygame.K_r:
                        self.new_game()

                elif self.game_state == "playing":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.game_state = "paused"
                        continue

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
                    if event.key == pygame.K_m:
                        self.game_state = "menu"

    def draw_tree(self, x, y, size=1.0):
        """Draw a simple tree silhouette.

        x,y are screen-space coordinates for the tree base (touching the ground).
        """
        # Trunk
        trunk_h = int(55 * size)
        trunk_w = max(8, int(18 * size))
        trunk_rect = pygame.Rect(x - trunk_w // 2, y - trunk_h, trunk_w, trunk_h)
        pygame.draw.rect(self.screen, TREE_BROWN, trunk_rect, border_radius=max(1, int(3 * size)))

        # Small shadow on trunk for depth
        shadow_col = (max(0, TREE_BROWN[0] - 25), max(0, TREE_BROWN[1] - 25), max(0, TREE_BROWN[2] - 25))
        pygame.draw.rect(
            self.screen,
            shadow_col,
            pygame.Rect(trunk_rect.x + trunk_rect.w // 2, trunk_rect.y, trunk_rect.w // 2, trunk_rect.h),
            border_radius=max(1, int(3 * size)),
        )

        # Canopy (overlapping circles reads better than a triangle at distance)
        canopy_base_y = y - trunk_h
        r_main = int(28 * size)
        r_small = int(22 * size)

        canopy_col = TREE_GREEN
        canopy_dark = (max(0, canopy_col[0] - 25), max(0, canopy_col[1] - 25), max(0, canopy_col[2] - 25))
        canopy_light = (min(255, canopy_col[0] + 25), min(255, canopy_col[1] + 25), min(255, canopy_col[2] + 25))

        # Dark underlayer
        pygame.draw.circle(self.screen, canopy_dark, (x, canopy_base_y + int(10 * size)), r_main)
        pygame.draw.circle(self.screen, canopy_dark, (x - int(24 * size), canopy_base_y + int(14 * size)), r_small)
        pygame.draw.circle(self.screen, canopy_dark, (x + int(24 * size), canopy_base_y + int(14 * size)), r_small)

        # Main layer
        pygame.draw.circle(self.screen, canopy_col, (x, canopy_base_y), r_main)
        pygame.draw.circle(self.screen, canopy_col, (x - int(26 * size), canopy_base_y + int(8 * size)), r_small)
        pygame.draw.circle(self.screen, canopy_col, (x + int(26 * size), canopy_base_y + int(8 * size)), r_small)

        # Highlight blobs
        pygame.draw.circle(self.screen, canopy_light, (x - int(10 * size), canopy_base_y - int(10 * size)), int(10 * size))
        pygame.draw.circle(self.screen, canopy_light, (x + int(12 * size), canopy_base_y - int(6 * size)), int(8 * size))

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

    def draw_menu_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_BLACK)
        self.screen.blit(overlay, (0, 0))

        title_surf = self.title_font.render("METAL SLUG: CLONE", True, GOLD)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 160))
        self.screen.blit(title_surf, title_rect)

        hs_surf = self.font.render(f"Best Score: {self.highscore}", True, WHITE)
        hs_rect = hs_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 80))
        self.screen.blit(hs_surf, hs_rect)

        start_surf = self.big_font.render("Press [ENTER] to Start", True, WHITE)
        start_rect = start_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10))
        self.screen.blit(start_surf, start_rect)

        info_surf = self.font.render("Press [ESC] to Quit", True, GREY)
        info_rect = info_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 70))
        self.screen.blit(info_surf, info_rect)

    def draw_pause_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(SEMI_TRANSPARENT_BLACK)
        self.screen.blit(overlay, (0, 0))

        title_surf = self.title_font.render("PAUSED", True, WHITE)
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 110))
        self.screen.blit(title_surf, title_rect)

        resume_surf = self.big_font.render("[ESC]/[P] Resume", True, WHITE)
        resume_rect = resume_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10))
        self.screen.blit(resume_surf, resume_rect)

        restart_surf = self.big_font.render("[R] Restart", True, WHITE)
        restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60))
        self.screen.blit(restart_surf, restart_rect)

        menu_surf = self.font.render("[M] Main Menu", True, GREY)
        menu_rect = menu_surf.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 120))
        self.screen.blit(menu_surf, menu_rect)

    def draw(self):
        self.screen.fill(SKY_BLUE)

        self.draw_scenery()

        # Background decorations (world-space -> screen-space via camera_x)
        for t in self.trees:
            sx = int(t["x"] - self.camera_x)
            if -300 <= sx <= SCREEN_WIDTH + 300:
                self.draw_tree(sx, t["y"], t["size"])

        for s in self.all_sprites:
            off_x = s.rect.x - int(self.camera_x)
            if (off_x + s.rect.width > -50) and (off_x < SCREEN_WIDTH + 50):
                self.screen.blit(s.image, (off_x, s.rect.y))
                if isinstance(s, Player) and s.is_shielding:
                    pygame.draw.circle(self.screen, CYAN, (off_x + 15, s.rect.y + 25), 40, 2)
        
        if self.game_state in ("playing", "paused"):
            # HP bar
            hp_pct = max(0, self.player.hp / self.player.max_hp)
            hp_col = (0, 255, 0) if hp_pct > 0.5 else (255, 0, 0)

            pygame.draw.rect(self.screen, (50,0,0), (10, 10, 200, 20))
            pygame.draw.rect(self.screen, hp_col, (10, 10, 200 * hp_pct, 20))
            pygame.draw.rect(self.screen, WHITE, (10, 10, 200, 20), 2)

            # Shield bar
            shield_pct = max(0, self.player.shield / self.player.max_shield)
            shield_col = CYAN if self.player.shield > 0 else (50, 50, 50)

            pygame.draw.rect(self.screen, (0,50,50), (10, 35, 150, 10))
            pygame.draw.rect(self.screen, shield_col, (10, 35, 150 * shield_pct, 10))
            pygame.draw.rect(self.screen, WHITE, (10, 35, 150, 10), 1)

            # Grenade cooldown
            grenade_pct = 1.0 - (max(0, self.player.grenade_cd) / self.player.max_grenade_cd)
            grenade_col = ORANGE if grenade_pct >= 1.0 else (100, 50, 0)
            
            pygame.draw.rect(self.screen, (50, 25, 0), (10, 50, 100, 8))
            pygame.draw.rect(self.screen, grenade_col, (10, 50, 100 * grenade_pct, 8))
            pygame.draw.rect(self.screen, WHITE, (10, 50, 100, 8), 1)

            g_label = self.font.render("G", True, WHITE)
            self.screen.blit(g_label, (115, 45))

            # Score
            score_txt = self.font.render(f"SCORE: {self.score}", True, WHITE)
            self.screen.blit(score_txt, (SCREEN_WIDTH - 150, 10))
            
            # Weapon
            w_txt = "PISTOL"
            w_col = WHITE
            if self.player.weapon_type == "hmg":
                w_txt = f"MACHINE GUN ({self.player.ammo})"
                w_col = GOLD
            elif self.player.weapon_type == "rocket":
                w_txt = f"ROCKET LAUNCHER ({self.player.ammo})"
                w_col = (255, 0, 0)
            
            txt_weapon = self.font.render(w_txt, True, w_col)
            self.screen.blit(txt_weapon, (10, 70))
            
            txt_info = self.font.render("F: Shoot (Hold for MG/RL) | C: Shield | G: Grenade", True, GREY)
            self.screen.blit(txt_info, (220, 10))

            # Boss bar
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

            # pickup msg
            if self.hmg_pickup_msg_timer > 0:
                msg = self.big_font.render("HEAVY MACHINE GUN!", True, GOLD)
                self.screen.blit(msg, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))

            if self.rl_pickup_msg_timer > 0:
                msg = self.big_font.render("ROCKET LAUNCHER!", True, (120, 200, 240))
                self.screen.blit(msg, (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 50))

        if self.game_state == "game_over":
            self.draw_game_over_screen()

        if self.game_state == "menu":
            self.draw_menu_screen()

        if self.game_state == "paused":
            self.draw_pause_screen()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
