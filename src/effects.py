import pygame
import random, math
from settings import *

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.radius = 10
        self.max_radius = 150
        self.growth_rate = 15
        self.pos_x = x
        self.pos_y = y
        self.image = pygame.Surface((self.max_radius*2, self.max_radius*2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.timer = 20

    def update(self):
        self.timer -= 1 * DT
        
        if self.radius < self.max_radius:
            self.radius += self.growth_rate * DT
        
        if self.timer < 10:
            self.alpha -= 25 * DT
            if self.alpha < 0: self.alpha = 0
            
        self.image.fill((0,0,0,0)) 
        
        pygame.draw.circle(self.image, (*ORANGE, int(self.alpha)), 
                        (self.max_radius, self.max_radius), int(self.radius))
        
        pygame.draw.circle(self.image, (*YELLOW, int(self.alpha)), 
                        (self.max_radius, self.max_radius), int(self.radius * 0.7))
        
        if self.timer <= 0:
            self.kill()

class MeleeEffect(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
        pygame.draw.arc(self.image, (255, 255, 255), (0,0,60,60), 0, 3.14, 5)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.timer = 15

    def update(self):
        self.timer -= 1 * DT
        if self.timer <= 0:
            self.kill()

class SoldierDeath(pygame.sprite.Sprite):
    def __init__(self, x, y, facing=1):
        super().__init__()
        self.base_w = 70
        self.base_h = 70
        self.image = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self.pos_x = float(x)
        self.pos_y = float(y)

        self.facing = 1 if facing >= 0 else -1
        self.vel_x = 0.8 * self.facing
        self.vel_y = -6
        self.angle = -20 * self.facing
        self.ang_vel = (-4.0 * self.facing) + random.uniform(-1.5, 1.5)
        self.alpha = 255
        self.timer = 32

        self.particles = []
        for _ in range(14):
            vx = random.uniform(-2.8, 2.8)
            vy = random.uniform(-5.0, -1.5)
            life = random.randint(10, 22)
            self.particles.append([0.0, 12.0, vx, vy, life])

    def _draw_body(self):
        surf = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)

        uniform = (70, 110, 70)
        uniform_dark = (45, 75, 45)
        helmet = (55, 70, 60)
        boots = (30, 30, 30)
        blood = (180, 30, 30)

        cx = self.base_w // 2
        cy = self.base_h // 2

        pygame.draw.circle(surf, helmet, (cx - 10, cy - 10), 10)
        pygame.draw.circle(surf, (20, 20, 20), (cx - 12, cy - 12), 10, 2)

        torso = pygame.Rect(cx - 8, cy - 5, 26, 18)
        pygame.draw.rect(surf, uniform, torso, border_radius=5)
        pygame.draw.rect(surf, uniform_dark, (torso.x, torso.y + torso.h // 2, torso.w, torso.h // 2), border_radius=5)

        pygame.draw.line(surf, uniform, (cx + 10, cy + 2), (cx + 26, cy + 12), 5)
        pygame.draw.line(surf, uniform, (cx + 10, cy + 2), (cx + 22, cy - 10), 5)

        pygame.draw.line(surf, uniform, (cx + 2, cy + 10), (cx + 12, cy + 26), 6)
        pygame.draw.line(surf, uniform, (cx + 12, cy + 10), (cx + 28, cy + 26), 6)
        pygame.draw.rect(surf, boots, (cx + 6, cy + 24, 14, 7), border_radius=2)
        pygame.draw.rect(surf, boots, (cx + 22, cy + 24, 14, 7), border_radius=2)

        pygame.draw.circle(surf, (*blood, 170), (cx - 6, cy + 16), 7)
        pygame.draw.circle(surf, (*blood, 150), (cx + 2, cy + 18), 5)

        return surf

    def update(self):
        self.timer -= 1 * DT
        if self.timer <= 0:
            self.kill()
            return

        self.vel_y += (GRAVITY * 1.2) * DT
        self.pos_x += self.vel_x * DT
        self.pos_y += self.vel_y * DT
        self.angle += self.ang_vel * DT

        if self.timer < 12:
            self.alpha -= 22 * DT
            if self.alpha < 0:
                self.alpha = 0

        for p in self.particles:
            p[4] -= 1 * DT
            p[2] *= 0.98
            p[3] += (GRAVITY * 0.9) * DT
            p[0] += p[2] * DT
            p[1] += p[3] * DT

        base = self._draw_body()
        rotated = pygame.transform.rotate(base, self.angle)
        rotated.set_alpha(int(self.alpha))
        self.image = pygame.Surface((self.base_w, self.base_h), pygame.SRCALPHA)

        r = rotated.get_rect(center=(self.base_w // 2, self.base_h // 2))
        self.image.blit(rotated, r)

        blood = (180, 30, 30)
        for p in self.particles:
            if p[4] > 0:
                px = int(self.base_w // 2 + p[0])
                py = int(self.base_h // 2 + p[1])
                a = max(0, min(180, int(180 * (p[4] / 22))))
                pygame.draw.circle(self.image, (*blood, a), (px, py), 2)

        self.rect = self.image.get_rect(center=(int(self.pos_x), int(self.pos_y)))
