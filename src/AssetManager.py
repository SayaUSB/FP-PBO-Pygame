import os
import pygame

class AssetManager:
    @staticmethod
    def load_sprite(path, width, height, color_fallback):
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(img, (width, height))
            except pygame.error:
                print(f"Error loading {path}, using fallback.")
        surf = pygame.Surface((width, height))
        surf.fill(color_fallback)
        return surf
