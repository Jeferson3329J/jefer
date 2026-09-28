"""
Bomberman - 3 Niveles | Bandera de Colombia | Personajes diferentes
Ejecutar: python bomberman.py
"""

import pygame
import random
import sys
import math

# ==================== CONFIGURACIÓN ====================
TILE = 40
COLS = 15
ROWS = 13
WIDTH = COLS * TILE
HEIGHT = ROWS * TILE + 60
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (20, 20, 35)
NAVY = (25, 35, 55)

# Bandera de Colombia
YELLOW = (252, 209, 22)
BLUE = (0, 56, 147)
RED = (206, 17, 38)

SOLID_COLOR = (60, 60, 70)
SOLID_LIGHT = (90, 90, 100)

PLAYER_GREEN = (0, 200, 120)
PLAYER_LIGHT = (50, 255, 180)
PLAYER_HAT = (255, 220, 50)

ENEMY_TYPES = {
    1: {"color": (180, 50, 220), "name": "Morado", "speed": (350, 450)},
    2: {"color": (255, 100, 50),  "name": "Naranja", "speed": (250, 350)},
    3: {"color": (50, 200, 255),  "name": "Cyan", "speed": (180, 280)},
}

EMPTY = 0
SOLID = 1
SOFT = 2

# ==================== CLASES ====================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.lives = 3
        self.max_bombs = 1
        self.range = 1
        self.move_delay = 110
        self.last_move = 0

    def try_move(self, dx, dy, game_map, bombs):
        now = pygame.time.get_ticks()
        if now - self.last_move < self.move_delay:
            return
        nx, ny = self.x + dx, self.y + dy
        if 0 <= nx < COLS and 0 <= ny < ROWS:
            if game_map[ny][nx] == EMPTY:
                if not any(b.x == nx and b.y == ny for b in bombs):
                    self.x, self.y = nx, ny
                    self.last_move = now


class Enemy:
    def __init__(self, x, y, enemy_type=1):
        self.x = x
        self.y = y
        self.type = enemy_type
        self.dir = random.randint(0, 3)
        self.move_timer = 0
        speed_range = ENEMY_TYPES[enemy_type]["speed"]
        self.speed = random.randint(speed_range[0], speed_range[1])
        self.color = ENEMY_TYPES[enemy_type]["color"]

    def update(self, dt, game_map, bombs):
        self.move_timer += dt
        if self.move_timer < self.speed:
            return
        self.move_timer = 0

        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        dx, dy = dirs[self.dir]
        nx, ny = self.x + dx, self.y + dy

        def can_walk(x, y):
            if not (0 <= x < COLS and 0 <= y < ROWS):
                return False
            if game_map[y][x] != EMPTY:
                return False
            if any(b.x == x and b.y == y for b in bombs):
                return False
            return True

        if not can_walk(nx, ny) or random.random() < 0.3:
            possible = [i for i, (dxx, dyy) in enumerate(dirs) if can_walk(self.x + dxx, self.y + dyy)]
            if possible:
                self.dir = random.choice(possible)
                dx, dy = dirs[self.dir]
                nx, ny = self.x + dx, self.y + dy
            else:
                return

        self.x, self.y = nx, ny


class Bomb:
    def __init__(self, x, y, range_):
        self.x = x
        self.y = y
        self.timer = 2000
        self.range = range_


class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.start = pygame.time.get_ticks()
        self.duration = 400


# ==================== NIVELES ====================
LEVELS = {
    1: {
        "name": "Nivel 1 - Facil",
        "enemies": 4,
        "enemy_type": 1,
        "soft_chance": 0.50,
        "player_bombs": 1,
        "player_range": 1,
    },
    2: {
        "name": "Nivel 2 - Medio",
        "enemies": 6,
        "enemy_type": 2,
        "soft_chance": 0.60,
        "player_bombs": 2,
        "player_range": 2,
    },
    3: {
        "name": "Nivel 3 - Dificil",
        "enemies": 8,
        "enemy_type": 3,
        "soft_chance": 0.70,
        "player_bombs": 3,
        "player_range": 3,
    },
}


