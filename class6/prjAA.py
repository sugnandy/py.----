import math
import random
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 900, 700
ARENA = pygame.Rect(20, 86, WIDTH - 40, HEIGHT - 106)
FPS = 60
CRYSTAL_GOAL = 8

BG = (20, 28, 42)
FLOOR = (31, 45, 59)
GRID = (39, 55, 69)
WHITE = (244, 247, 250)
MINT = (88, 232, 183)
GOLD = (255, 207, 89)
RED = (255, 105, 117)
BLUE = (91, 178, 255)

CHARACTERS = [
    {
        "name": "遊俠",
        "color": BLUE,
        "health": 100,
        "speed": 225,
        "attack": "single",
        "attack_name": "精準射擊",
        "description": "均衡的單發攻擊",
    },
    {
        "name": "散彈手",
        "color": GOLD,
        "health": 110,
        "speed": 195,
        "attack": "spread",
        "attack_name": "扇形散射",
        "description": "一次射出三發，近距離威力強",
    },
    {
        "name": "速射手",
        "color": MINT,
        "health": 85,
        "speed": 245,
        "attack": "rapid",
        "attack_name": "高速連射",
        "description": "傷害較低，但可以快速連射",
    },
    {
        "name": "狙擊手",
        "color": (202, 117, 255),
        "health": 90,
        "speed": 205,
        "attack": "sniper",
        "attack_name": "強力狙擊",
        "description": "射速較慢，單發傷害最高",
    },
    {
        "name": "彈射",
        "color": (255, 155, 91),
        "health": 100,
        "speed": 215,
        "attack": "bounce",
        "attack_name": "反彈射擊",
        "description": "子彈撞到牆壁後會反彈",
    },
]

MODES = [
    {
        "id": "crystal",
        "name": "星晶爭奪",
        "description": "收集 8 顆星晶即可獲勝",
    },
    {
        "id": "elimination",
        "name": "淘汰對決",
        "description": "擊敗所有對手即可獲勝",
    },
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("星晶競技場 | GEM ARENA")
clock = pygame.time.Clock()


def make_font(size, bold=False):
    return pygame.font.SysFont("Microsoft JhengHei", size, bold=bold)


title_font = make_font(34, True)
large_font = make_font(48, True)
medium_font = make_font(23, True)
small_font = make_font(17)
tiny_font = make_font(14)


class Fighter:
    def __init__(self, x, y, color, name, is_player=False, character=None):
        self.pos = pygame.Vector2(x, y)
        self.color = color
        self.name = name
        self.is_player = is_player
        self.radius = 18 if is_player else 16
        self.max_health = character["health"] if is_player else 65
        self.health = self.max_health
        self.speed = character["speed"] if is_player else 112
        self.attack = character["attack"] if is_player else "single"
        self.shot_timer = 0.0
        self.hit_timer = 0.0
        self.alive = True
        self.facing = pygame.Vector2(1, 0)

    def move(self, direction, obstacles, dt):
        if direction.length_squared() == 0:
            return
        direction = direction.normalize()
        distance = direction * self.speed * dt
        for axis in ("x", "y"):
            candidate = self.pos.copy()
            setattr(candidate, axis, getattr(candidate, axis) + getattr(distance, axis))
            body = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
            body.center = (round(candidate.x), round(candidate.y))
            if ARENA.contains(body) and not any(body.colliderect(wall) for wall in obstacles):
                self.pos = candidate

    def draw(self, surface):
        center = (round(self.pos.x), round(self.pos.y))
        if self.hit_timer > 0 and int(self.hit_timer * 18) % 2 == 0:
            body_color = WHITE
        else:
            body_color = self.color
        pygame.draw.circle(surface, (12, 19, 29), (center[0], center[1] + 4), self.radius + 3)
        pygame.draw.circle(surface, body_color, center, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), center, self.radius, 2)
        tip = self.pos + self.facing * (self.radius + 10)
        pygame.draw.line(surface, (226, 235, 243), center, (round(tip.x), round(tip.y)), 6)
        pygame.draw.circle(surface, (226, 235, 243), (round(tip.x), round(tip.y)), 4)
        if not self.is_player:
            bar = pygame.Rect(center[0] - 20, center[1] - self.radius - 12, 40, 5)
            pygame.draw.rect(surface, (16, 23, 32), bar, border_radius=3)
            fill = bar.copy()
            fill.width = round(bar.width * max(0, self.health / self.max_health))
            if fill.width:
                pygame.draw.rect(surface, MINT, fill, border_radius=3)


