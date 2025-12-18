# Metal Slug: Clone (Pygame)

Game side-scrolling shooter sederhana yang terinspirasi dari Metal Slug, dibuat dengan **Python + Pygame**. Project ini memakai pendekatan OOP (kelas `Game`, `Player`, `Enemy`, dll) dan memanfaatkan `pygame.sprite.Group` untuk manajemen objek, collision, update, dan render.

## Cara Menjalankan

### Requirements
- Python 3.x
- Pygame

Install Pygame manual:

```bash
pip install pygame
```

### Menjalankan game
Di root project:

```bash
python main.py
```

File entry point adalah `main.py` yang memanggil `Game().run()`.

## Kontrol

Kontrol utama diambil dari `src/player.py` dan UI hint di `game.py`:

- **Gerak**: `LEFT` / `RIGHT`
- **Lompat**: `SPACE` (hanya saat di ground)
- **Arah bidik**:
  - `UP` = tembak ke atas
  - `DOWN` (saat di udara) = tembak ke bawah / diagonal (jika sambil bergerak)
- **Tembak**: `F` (tahan untuk mode otomatis saat pakai Machine Gun / Rocket Launcher)
- **Lempar granat**: `G`
- **Shield**: tahan `C` (menghabiskan shield)

Menu & pause:
- **Start**: `ENTER` (di menu)
- **Quit**: `ESC` (di menu)
- **Pause/Resume**: `ESC` atau `P` (saat bermain)
- **Restart**: `R` (saat pause)
- **Kembali ke menu**: `M` (saat pause)

## Gambaran Gameplay

- **Side-scrolling**: kamera mengikuti player ke kanan (`camera_x`), dan world dibuat bertahap dengan sistem *chunk generation*.
- **Platform & obstacle**: tanah + rintangan acak (crate/stone/sandbag/metal/barrel/spikes) dibuat di `Game.generate_chunk()`.
- **Enemy spawn**: musuh di-*spawn* bersamaan dengan obstacle setelah melewati area grace (`enemy_grace_x`).
- **Scoring**:
  - Tambah skor dari kill, hit, dan progres jarak.
  - Ada *penalty* skor saat peluru/granat meleset (`apply_miss_penalty`) dan saat terkena damage (`apply_damage_penalty`).
- **Boss fight**:
  - Boss `BossHelicopter` muncul ketika skor melewati threshold (`next_boss_score`).
  - Saat boss aktif, game bisa mengunci pergerakan kamera (`battle_lock`) agar arena lebih terkendali.
- **Airstrike event**:
  - Pada jarak tertentu, game memicu airstrike yang menjatuhkan granat musuh dari atas (state `warning` -> `active`).
- **Loot / pickup**:
  - `HealthPack`: menambah HP.
  - `MachineGunPickup`: memberi senjata `hmg` + ammo.
  - `RocketLauncherPickup`: memberi senjata `rocket` + ammo.

## Struktur Folder & Tanggung Jawab File

- **`main.py`**
  - Entry point program.
  - Membuat instance `Game` dan menjalankan `Game.run()`.

- **`game.py`**
  - Orkestrator utama.
  - Mengurus:
    - Inisialisasi Pygame + audio
    - State game (`menu`, `playing`, `paused`, `game_over`)
    - Game loop (`run()`): `handle_input()` -> `update()` -> `draw()`
    - World generation (`generate_chunk`) + dekorasi (background, trees, birds)
    - Spawn enemy, boss, dan event airstrike
    - Collision & konsekuensi (damage, skor, pickup)
    - UI/HUD (HP, shield, cooldown granat, skor, info weapon)

- **`settings.py`**
  - Konstanta global:
    - Resolusi (`SCREEN_WIDTH`, `SCREEN_HEIGHT`), FPS, `DT`
    - Gravitasi (`GRAVITY`)
    - Palet warna

- **`platforms.py`**
  - `Platform`: tanah dan obstacle (termasuk variasi `kind` seperti crate/metal/stone/sandbag/barrel).
  - `ExplosiveBarrel`: barrel khusus yang dapat meledak (hp + flag `explode_now`).

- **`src/`**
  - **`src/player.py`**
    - Kelas `Player`: movement, aim pose, shooting, shield, melee auto, cooldown, dan animasi berbasis sprite sederhana.
    - Membuat projectile (`Bullet`, `Grenade`, `Rocket`) dan mengatur perilakunya.

  - **`src/enemies.py`**
    - `Enemy` base class.
    - Enemy umum: `Soldier`, `TurretSoldier`, `Paratrooper`, `Tank`, `Helicopter`.
    - Boss: `BossHelicopter` (HP besar, beberapa pola serangan berdasarkan persentase HP, serta drop `HealthPack` di ambang HP tertentu).

  - **`src/projectiles.py`**
    - `Bullet`: peluru player/enemy, termasuk mekanisme *miss penalty* untuk player.
    - `Grenade`: granat player/enemy dengan timer meledak.
    - `Missile`: misil homing untuk musuh (dipakai `Tank`).
    - `Rocket`: roket homing untuk player (mode Rocket Launcher).

  - **`src/items.py`**
    - Pickup item: `HealthPack`, `MachineGunPickup`, `RocketLauncherPickup`.

  - **`src/effects.py`**
    - Efek visual: `Explosion`, `MediumExplosion`, `SmallExplosion`, `MeleeEffect`.
    - Efek death anim: `SoldierDeath`, `PlayerDeath`.

- **`assets/`**
  - `assets/sfx/`: file audio (bgm + sfx). `game.py` memetakan nama SFX ke path.
  - `assets/beras.png`: dipakai sebagai gambar peluru tertentu (mis. projectile dari heli).

- **`highscore.txt`**
  - Penyimpanan high score sederhana (dibaca/tulis oleh `Game.load_high_score()` / `Game.save_high_score()`).

## Alur Program (High Level)

1. **Start**: `main.py` -> `Game()`
2. **Init**: Pygame, audio, font, load high score, `new_game()`, masuk state `menu`.
3. **Loop** (`Game.run()`):
   - `handle_input()` mengelola event (quit, menu start, pause/resume, dll)
   - `update()`:
     - update player, enemy, projectile, effect
     - collision (bullet vs enemy, enemy bullet vs player, grenade explode, pickup)
     - spawn chunk baru saat mendekati batas world
     - boss spawn & airstrike state machine
   - `draw()`:
     - gambar background, sprites (offset oleh `camera_x`), HUD, dan overlay (menu/pause/game over)

## Catatan Teknis

- Game ini memakai `DT = 60 / FPS` untuk membuat pergerakan/cooldown relatif konsisten meski FPS berbeda.
- Banyak sprite digambar secara *procedural* (menggunakan `pygame.draw.*`) bukan dari spritesheet.

## Lisensi

Lihat file `LICENSE`.
