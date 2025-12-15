import pygame
from settings import *
from .projectiles import Grenade 

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, color, type_name):
        super().__init__()
        self.image = pygame.Surface((25, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_y = -5
        self.type_name = type_name

    def update(self, platforms):
        self.vel_y += GRAVITY * DT
        self.pos_y += self.vel_y * DT
        self.rect.centery = int(self.pos_y)
        
        hits = pygame.sprite.spritecollide(self, platforms, False)
        for p in hits:
            if self.vel_y > 0:
                self.rect.bottom = p.rect.top
                self.vel_y = 0
                self.pos_y = float(self.rect.centery)

class HealthPack(Item):
    def __init__(self, x, y):
        super().__init__(x, y, PINK, 'heal')
        pygame.draw.rect(self.image, WHITE, (8, 4, 9, 17))
        pygame.draw.rect(self.image, WHITE, (4, 8, 17, 9))
        pygame.draw.rect(self.image, RED, (10, 6, 5, 13))
        pygame.draw.rect(self.image, RED, (6, 10, 13, 5))

class MachineGunPickup(Item):
    def __init__(self, x, y):
        super().__init__(x, y, GOLD, 'mg')
        font = pygame.font.SysFont("Arial", 20, bold=True)
        txt = font.render("M", True, BLACK)
        self.image.blit(txt, (5, 2))

class RocketLauncherPickup(Item):
    def __init__(self, x, y):
        super().__init__(x, y, (120, 170, 210), 'rl')
        body = (40, 60, 70)
        body_dark = (25, 35, 45)
        tip = (210, 60, 60)
        steel = (90, 95, 105)
        flame = (255, 170, 60)

        pygame.draw.rect(self.image, body, (5, 12, 15, 7), border_radius=3)
        pygame.draw.rect(self.image, body_dark, (7, 15, 11, 3), border_radius=2)
        pygame.draw.polygon(self.image, tip, [(20, 12), (24, 15), (20, 19)])
        pygame.draw.rect(self.image, steel, (6, 9, 6, 4), border_radius=2)
        pygame.draw.rect(self.image, (20, 20, 25), (10, 18, 7, 4), border_radius=2)
        pygame.draw.polygon(self.image, (*flame, 200), [(5, 15), (2, 13), (2, 17)])