class Bullet:
    def __init__(self, position, direction, owner, color, damage, speed, can_bounce=False):
        self.pos = pygame.Vector2(position)
        self.velocity = direction.normalize() * speed
        self.owner = owner
        self.color = color
        self.damage = damage
        self.life = 1.8
        self.radius = 5
        self.can_bounce = can_bounce

    def update(self, dt, walls):
        self.life -= dt
        if not self.can_bounce:
            self.pos += self.velocity * dt
            return

        steps = max(1, math.ceil(max(abs(self.velocity.x * dt),
                                     abs(self.velocity.y * dt)) / self.radius))
        for _ in range(steps):
            for axis in ("x", "y"):
                candidate = self.pos.copy()
                setattr(candidate, axis, getattr(candidate, axis)
                        + getattr(self.velocity, axis) * dt / steps)
                body = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
                body.center = (round(candidate.x), round(candidate.y))
                if (not ARENA.contains(body)
                        or any(body.colliderect(wall) for wall in walls)):
                    setattr(self.velocity, axis, -getattr(self.velocity, axis))
                else:
                    self.pos = candidate

    def draw(self, surface):
        center = (round(self.pos.x), round(self.pos.y))
        pygame.draw.circle(surface, self.color, center, self.radius + 3)
        pygame.draw.circle(surface, WHITE, center, self.radius)


class Crystal:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.phase = random.random() * math.tau

    def draw(self, surface, elapsed):
        bob = math.sin(elapsed * 3 + self.phase) * 3
        x, y = round(self.pos.x), round(self.pos.y + bob)
        pygame.draw.circle(surface, (50, 124, 112), (x, y), 16)
        points = [(x, y - 10), (x + 8, y - 3), (x + 6, y + 7),
                  (x, y + 11), (x - 6, y + 7), (x - 8, y - 3)]
        pygame.draw.polygon(surface, MINT, points)
        pygame.draw.line(surface, (219, 255, 242), (x, y - 7), (x, y + 6), 2)


def create_game(character):
    walls = [
        pygame.Rect(120, 168, 112, 30),
        pygame.Rect(668, 168, 112, 30),
        pygame.Rect(120, 500, 112, 30),
        pygame.Rect(668, 500, 112, 30),
        pygame.Rect(300, 225, 38, 104),
        pygame.Rect(562, 225, 38, 104),
        pygame.Rect(300, 398, 38, 104),
        pygame.Rect(562, 398, 38, 104),
        pygame.Rect(412, 160, 76, 26),
        pygame.Rect(412, 532, 76, 26),
    ]
    player = Fighter(450, 350, character["color"], character["name"], True, character)
    bots = [
        Fighter(76, 124, RED, "赤狐"),
        Fighter(824, 124, (255, 155, 91), "橘子"),
        Fighter(76, 618, (202, 117, 255), "紫電"),
        Fighter(824, 618, (255, 119, 190), "粉星"),
    ]
    return player, bots, walls, [], [], 0


def spawn_crystal(walls, fighters):
    for _ in range(100):
        x = random.randint(58, WIDTH - 58)
        y = random.randint(116, HEIGHT - 58)
        point = pygame.Vector2(x, y)
        if any(wall.inflate(34, 34).collidepoint(x, y) for wall in walls):
            continue
        if any(fighter.alive and point.distance_to(fighter.pos) < 70 for fighter in fighters):
            continue
        return Crystal(x, y)
    return None


def draw_arena(surface, walls):
    surface.fill(BG)
    pygame.draw.rect(surface, FLOOR, ARENA, border_radius=18)
    clip = surface.get_clip()
    surface.set_clip(ARENA)
    for x in range(ARENA.left + 18, ARENA.right, 36):
        pygame.draw.line(surface, GRID, (x, ARENA.top), (x, ARENA.bottom), 1)
    for y in range(ARENA.top + 18, ARENA.bottom, 36):
        pygame.draw.line(surface, GRID, (ARENA.left, y), (ARENA.right, y), 1)
    for wall in walls:
        shadow = wall.move(0, 6)
        pygame.draw.rect(surface, (17, 26, 34), shadow, border_radius=8)
        pygame.draw.rect(surface, (78, 105, 113), wall, border_radius=8)
        pygame.draw.rect(surface, (105, 137, 139), wall, 2, border_radius=8)
    surface.set_clip(clip)
    pygame.draw.rect(surface, (76, 111, 121), ARENA, 2, border_radius=18)


