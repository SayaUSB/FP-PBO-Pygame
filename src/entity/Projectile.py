import json
from .Entity import Entity

def load_config():
    filename = "config/config.json"
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

CONFIG = load_config() 

class Projectile(Entity):
    def __init__(self, x, y, direction, owner_type):
        super().__init__(x, y, 10, 10, "--TODO--", (255, 255, 0))
        self.speed = 10
        self.direction = direction
        self.owner_type = owner_type # 'player' or 'enemy'

    def update(self):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > CONFIG.get("SCREEN_WIDTH"):
            self.kill()