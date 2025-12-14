import pygame
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