def draw_hud(surface, player, score, alive_bots, mode_name):
    pygame.draw.rect(surface, (24, 34, 48), (0, 0, WIDTH, 76))
    label = title_font.render("星晶競技場", True, WHITE)
    surface.blit(label, (24, 15))
    if mode_name == "星晶爭奪":
        pygame.draw.circle(surface, MINT, (255, 37), 9)
        surface.blit(make_font(22, True).render(f"{score} / {CRYSTAL_GOAL}", True, WHITE),
                     (273, 23))
    else:
        surface.blit(small_font.render("淘汰對決", True, WHITE), (260, 29))
    surface.blit(tiny_font.render(f"{player.name} | {mode_name}", True, (190, 209, 218)),
                 (354, 31))

    health_x, health_y = 500, 28
    pygame.draw.rect(surface, (54, 65, 77), (health_x, health_y, 190, 18), border_radius=9)
    health_width = round(186 * max(0, player.health / player.max_health))
    if health_width:
        color = MINT if player.health > 35 else RED
        pygame.draw.rect(surface, color, (health_x + 2, health_y + 2, health_width, 14), border_radius=7)
    surface.blit(small_font.render(f"生命 {max(0, player.health)}", True, WHITE), (health_x, 49))
    surface.blit(small_font.render(f"對手 {alive_bots}", True, (255, 184, 176)), (730, 27))