def create_map(soft_chance=0.55):
    game_map = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            if x == 0 or y == 0 or x == COLS - 1 or y == ROWS - 1 or (x % 2 == 0 and y % 2 == 0):
                row.append(SOLID)
            else:
                if (x <= 2 and y <= 2) or random.random() > soft_chance:
                    row.append(EMPTY)
                else:
                    row.append(SOFT)
        game_map.append(row)
    game_map[1][1] = EMPTY
    game_map[1][2] = EMPTY
    game_map[2][1] = EMPTY
    return game_map


def spawn_enemies(game_map, count, enemy_type):
    enemies = []
    attempts = 0
    while len(enemies) < count and attempts < 400:
        attempts += 1
        x = random.randint(1, COLS - 2)
        y = random.randint(1, ROWS - 2)
        if game_map[y][x] == EMPTY and not (x <= 4 and y <= 4):
            if not any(e.x == x and e.y == y for e in enemies):
                enemies.append(Enemy(x, y, enemy_type))
    return enemies


def explode(bomb, game_map, bombs, enemies, player, explosions):
    cells = [(bomb.x, bomb.y)]
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]

    for dx, dy in directions:
        for r in range(1, bomb.range + 1):
            nx, ny = bomb.x + dx * r, bomb.y + dy * r
            if not (0 <= nx < COLS and 0 <= ny < ROWS):
                break
            if game_map[ny][nx] == SOLID:
                break
            cells.append((nx, ny))
            if game_map[ny][nx] == SOFT:
                game_map[ny][nx] = EMPTY
                break

    for cx, cy in cells:
        explosions.append(Explosion(cx, cy))

    enemies[:] = [e for e in enemies if (e.x, e.y) not in cells]

    if (player.x, player.y) in cells:
        player.lives -= 1
        if player.lives > 0:
            player.x, player.y = 1, 1

    chain = [b for b in bombs if (b.x, b.y) in cells and b is not bomb]
    bombs[:] = [b for b in bombs if b is not bomb and b not in chain]
    for b in chain:
        explode(b, game_map, bombs, enemies, player, explosions)


