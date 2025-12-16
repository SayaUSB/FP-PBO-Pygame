import pygame
import random
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, kind=None):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        self.kind = kind
        self.damage = 0
        self.is_ground = h >= 160

        rng = random.Random((int(x) * 31 + int(y) * 17 + int(w) * 13 + int(h) * 7 + (hash(self.kind) if self.kind else 0)) & 0xFFFFFFFF)

        if self.is_ground:
            grass_h = max(18, min(60, int(h * 0.22)))

            soil_base = TREE_BROWN
            soil_dark = (90, 55, 25)
            grass_base = TREE_GREEN
            grass_dark = (25, 110, 25)

            self.image.fill(soil_base)
            pygame.draw.rect(self.image, grass_base, (0, 0, w, grass_h))
            pygame.draw.rect(self.image, grass_dark, (0, grass_h - 6, w, 6))

            for i in range(0, w, 12):
                blade_h = rng.randint(6, 16)
                bx = i + rng.randint(-2, 2)
                pygame.draw.line(self.image, grass_dark, (bx, grass_h - 6), (bx, grass_h - 6 - blade_h), 2)

            pebble_count = max(40, (w * h) // 9000)
            for _ in range(int(pebble_count)):
                px = rng.randrange(0, max(1, w))
                py = rng.randrange(grass_h, max(grass_h + 1, h))
                r = rng.randint(1, 3)
                c = rng.choice([soil_dark, (120, 80, 45), (140, 95, 55), (70, 45, 20)])
                pygame.draw.circle(self.image, c, (px, py), r)

            for _ in range(max(10, w // 120)):
                wx = rng.randrange(0, max(1, w))
                wy = rng.randrange(grass_h + 10, max(grass_h + 11, h - 10))
                ww = rng.randint(30, 90)
                pygame.draw.arc(self.image, soil_dark, (wx - ww // 2, wy, ww, 30), 0.0, 3.14, 2)

            pygame.draw.rect(self.image, (60, 40, 20), (0, 0, w, h), 3)
        else:
            if self.kind is None:
                self.kind = rng.choice(["crate", "stone", "metal", "sandbag", "barrel"])
            self._draw_obstacle(w, h, rng)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def _draw_obstacle(self, w, h, rng):
        if self.kind == "crate":
            base = (146, 93, 54)
            dark = (108, 68, 36)
            light = (176, 120, 70)
            self.image.fill(base)
            pygame.draw.rect(self.image, dark, (0, 0, w, h), 3)
            plank_count = max(2, min(6, w // 28))
            for i in range(1, plank_count):
                x = int(i * w / plank_count)
                pygame.draw.line(self.image, dark, (x, 2), (x, h - 3), 2)
                pygame.draw.line(self.image, light, (x + 2, 3), (x + 2, h - 4), 1)
            pygame.draw.line(self.image, light, (3, 3), (w - 4, 3), 2)
            pygame.draw.line(self.image, dark, (3, h - 4), (w - 4, h - 4), 2)
            pygame.draw.line(self.image, dark, (w // 2, 2), (w // 2, h - 3), 3)
            pygame.draw.line(self.image, dark, (2, h // 2), (w - 3, h // 2), 3)

        elif self.kind == "stone":
            base = (120, 125, 135)
            dark = (85, 90, 100)
            light = (165, 170, 180)
            self.image.fill(base)
            for _ in range(max(8, (w * h) // 1400)):
                px = rng.randrange(0, max(1, w))
                py = rng.randrange(0, max(1, h))
                r = rng.randint(2, 6)
                pygame.draw.circle(self.image, rng.choice([dark, light]), (px, py), r)
            for _ in range(max(2, w // 60)):
                x1 = rng.randrange(0, max(1, w))
                y1 = rng.randrange(0, max(1, h))
                x2 = max(0, min(w - 1, x1 + rng.randint(-40, 40)))
                y2 = max(0, min(h - 1, y1 + rng.randint(-20, 20)))
                pygame.draw.line(self.image, dark, (x1, y1), (x2, y2), 2)
            pygame.draw.rect(self.image, (60, 60, 70), (0, 0, w, h), 3)

        elif self.kind == "metal":
            base = (85, 100, 130)
            dark = (55, 65, 90)
            light = (135, 155, 190)
            self.image.fill(base)
            stripe_h = max(10, h // 5)
            for y in range(0, h, stripe_h):
                col = light if (y // stripe_h) % 2 == 0 else dark
                pygame.draw.rect(self.image, col, (0, y, w, min(stripe_h, h - y)), 0)
            pygame.draw.rect(self.image, (30, 30, 45), (0, 0, w, h), 3)
            rivet_r = 3
            for rx in (10, w - 10):
                for ry in (10, h - 10):
                    if 0 <= rx < w and 0 <= ry < h:
                        pygame.draw.circle(self.image, (210, 220, 235), (rx, ry), rivet_r)
                        pygame.draw.circle(self.image, (40, 40, 55), (rx + 1, ry + 1), rivet_r, 1)

        elif self.kind == "sandbag":
            base = (190, 170, 120)
            dark = (145, 125, 85)
            light = (220, 205, 150)
            self.image.fill(base)
            bag_h = max(14, min(26, h // 2))
            y = h - bag_h
            while y >= 0:
                pygame.draw.ellipse(self.image, dark, (2, y, w - 4, bag_h))
                pygame.draw.ellipse(self.image, base, (3, y + 1, w - 6, bag_h - 2))
                pygame.draw.ellipse(self.image, light, (6, y + 3, max(1, w - 16), max(1, bag_h - 8)))
                pygame.draw.line(self.image, dark, (6, y + bag_h // 2), (w - 7, y + bag_h // 2), 2)
                y -= int(bag_h * 0.65)
            pygame.draw.rect(self.image, dark, (0, 0, w, h), 3)

        elif self.kind == "barrel":
            base = (110, 125, 155)
            dark = (70, 85, 110)
            light = (170, 190, 220)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, base, (0, 0, w, h), border_radius=max(2, min(12, w // 4)))
            pygame.draw.rect(self.image, dark, (0, 0, w, h), 3, border_radius=max(2, min(12, w // 4)))
            band_h = max(6, h // 6)
            pygame.draw.rect(self.image, dark, (0, band_h, w, band_h))
            pygame.draw.rect(self.image, dark, (0, h - 2 * band_h, w, band_h))
            pygame.draw.rect(self.image, light, (w // 4, 6, max(2, w // 8), h - 12))
            bolt_r = 2
            for by in (band_h + band_h // 2, h - 2 * band_h + band_h // 2):
                for bx in (6, w - 7):
                    if 0 <= bx < w and 0 <= by < h:
                        pygame.draw.circle(self.image, (230, 230, 230), (bx, by), bolt_r)
                        pygame.draw.circle(self.image, (60, 60, 60), (bx + 1, by + 1), bolt_r, 1)

        else:
            self.image.fill(GREEN)
            pygame.draw.rect(self.image, (80, 80, 80), (0, 0, w, h), 2)

class ExplosiveBarrel(pygame.sprite.Sprite):
    def __init__(self, x, y_bottom):
        super().__init__()
        w, h = 44, 60
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        base = (205, 50, 50)
        dark = (135, 25, 25)
        light = (255, 120, 120)
        hazard = (255, 210, 60)

        pygame.draw.rect(self.image, base, (0, 0, w, h), border_radius=10)
        pygame.draw.rect(self.image, dark, (0, 0, w, h), 3, border_radius=10)
        band_h = 9
        pygame.draw.rect(self.image, dark, (0, band_h, w, band_h))
        pygame.draw.rect(self.image, dark, (0, h - 2 * band_h, w, band_h))
        pygame.draw.rect(self.image, light, (w // 4, 7, 5, h - 14))

        cx, cy = w // 2, h // 2
        pygame.draw.circle(self.image, hazard, (cx, cy), 10)
        pygame.draw.circle(self.image, dark, (cx, cy), 10, 2)
        pygame.draw.polygon(self.image, dark, [(cx - 3, cy - 6), (cx + 3, cy - 6), (cx, cy + 6)])

        self.rect = self.image.get_rect(midbottom=(int(x), int(y_bottom)))
        self.hp = 60
        self.explode_now = False
