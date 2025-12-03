import pygame

class DialogueManager:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 20)
        self.active = False
        self.current_node = None
        self.current_npc = None
        self.options_rects = []

    def start_dialogue(self, npc):
        self.active = True
        self.current_npc = npc
        self.current_node = npc.dialog_data['start'] # Start from the starting node

    def draw(self):
        if not self.active or not self.current_node: return

        # UI Dialog Rectangle
        panel_rect = pygame.Rect(50, 400, 700, 180)
        pygame.draw.rect(self.screen, (50, 50, 50), panel_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), panel_rect, 2)

        # UI NPC Text
        text = self.current_node['text']
        text_surf = self.font.render(text, True, (255, 255, 255))
        self.screen.blit(text_surf, (70, 420))

        # UI Dialog Option
        self.options_rects = []
        y_offset = 460
        for index, option in enumerate(self.current_node['options']):
            opt_text = f"{index + 1}. {option['text']}"
            opt_surf = self.font.render(opt_text, True, (255, 255, 0))
            rect = opt_surf.get_rect(topleft=(70, y_offset))
            self.screen.blit(opt_surf, rect)
            self.options_rects.append((rect, option))
            y_offset += 30

    def handle_input(self, event):
        if not self.active: return

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            for rect, option in self.options_rects:
                if rect.collidepoint(mouse_pos):
                    self.process_choice(option)

    def process_choice(self, option):
        """Dialog choice that can effect gameplay"""
        effect = option.get('effect')
        if effect == 'hostile':
            self.current_npc.turn_hostile()
            self.active = False # Dialog finished
            print("NPC Marah!") # TODO: Make NPC attack or just angry
        elif effect == 'give_item':
            print("Kamu mendapatkan Potion!") # TODO: Inventory implementation
            self.current_npc.kill() # TODO: NPC gives item and runaway (opsional)
            self.active = False
        elif effect == 'exit':
            self.active = False
        
        if 'next' in option and option['next']:
            # TODO: Extended dialog option
            pass 