# ==================== DIBUJO ====================
def draw_soft_block(screen, px, py, x, y):
    pattern = (x + y) % 3
    if pattern == 0:
        color = YELLOW
        dark = (200, 160, 10)
    elif pattern == 1:
        color = BLUE
        dark = (0, 35, 100)
    else:
        color = RED
        dark = (150, 10, 25)

    pygame.draw.rect(screen, color, (px, py, TILE, TILE))
    pygame.draw.rect(screen, dark, (px + 3, py + 3, TILE - 6, TILE - 6))
    pygame.draw.line(screen, dark, (px, py + TILE // 2), (px + TILE, py + TILE // 2), 2)
    pygame.draw.line(screen, dark, (px + TILE // 2, py), (px + TILE // 2, py + TILE // 2), 1)


def draw_player(screen, player):
    if player.lives <= 0:
        return
    cx = player.x * TILE + TILE // 2
    cy = player.y * TILE + TILE // 2

    pygame.draw.circle(screen, PLAYER_GREEN, (cx, cy), int(TILE * 0.36))
    pygame.draw.ellipse(screen, PLAYER_HAT, (cx - 14, cy - 20, 28, 14))
    pygame.draw.rect(screen, PLAYER_HAT, (cx - 10, cy - 14, 20, 8))
    pygame.draw.circle(screen, PLAYER_LIGHT, (cx, cy + 2), int(TILE * 0.22))
    pygame.draw.circle(screen, WHITE, (cx - 6, cy), 5)
    pygame.draw.circle(screen, WHITE, (cx + 6, cy), 5)
    pygame.draw.circle(screen, BLACK, (cx - 6, cy + 1), 2)
    pygame.draw.circle(screen, BLACK, (cx + 6, cy + 1), 2)
    pygame.draw.arc(screen, BLACK, (cx - 8, cy + 4, 16, 10), 3.5, 6.0, 2)


def draw_enemy(screen, e):
    cx = e.x * TILE + TILE // 2
    cy = e.y * TILE + TILE // 2
    color = e.color

    if e.type == 1:
        pygame.draw.circle(screen, color, (cx, cy), int(TILE * 0.34))
        for angle in range(0, 360, 45):
            rad = math.radians(angle)
            px = cx + int(math.cos(rad) * 16)
            py = cy + int(math.sin(rad) * 16)
            pygame.draw.circle(screen, color, (px, py), 5)
        pygame.draw.circle(screen, WHITE, (cx - 7, cy - 3), 5)
        pygame.draw.circle(screen, WHITE, (cx + 7, cy - 3), 5)
        pygame.draw.circle(screen, BLACK, (cx - 7, cy - 2), 3)
        pygame.draw.circle(screen, BLACK, (cx + 7, cy - 2), 3)
        pygame.draw.line(screen, BLACK, (cx - 12, cy - 10), (cx - 3, cy - 7), 2)
        pygame.draw.line(screen, BLACK, (cx + 3, cy - 7), (cx + 12, cy - 10), 2)

    elif e.type == 2:
        pygame.draw.rect(screen, color, (cx - 14, cy - 14, 28, 28), border_radius=4)
        pygame.draw.rect(screen, (255, 180, 100), (cx - 10, cy - 10, 20, 20), border_radius=3)
        pygame.draw.rect(screen, WHITE, (cx - 10, cy - 6, 8, 8))
        pygame.draw.rect(screen, WHITE, (cx + 2, cy - 6, 8, 8))
        pygame.draw.rect(screen, BLACK, (cx - 8, cy - 4, 4, 4))
        pygame.draw.rect(screen, BLACK, (cx + 4, cy - 4, 4, 4))
        pygame.draw.line(screen, (200, 200, 200), (cx, cy - 14), (cx, cy - 22), 2)
        pygame.draw.circle(screen, RED, (cx, cy - 24), 4)

    else:
        points = [(cx, cy - 16), (cx - 16, cy + 12), (cx + 16, cy + 12)]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, (100, 230, 255), [(cx, cy - 10), (cx - 10, cy + 8), (cx + 10, cy + 8)])
        pygame.draw.circle(screen, WHITE, (cx - 6, cy - 2), 6)
        pygame.draw.circle(screen, WHITE, (cx + 6, cy - 2), 6)
        pygame.draw.circle(screen, BLACK, (cx + 6, cy), 3)
        pygame.draw.circle(screen, BLACK, (cx - 6, cy), 3)


def draw_game(screen, game_map, player, enemies, bombs, explosions, font, level, level_name):
    screen.fill(DARK_BG)

    for y in range(ROWS):
        for x in range(COLS):
            px, py = x * TILE, y * TILE
            cell = game_map[y][x]

            if cell == SOLID:
                pygame.draw.rect(screen, SOLID_COLOR, (px, py, TILE, TILE))
                pygame.draw.rect(screen, SOLID_LIGHT, (px + 3, py + 3, TILE - 6, TILE - 6))
                pygame.draw.rect(screen, (40, 40, 50), (px, py, TILE, TILE), 2)
            elif cell == SOFT:
                draw_soft_block(screen, px, py, x, y)
            else:
                color = DARK_BG if (x + y) % 2 == 0 else NAVY
                pygame.draw.rect(screen, color, (px, py, TILE, TILE))

    for ex in explosions:
        pygame.draw.rect(screen, YELLOW, (ex.x * TILE + 4, ex.y * TILE + 4, TILE - 8, TILE - 8))
        pygame.draw.rect(screen, RED, (ex.x * TILE + 10, ex.y * TILE + 10, TILE - 20, TILE - 20))
        pygame.draw.rect(screen, WHITE, (ex.x * TILE + 15, ex.y * TILE + 15, TILE - 30, TILE - 30))

    now = pygame.time.get_ticks()
    for b in bombs:
        pulse = 0.85 + 0.15 * abs(((now // 50) % 20) - 10) / 10
        size = int(TILE * 0.55 * pulse)
        cx = b.x * TILE + TILE // 2
        cy = b.y * TILE + TILE // 2
        pygame.draw.circle(screen, (30, 30, 30), (cx, cy), size // 2)
        pygame.draw.circle(screen, (200, 200, 200), (cx - 4, cy - 5), max(2, size // 6))
        pygame.draw.line(screen, YELLOW, (cx, cy - size // 2), (cx + 6, cy - size // 2 - 12), 3)
        pygame.draw.circle(screen, RED, (cx + 6, cy - size // 2 - 14), 3)

    for e in enemies:
        draw_enemy(screen, e)

    draw_player(screen, player)

    pygame.draw.rect(screen, (15, 15, 25), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.line(screen, YELLOW, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 3)

    level_text = font.render(f"{level_name}", True, YELLOW)
    lives_text = font.render(f"Vidas: {player.lives}", True, WHITE)
    enemies_text = font.render(f"Enemigos: {len(enemies)}", True, WHITE)
    bombs_text = font.render(f"Bombas: {player.max_bombs - len(bombs)}", True, WHITE)

    screen.blit(level_text, (10, HEIGHT - 50))
    screen.blit(lives_text, (10, HEIGHT - 28))
    screen.blit(enemies_text, (200, HEIGHT - 28))
    screen.blit(bombs_text, (380, HEIGHT - 28))


def show_message(screen, font, big_font, text, subtext="", color=WHITE):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    msg = big_font.render(text, True, color)
    rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(msg, rect)

    if subtext:
        sub = font.render(subtext, True, (200, 200, 200))
        sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
        screen.blit(sub, sub_rect)

    restart = font.render("Presiona R para continuar / reiniciar", True, YELLOW)
    r_rect = restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    screen.blit(restart, r_rect)


def draw_menu(screen, font, big_font, selected):
    """Menú para elegir nivel 1, 2 o 3"""
    screen.fill(DARK_BG)

    title = big_font.render("BOMBERMAN COLOMBIA", True, YELLOW)
    title_rect = title.get_rect(center=(WIDTH // 2, 80))
    screen.blit(title, title_rect)

    subtitle = font.render("Elige el nivel que quieres jugar", True, WHITE)
    sub_rect = subtitle.get_rect(center=(WIDTH // 2, 130))
    screen.blit(subtitle, sub_rect)

    options = [
        ("1  -  Nivel 1  (Facil)", YELLOW),
        ("2  -  Nivel 2  (Medio)", (255, 180, 50)),
        ("3  -  Nivel 3  (Dificil)", RED),
    ]

    for i, (text, color) in enumerate(options):
        y = 200 + i * 70
        if selected == i + 1:
            pygame.draw.rect(screen, (40, 40, 60), (100, y - 15, WIDTH - 200, 50), border_radius=10)
            pygame.draw.rect(screen, color, (100, y - 15, WIDTH - 200, 50), 3, border_radius=10)

        label = big_font.render(text, True, color if selected == i + 1 else WHITE)
        label_rect = label.get_rect(center=(WIDTH // 2, y + 10))
        screen.blit(label, label_rect)

    inst1 = font.render("Usa las FLECHAS ARRIBA/ABAJO o las teclas 1, 2, 3", True, (180, 180, 180))
    inst2 = font.render("Presiona ENTER o ESPACIO para empezar", True, (180, 180, 180))
    screen.blit(inst1, inst1.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
    screen.blit(inst2, inst2.get_rect(center=(WIDTH // 2, HEIGHT - 70)))


# ==================== MAIN ====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Bomberman Colombia - 3 Niveles")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("segoeui", 18)
    big_font = pygame.font.SysFont("segoeui", 36, bold=True)

    state = "menu"
    selected_level = 1
    current_level = 1
    game_map = None
    player = None
    enemies = []
    bombs = []
    explosions = []
    level_name = ""

    def start_level(level_num):
        cfg = LEVELS[level_num]
        gmap = create_map(cfg["soft_chance"])
        p = Player(1, 1)
        p.max_bombs = cfg["player_bombs"]
        p.range = cfg["player_range"]
        p.lives = 3
        en = spawn_enemies(gmap, cfg["enemies"], cfg["enemy_type"])
        return gmap, p, en, [], [], cfg["name"]

    running = True

    while running:
        dt = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if state == "menu":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        selected_level = max(1, selected_level - 1)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        selected_level = min(3, selected_level + 1)
                    if event.key == pygame.K_1:
                        selected_level = 1
                    if event.key == pygame.K_2:
                        selected_level = 2
                    if event.key == pygame.K_3:
                        selected_level = 3
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                        current_level = selected_level
                        game_map, player, enemies, bombs, explosions, level_name = start_level(current_level)
                        state = "playing"

                elif state == "playing":
                    if event.key == pygame.K_SPACE:
                        if len(bombs) < player.max_bombs:
                            if not any(b.x == player.x and b.y == player.y for b in bombs):
                                bombs.append(Bomb(player.x, player.y, player.range))
                    if event.key == pygame.K_r:
                        state = "menu"

                elif state in ("game_over", "won_level", "won_game"):
                    if event.key == pygame.K_r:
                        if state == "won_game":
                            state = "menu"
                        elif state == "won_level":
                            current_level += 1
                            if current_level > 3:
                                state = "won_game"
                            else:
                                game_map, player, enemies, bombs, explosions, level_name = start_level(current_level)
                                state = "playing"
                        elif state == "game_over":
                            game_map, player, enemies, bombs, explosions, level_name = start_level(current_level)
                            state = "playing"

                    if event.key == pygame.K_m:
                        state = "menu"

        if state == "playing":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.try_move(0, -1, game_map, bombs)
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player.try_move(0, 1, game_map, bombs)
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.try_move(-1, 0, game_map, bombs)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.try_move(1, 0, game_map, bombs)

            for b in bombs[:]:
                b.timer -= dt
                if b.timer <= 0:
                    explode(b, game_map, bombs, enemies, player, explosions)

            now = pygame.time.get_ticks()
            explosions[:] = [e for e in explosions if now - e.start < e.duration]

            for e in enemies:
                e.update(dt, game_map, bombs)
                if e.x == player.x and e.y == player.y:
                    player.lives -= 1
                    if player.lives > 0:
                        player.x, player.y = 1, 1
                    else:
                        state = "game_over"

            if player.lives <= 0:
                state = "game_over"

            if len(enemies) == 0:
                if current_level == 3:
                    state = "won_game"
                else:
                    state = "won_level"

        if state == "menu":
            draw_menu(screen, font, big_font, selected_level)
        else:
            draw_game(screen, game_map, player, enemies, bombs, explosions, font, current_level, level_name)

            if state == "won_game":
                show_message(screen, font, big_font, "¡GANASTE EL JUEGO!", "Presiona R o M para volver al menu", YELLOW)
            elif state == "won_level":
                show_message(screen, font, big_font, f"¡NIVEL {current_level} COMPLETADO!", "Presiona R para el siguiente nivel", YELLOW)
            elif state == "game_over":
                show_message(screen, font, big_font, "¡HAS MUERTO!", "Presiona R para reiniciar | M para menu", RED)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()