import pygame
import random
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        is_ground = h >= 160
        if is_ground:
            rng = random.Random((int(x) * 31 + int(y) * 17 + int(w) * 13 + int(h) * 7) & 0xFFFFFFFF)
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
            self.image.fill(GREEN)
            pygame.draw.rect(self.image, (80, 80, 80), (0, 0, w, h), 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
