from .BaseEnemy import BaseEnemy
from .Player import Player

class MeleeEnemy(BaseEnemy):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, "TODO: ASSETS", (255, 0, 0))
    
    def update(self, player: Player) -> None:
        self.patrol()
        if self.hostile and self.rect.colliderect(player.rect):
            player.take_damage(self.rect)
