import pygame
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(GREEN)
        pygame.draw.rect(self.image, (80, 80, 80), (0,0,w,h), 2)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
