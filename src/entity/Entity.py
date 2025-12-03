import pygame
from ..AssetManager import AssetManager

class Entity(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, image_path, color):
        super().__init__()
        self.image = AssetManager.load_sprite(image_path, width, height, color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = width
        self.height = height
        self.vel_x = 0
        self.vel_y = 0
        self.direction = 1

    def update(self):
        pass