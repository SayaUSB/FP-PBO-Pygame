import pygame
from ..Entity import Entity

class BaseEnemy(Entity):
    def __init__(self, x, y, img_path, color):
        super().__init__(x, y, 40, 40, img_path, color)
        self.speed = 2
        self.patrol_range = 100
        self.start_x = x
        self.hostile = True 
        self.hp = 3
        self.invulnerable = False
        self.invul_timer = 0

    def patrol(self):
        if not self.hostile: return 
        self.rect.x += self.speed * self.direction
        if abs(self.rect.x - self.start_x) > self.patrol_range:
            self.direction *= -1

    def take_damage(self):
        current_time = pygame.time.get_ticks()
        if self.invulnerable and current_time - self.invul_timer < 500:
            return

        self.hp -= 1
        self.invulnerable = True
        self.invul_timer = current_time
        self.image.fill((255, 255, 255)) 

        if self.hp <= 0:
            self.kill()