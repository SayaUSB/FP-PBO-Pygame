import pygame

class AttackHitbox(pygame.sprite.Sprite):
    def __init__(self, player):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 255, 0)) 
        self.rect = self.image.get_rect()
        self.player = player

        if self.player.direction == 1: 
            self.rect.left = self.player.rect.right
        else: 
            self.rect.right = self.player.rect.left
        
        self.rect.centery = self.player.rect.centery
        self.lifetime = 10 

    def update(self):
        if self.player.direction == 1:
            self.rect.left = self.player.rect.right
        else:
            self.rect.right = self.player.rect.left
        self.rect.centery = self.player.rect.centery

        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()