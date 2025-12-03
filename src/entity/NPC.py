from .Entity import Entity

class NPC(Entity):
    def __init__(self, x, y, dialog_data):
        super().__init__(x, y, 40, 60, "TODO: ASSETS", (255, 255, 255))
        self.dialog_data = dialog_data
        self.hostile = False 
    
    def turn_hostile(self):
        self.hostile = True
        self.image.fill((255, 0, 0))