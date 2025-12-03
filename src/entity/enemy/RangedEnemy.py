from .BaseEnemy import BaseEnemy
from ..Projectile import Projectile

class RangedEnemy(BaseEnemy):
    def __init__(self, x, y, all_sprites, projectiles_group):
        super().__init__(x, y, "TODO: ASSETS", (0, 255, 0))
        self.shoot_delay = 120 # Frames
        self.timer = 0
        self.all_sprites = all_sprites
        self.projectiles_group = projectiles_group

    def update(self, player):
        self.patrol()
        if not self.hostile: return

        self.timer += 1
        if self.timer >= self.shoot_delay:
            self.shoot()
            self.timer = 0

    def shoot(self):
        bullet = Projectile(self.rect.centerx, self.rect.centery, self.direction, 'enemy')
        self.all_sprites.add(bullet)
        self.projectiles_group.add(bullet)