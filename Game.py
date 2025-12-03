import sys
import json
import pygame
from src.Platform import Platform
from src.entity.NPC import NPC
from src.entity.Player import Player
from src.entity.enemy.MeleeEnemy import MeleeEnemy
from src.entity.enemy.RangedEnemy import RangedEnemy
from src.DialogueManager import DialogueManager

def load_config():
    filename = "config/config.json"
    with open(filename, 'r') as f:
        config = json.load(f)
    return config

CONFIG = load_config() 

def main():
    pygame.init()
    screen = pygame.display.set_mode((CONFIG.get("SCREEN_WIDTH"), CONFIG.get("SCREEN_HEIGHT")))
    pygame.display.set_caption("OOP Platformer RPG")
    clock = pygame.time.Clock()
    attack_group = pygame.sprite.Group()

    # Grup Sprite
    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    projectiles = pygame.sprite.Group()
    npcs = pygame.sprite.Group()

    # Setup Level
    ground = Platform(0, CONFIG.get("SCREEN_HEIGHT") - 40, CONFIG.get("SCREEN_WIDTH"), 40)
    plat1 = Platform(200, 450, 200, 20)
    plat2 = Platform(500, 350, 200, 20)
    platforms.add(ground, plat1, plat2)
    all_sprites.add(ground, plat1, plat2)

    # Setup Player
    player = Player(50, 450)
    all_sprites.add(player)

    # Setup Enemies
    enemy1 = MeleeEnemy(250, 410)
    enemy2 = RangedEnemy(550, 310, all_sprites, projectiles)
    enemies.add(enemy1, enemy2)
    all_sprites.add(enemy1, enemy2)

    # Setup NPC dengan Dialog Tree
    dialog_data_guard = {
        'start': {
            'text': "Berhenti! Siapa kamu? (Klik pilihan)",
            'options': [
                {'text': "Saya petualang.", 'next': None, 'effect': 'give_item'},
                {'text': "Saya musuhmu!", 'next': None, 'effect': 'hostile'},
                {'text': "Permisi...", 'next': None, 'effect': 'exit'}
            ]
        }
    }
    npc = NPC(600, 490, dialog_data_guard)
    npcs.add(npc)
    all_sprites.add(npc)

    dialog_manager = DialogueManager(screen)

    running = True
    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Jika dialog aktif, input keyboard player dimatikan, mouse aktif untuk dialog
            if dialog_manager.active:
                dialog_manager.handle_input(event)
            else:
                # Trigger Dialog jika dekat NPC dan tekan 'E'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_e:
                        hits = pygame.sprite.spritecollide(player, npcs, False)
                        if hits:
                            dialog_manager.start_dialogue(hits[0])

        # 2. Update Logic
        if not dialog_manager.active:
            player.update(platforms, all_sprites, attack_group)
            
            for enemy in enemies:
                # Cek tipe musuh
                if isinstance(enemy, RangedEnemy):
                    enemy.update(player)
                elif isinstance(enemy, MeleeEnemy):
                    enemy.update(player)
                
                # Jika NPC berubah jadi hostile, dia bisa dimasukkan ke logic musuh di sini
                # (Sederhananya di demo ini: NPC hostile hanya berubah warna)

                # --- LOGIKA KENA HIT (PLAYER -> MUSUH) ---
                # Cek apakah musuh ini bersentuhan dengan salah satu hitbox di attack_group
                if pygame.sprite.spritecollide(enemy, attack_group, False):
                    enemy.take_damage()
                    
                    # Balikin warna musuh jika invulnerable habis (Visual Feedback Sederhana)
                    if enemy.invulnerable and pygame.time.get_ticks() - enemy.invul_timer > 500:
                         enemy.invulnerable = False
                         # Kembalikan warna asli (Merah/Hijau)
                         if isinstance(enemy, MeleeEnemy): enemy.image.fill((255, 0, 0))
                         else: enemy.image.fill((0, 255, 0))
            attack_group.update()
            projectiles.update()

        # 3. Drawing
        screen.fill((0, 0, 0))
        all_sprites.draw(screen)
        dialog_manager.draw() # Gambar UI Dialog di atas segalanya

        pygame.display.flip()
        clock.tick(CONFIG.get("FPS"))

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()