def draw_character_selection(surface, selected_character):
    surface.fill(BG)
    heading = title_font.render("選擇角色", True, WHITE)
    surface.blit(heading, heading.get_rect(center=(WIDTH // 2, 78)))
    hint = small_font.render("左右方向鍵選擇，Enter 確認，ESC 離開", True, (216, 226, 235))
    surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 124)))

    gap = 12
    card_width = min(198, (WIDTH - 32 - gap * (len(CHARACTERS) - 1)) // len(CHARACTERS))
    card_height = 300
    total_width = len(CHARACTERS) * card_width + (len(CHARACTERS) - 1) * gap
    start_x = (WIDTH - total_width) // 2
    for index, character in enumerate(CHARACTERS):
        card = pygame.Rect(
            start_x + index * (card_width + gap), 180, card_width, card_height
        )
        selected = index == selected_character
        pygame.draw.rect(surface, (39, 55, 69) if selected else (27, 39, 53),
                         card, border_radius=14)
        pygame.draw.rect(surface, character["color"] if selected else (76, 91, 105),
                         card, 3 if selected else 1, border_radius=14)
        pygame.draw.circle(surface, character["color"], (card.centerx, card.y + 55), 24)

        name = medium_font.render(character["name"], True, WHITE)
        surface.blit(name, name.get_rect(center=(card.centerx, card.y + 104)))
        attack = small_font.render(character["attack_name"], True, MINT)
        surface.blit(attack, attack.get_rect(center=(card.centerx, card.y + 145)))

        health = small_font.render(f"生命：{character['health']}", True, WHITE)
        speed = small_font.render(f"速度：{character['speed']}", True, WHITE)
        surface.blit(health, health.get_rect(center=(card.centerx, card.y + 191)))
        surface.blit(speed, speed.get_rect(center=(card.centerx, card.y + 221)))
        for line_index, line in enumerate(
                (character["description"][offset:offset + 12]
                 for offset in range(0, len(character["description"]), 12))):
            detail = tiny_font.render(line, True, (190, 209, 218))
            surface.blit(detail, detail.get_rect(center=(card.centerx, card.y + 260 + line_index * 20)))


def draw_mode_selection(surface, selected_mode):
    surface.fill(BG)
    heading = title_font.render("選擇模式", True, WHITE)
    surface.blit(heading, heading.get_rect(center=(WIDTH // 2, 120)))
    hint = small_font.render("左右方向鍵選擇，Enter 開始，Backspace 返回選角", True,
                             (216, 226, 235))
    surface.blit(hint, hint.get_rect(center=(WIDTH // 2, 166)))

    card_width = 330
    card_height = 210
    gap = 32
    start_x = (WIDTH - (card_width * 2 + gap)) // 2
    for index, mode in enumerate(MODES):
        card = pygame.Rect(start_x + index * (card_width + gap), 245, card_width, card_height)
        selected = index == selected_mode
        color = MINT if index == 0 else RED
        pygame.draw.rect(surface, (39, 55, 69) if selected else (27, 39, 53),
                         card, border_radius=14)
        pygame.draw.rect(surface, color if selected else (76, 91, 105),
                         card, 3 if selected else 1, border_radius=14)
        name = medium_font.render(mode["name"], True, WHITE)
        detail = small_font.render(mode["description"], True, (216, 226, 235))
        surface.blit(name, name.get_rect(center=(card.centerx, card.y + 76)))
        surface.blit(detail, detail.get_rect(center=(card.centerx, card.y + 130)))


def draw_overlay(surface, heading, subtitle, hint):
    shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    shade.fill((8, 14, 23, 190))
    surface.blit(shade, (0, 0))
    title = large_font.render(heading, True, WHITE)
    detail = medium_font.render(subtitle, True, MINT)
    prompt = small_font.render(hint, True, (216, 226, 235))
    surface.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))
    surface.blit(detail, detail.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    surface.blit(prompt, prompt.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 54)))


def main():
    selected_character = 0
    selected_mode = 0
    player, bots, walls, bullets, crystals, score = create_game(CHARACTERS[selected_character])
    game_state = "menu"
    game_mode = MODES[selected_mode]["id"]
    elapsed = 0.0
    running = True

    while running:
        dt = min(clock.tick(FPS) / 1000, 0.04)
        elapsed += dt
        mouse = pygame.Vector2(pygame.mouse.get_pos())

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif game_state == "menu" and event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    game_state = "character_select"
                elif game_state == "character_select":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_character = (selected_character - 1) % len(CHARACTERS)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_character = (selected_character + 1) % len(CHARACTERS)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_state = "mode_select"
                elif game_state == "mode_select":
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_mode = (selected_mode - 1) % len(MODES)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_mode = (selected_mode + 1) % len(MODES)
                    elif event.key == pygame.K_BACKSPACE:
                        game_state = "character_select"
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        game_mode = MODES[selected_mode]["id"]
                        player, bots, walls, bullets, crystals, score = create_game(
                            CHARACTERS[selected_character]
                        )
                        if game_mode == "crystal":
                            crystals = [
                                gem for _ in range(5)
                                if (gem := spawn_crystal(walls, [player] + bots))
                            ]
                        game_state = "playing"
                        elapsed = 0.0
                elif game_state in ("win", "lose"):
                    if event.key == pygame.K_SPACE:
                        player, bots, walls, bullets, crystals, score = create_game(
                            CHARACTERS[selected_character]
                        )
                        if game_mode == "crystal":
                            crystals = [
                                gem for _ in range(5)
                                if (gem := spawn_crystal(walls, [player] + bots))
                            ]
                        game_state = "playing"
                        elapsed = 0.0
                    elif event.key == pygame.K_c:
                        game_state = "character_select"

        if game_state == "playing":
            keys = pygame.key.get_pressed()
            direction = pygame.Vector2(
                int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT]),
                int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP]),
            )
            player.move(direction, walls, dt)
            aim = mouse - player.pos
            if aim.length_squared() > 0:
                player.facing = aim.normalize()
            player.shot_timer = max(0.0, player.shot_timer - dt)
            player.hit_timer = max(0.0, player.hit_timer - dt)
            if pygame.mouse.get_pressed()[0] and player.shot_timer == 0:
                if player.attack == "spread":
                    for angle in (-18, 0, 18):
                        shot_direction = player.facing.rotate(angle)
                        bullets.append(Bullet(player.pos + shot_direction * 22, shot_direction,
                                              "player", GOLD, 12, 480))
                    player.shot_timer = 0.62
                elif player.attack == "rapid":
                    bullets.append(Bullet(player.pos + player.facing * 22, player.facing,
                                          "player", MINT, 11, 560))
                    player.shot_timer = 0.12
                elif player.attack == "sniper":
                    bullets.append(Bullet(player.pos + player.facing * 22, player.facing,
                                          "player", (202, 117, 255), 48, 760))
                    player.shot_timer = 0.8
                elif player.attack == "bounce":
                    bullets.append(Bullet(player.pos + player.facing * 22, player.facing,
                                          "player", (255, 155, 91), 20, 520, can_bounce=True))
                    player.shot_timer = 0.34
                else:
                    bullets.append(Bullet(player.pos + player.facing * 22, player.facing,
                                          "player", GOLD, 25, 560))
                    player.shot_timer = 0.26

            for bot in bots:
                if not bot.alive:
                    continue
                bot.shot_timer = max(0.0, bot.shot_timer - dt)
                bot.hit_timer = max(0.0, bot.hit_timer - dt)
                to_player = player.pos - bot.pos
                distance = to_player.length()
                if distance > 0:
                    bot.facing = to_player.normalize()
                move_direction = pygame.Vector2()
                if distance > 210:
                    move_direction = to_player
                elif distance < 145:
                    move_direction = -to_player
                if move_direction.length_squared() > 0:
                    bot.move(move_direction, walls, dt)
                if distance < 440 and bot.shot_timer == 0:
                    spread = random.uniform(-0.09, 0.09)
                    direction_to_player = bot.facing.rotate(math.degrees(spread))
                    bullets.append(Bullet(bot.pos + direction_to_player * 20, direction_to_player,
                                          "bot", RED, 12, 340))
                    bot.shot_timer = random.uniform(0.9, 1.35)

            for bullet in bullets[:]:
                bullet.update(dt, walls)
                point = (round(bullet.pos.x), round(bullet.pos.y))
                if (bullet.life <= 0 or (not bullet.can_bounce and
                        (not ARENA.collidepoint(point)
                         or any(wall.collidepoint(point) for wall in walls)))):
                    bullets.remove(bullet)
                    continue
                if bullet.owner == "player":
                    target = next((bot for bot in bots if bot.alive
                                   and bullet.pos.distance_to(bot.pos) < bot.radius + bullet.radius), None)
                    if target:
                        target.health -= bullet.damage
                        target.hit_timer = 0.12
                        bullets.remove(bullet)
                        if target.health <= 0:
                            target.alive = False
                            if game_mode == "crystal":
                                gem = spawn_crystal(walls, [player] + bots)
                                if gem:
                                    crystals.append(gem)
                elif bullet.pos.distance_to(player.pos) < player.radius + bullet.radius:
                    bullets.remove(bullet)
                    if player.hit_timer == 0:
                        player.health -= bullet.damage
                        player.hit_timer = 0.65
                        if player.health <= 0:
                            game_state = "lose"

            if game_mode == "crystal":
                for gem in crystals[:]:
                    if gem.pos.distance_to(player.pos) < player.radius + 13:
                        crystals.remove(gem)
                        score += 1
                        replacement = spawn_crystal(walls, [player] + bots)
                        if replacement and score < CRYSTAL_GOAL:
                            crystals.append(replacement)
            if game_state == "playing" and game_mode == "crystal" and score >= CRYSTAL_GOAL:
                game_state = "win"
            elif (game_state == "playing" and game_mode == "elimination"
                  and not any(bot.alive for bot in bots)):
                game_state = "win"

        draw_arena(screen, walls)
        mode_name = next(mode["name"] for mode in MODES if mode["id"] == game_mode)
        draw_hud(screen, player, score, sum(bot.alive for bot in bots), mode_name)
        for gem in crystals:
            gem.draw(screen, elapsed)
        for bullet in bullets:
            bullet.draw(screen)
        for bot in bots:
            if bot.alive:
                bot.draw(screen)
        player.draw(screen)
        footer_text = ("WASD / 方向鍵 移動     滑鼠瞄準與射擊     收集 8 顆星晶！"
                       if game_mode == "crystal"
                       else "WASD / 方向鍵 移動     滑鼠瞄準與射擊     擊敗所有對手！")
        footer = small_font.render(footer_text, True, (190, 209, 218))
        screen.blit(footer, footer.get_rect(center=(WIDTH // 2, HEIGHT - 15)))

        if game_state == "menu":
            draw_overlay(screen, "星晶競技場", "選擇角色與模式，開始你的競技！",
                          "按 SPACE / ENTER 開始，ESC 離開")
        elif game_state == "character_select":
            draw_character_selection(screen, selected_character)
        elif game_state == "mode_select":
            draw_mode_selection(screen, selected_mode)
        elif game_state == "win":
            result = f"你收集了 {score} 顆星晶" if game_mode == "crystal" else "你擊敗了所有對手！"
            draw_overlay(screen, "勝利！", result, "按 SPACE 再玩一次，C 重新選角，ESC 離開")
        elif game_state == "lose":
            draw_overlay(screen, "再接再厲！", f"你收集到 {score} 顆星晶",
                         "按 SPACE 再試一次，C 重新選角，ESC 離開")

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()