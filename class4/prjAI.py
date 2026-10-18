######################載入套件/ import packages######################
import random
import pygame
import sys


######################物件類別/ object class######################
class Brick:
    def __init__(self, x, y, width, height, color, brick_type="normal", hits_left=1, moving=False):
        """
        初始化磚塊物件/initialize brick object
        x,y: 磚塊的位置/position of brick
        width,height: 磚塊的寬度/width and height of brick
        color: 磚塊的顏色/color of brick
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.brick_type = brick_type
        self.hit = False
        self.hits_left = hits_left
        self.max_hits = hits_left
        self.moving = moving
        self.move_direction = random.choice([-1, 1])

    def draw(self, display_area):
        """
        繪製磚塊物件/draw brick object
        display_area: 繪製區域/area to draw
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            center_x = self.rect.centerx
            center_y = self.rect.centery

            if self.moving:
                pygame.draw.line(display_area, (255, 255, 255), (center_x - 10, center_y), (center_x + 10, center_y), 2)
                pygame.draw.polygon(
                    display_area,
                    (255, 255, 255),
                    [(center_x - 10, center_y), (center_x - 5, center_y - 4), (center_x - 5, center_y + 4)],
                )
                pygame.draw.polygon(
                    display_area,
                    (255, 255, 255),
                    [(center_x + 10, center_y), (center_x + 5, center_y - 4), (center_x + 5, center_y + 4)],
                )
            if self.hits_left > 1:
                pygame.draw.rect(display_area, (255, 255, 255), self.rect, 2)

            if self.brick_type == "explosive":
                pygame.draw.circle(display_area, (255, 255, 255), (center_x, center_y + 1), 4)
                pygame.draw.line(display_area, (255, 255, 255), (center_x + 2, center_y - 3), (center_x + 5, center_y - 6), 2)
                pygame.draw.line(display_area, (255, 230, 80), (center_x + 5, center_y - 6), (center_x + 7, center_y - 4), 2)
            elif self.brick_type == "add_bricks":
                pygame.draw.line(display_area, (255, 255, 255), (center_x - 5, center_y), (center_x + 5, center_y), 3)
                pygame.draw.line(display_area, (255, 255, 255), (center_x, center_y - 5), (center_x, center_y + 5), 3)
            elif self.brick_type == "extra_ball":
                pygame.draw.circle(display_area, (255, 255, 255), (center_x, center_y), 5)
                pygame.draw.circle(display_area, self.color, (center_x, center_y), 2)
            elif self.brick_type == "restore":
                pygame.draw.circle(display_area, (255, 255, 255), (center_x, center_y), 5, 2)
                pygame.draw.polygon(
                    display_area,
                    (255, 255, 255),
                    [(center_x + 5, center_y - 5), (center_x + 5, center_y), (center_x, center_y - 5)],
                )

class Ball:
    def __init__(self, x, y, radius, color):
        """
        初始化球物件/initialize ball object
        x,y: 球的位置/position of ball
        radius: 球的半徑/radius of ball
        color: 球的顏色/color of ball
        """
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = 5
        self.speed_y = -5
        self.is_moving = False
        self.radius = radius
        self.last_brick = None
        self.previous_x = x
        self.previous_y = y


    def draw(self, display_area):
        """
        繪製球物件/draw ball object
        display_area: 繪製區域/area to draw
        """
        pygame.draw.circle(display_area, self.color,(self.x, self.y), self.radius)

    def move(self):
        """
        移動球物件/move ball object
        """
        if self.is_moving:
            self.previous_x = self.x
            self.previous_y = self.y
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad, piercing=False, invincible=False):
        """
        檢查球物件與磚塊物件是否有碰撞/check collision between ball and brick
        bg_x, bg_y: 背景的寬度/width of background
        bricks: 磚塊物件的陣列/array of brick objects
        pad: 底板物件/paddle object
        """
        if self.x - self.radius <= 0 or self.x + self.radius >= bg_x:
            self.speed_x = -self.speed_x

        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y

        if self.y + self.radius >= bg_y:
            if invincible:
                self.y = bg_y - self.radius
                self.speed_y = -abs(self.speed_y)
            else:
                self.is_moving = False

        # 檢查球物件與磚塊物件是否有碰撞
        if(
            self.y + self.radius >= pad.rect.y
            and self.y - self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        if self.last_brick is not None:
            dx = abs(self.x - self.last_brick.rect.centerx)
            dy = abs(self.y - self.last_brick.rect.centery)
            if (
                dx > self.radius + self.last_brick.rect.width / 2
                or dy > self.radius + self.last_brick.rect.height / 2
            ):
                self.last_brick = None

        for brick in bricks:
            if not brick.hit:
                left = brick.rect.left - self.radius
                right = brick.rect.right + self.radius
                top = brick.rect.top - self.radius
                bottom = brick.rect.bottom + self.radius

                if left <= self.x <= right and top <= self.y <= bottom:
                    if brick is self.last_brick:
                        continue

                    brick.hits_left -= 1
                    if brick.hits_left <= 0:
                        brick.hit = True
                    self.last_brick = brick

                    if not piercing:
                        came_from_top = self.previous_y + self.radius <= brick.rect.top
                        came_from_bottom = self.previous_y - self.radius >= brick.rect.bottom
                        came_from_left = self.previous_x + self.radius <= brick.rect.left
                        came_from_right = self.previous_x - self.radius >= brick.rect.right

                        if came_from_top and self.speed_y > 0:
                            self.y = top
                            self.speed_y = -abs(self.speed_y)
                        elif came_from_bottom and self.speed_y < 0:
                            self.y = bottom
                            self.speed_y = abs(self.speed_y)
                        elif came_from_left and self.speed_x > 0:
                            self.x = left
                            self.speed_x = -abs(self.speed_x)
                        elif came_from_right and self.speed_x < 0:
                            self.x = right
                            self.speed_x = abs(self.speed_x)
                        else:
                            overlaps = [
                                (self.x - left, "left"),
                                (right - self.x, "right"),
                                (self.y - top, "top"),
                                (bottom - self.y, "bottom"),
                            ]
                            side = min(overlaps)[1]
                            if side == "left":
                                self.x = left
                                self.speed_x = -abs(self.speed_x)
                            elif side == "right":
                                self.x = right
                                self.speed_x = abs(self.speed_x)
                            elif side == "top":
                                self.y = top
                                self.speed_y = -abs(self.speed_y)
                            else:
                                self.y = bottom
                                self.speed_y = abs(self.speed_y)

                    if brick.hit:
                        return brick

                    return None

        return None


######################定義函式區/ define functions######################

######################初始化設定/ initialize settings######################
pygame.init()
FPS = pygame.time.Clock()

######################載入圖片/ load images######################

######################遊戲視窗設定/ game window settings######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("打磚塊遊戲")
screen = pygame.display.set_mode(bg_size)
game_surface = pygame.Surface(bg_size)
score_font = pygame.font.Font(None, 28)
button_font = pygame.font.Font(None, 22)
info_font = pygame.font.Font(None, 30)
power_duration = 5000
power_cooldown = 15000
big_ball_button = pygame.Rect(16, 50, 184, 34)
piercing_button = pygame.Rect(212, 50, 184, 34)
wide_paddle_button = pygame.Rect(408, 50, 184, 34)
invincible_button = pygame.Rect(604, 50, 184, 34)
pause_button = pygame.Rect(16, 92, 184, 34)
ball_color_button = pygame.Rect(212, 92, 220, 34)
ball_colors = [
    (255, 215, 0),
    (100, 220, 255),
    (255, 100, 150),
    (150, 255, 100),
    (255, 255, 255),
]
ball_color_index = 0
paddle_power_duration = 5000
paddle_cooldown = power_cooldown
invincible_duration = 3000
invincible_cooldown = 13000


def draw_button(surface, button_rect, label, color):
    pygame.draw.rect(
        surface,
        (7, 12, 24),
        (button_rect.x, button_rect.y + 3, button_rect.width, button_rect.height),
    )
    pygame.draw.rect(surface, color, button_rect)
    pygame.draw.rect(surface, (105, 125, 155), button_rect, 1)
    pygame.draw.rect(
        surface,
        (150, 190, 235),
        (button_rect.x, button_rect.y + 4, 3, button_rect.height - 8),
    )
    button_text = button_font.render(label, True, (245, 248, 255))
    surface.blit(button_text, button_text.get_rect(center=button_rect.center))


######################磚塊設定/ brick settings######################
bricks_row =9
bricks_col = 11
brick_w = 58
brick_h = 16
bricks_gap =2


def create_brick(x, y):
    brick_type = "normal"
    special_type = random.randint(1, 10)
    if special_type == 8:
        brick_type = "explosive"
    elif special_type == 9:
        brick_type = "add_bricks"
    elif special_type == 10:
        brick_type = "extra_ball"
    elif special_type == 7:
        brick_type = "restore"

    if brick_type == "explosive":
        color = (255, 80, 40)
    elif brick_type == "add_bricks":
        color = (80, 220, 100)
    elif brick_type == "extra_ball":
        color = (80, 160, 255)
    elif brick_type == "restore":
        color = (180, 100, 230)
    else:
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    hits_left = 2 if random.randint(1, 8) == 1 else 1
    moving = random.randint(1, 10) == 1
    return Brick(x, y, brick_w, brick_h, color, brick_type, hits_left, moving)


def create_bricks(level):
    level_bricks = []
    pattern = (level - 1) % 3
    for col in range(bricks_col):
        for row in range(bricks_row):
            if pattern == 1 and (col + row) % 2 == 1:
                continue
            if pattern == 2 and abs(col - bricks_col // 2) + abs(row - bricks_row // 2) > 7:
                continue

            x = col * (brick_w + bricks_gap) + 70
            y = row * (brick_h + bricks_gap) + 140
            level_bricks.append(create_brick(x, y))

    return level_bricks


level = 1
bricks = create_bricks(level)
level_brick_limit = len(bricks)


def add_bricks(bricks, amount):
    for _ in range(amount):
        active_bricks = sum(not brick.hit for brick in bricks)
        if active_bricks >= level_brick_limit:
            break

        empty_positions = []
        for col in range(bricks_col):
            for row in range(bricks_row):
                x = col * (brick_w + bricks_gap) + 70
                y = row * (brick_h + bricks_gap) + 140
                position_is_used = False
                for brick in bricks:
                    if not brick.hit and brick.rect.topleft == (x, y):
                        position_is_used = True
                        break
                if not position_is_used:
                    empty_positions.append((x, y))

        if not empty_positions:
            break

        x, y = random.choice(empty_positions)
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        bricks.append(
            Brick(
                x,
                y,
                brick_w,
                brick_h,
                color,
                brick_type="normal",
                hits_left=1,
                moving=False,
            )
        )


def restore_nearby_bricks(bricks, source_brick):
    for brick in bricks:
        if (
            brick.hit
            and brick is not source_brick
            and abs(brick.rect.centerx - source_brick.rect.centerx) <= brick_w + bricks_gap
            and abs(brick.rect.centery - source_brick.rect.centery) <= brick_h + bricks_gap
        ):
            brick.hit = False
            brick.hits_left = brick.max_hits


######################顯示文字設定/ text display settings######################

######################底板設定/ paddle settings######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定/ ball settings######################
ball_radius = 10
ball_color = (255, 215, 0)
max_balls = 10
ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)
balls = [ball]
score = 0
starting_lives = 10
lives = starting_lives
game_over = False
paused = False
pause_started_at = 0
shake_end_time = 0
big_ball_end_time = 0
big_ball_cooldown_end_time = 0
piercing_end_time = 0
piercing_cooldown_end_time = 0
wide_paddle_end_time = 0
wide_paddle_cooldown_end_time = 0
invincible_end_time = 0
invincible_cooldown_end_time = 0

######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    current_time = pause_started_at if paused else pygame.time.get_ticks()
    game_surface.fill((10, 16, 29))#清空畫面
    if current_time < wide_paddle_end_time:
        pad.rect.width = brick_w * 2
    else:
        pad.rect.width = brick_w

    if not paused:
        mos_x, mos_y = pygame.mouse.get_pos()#取得滑鼠位置
        pad.rect.x = mos_x - pad.rect.width // 2#設定底板位置
        if pad.rect.x < 0:
            pad.rect.x = 0

        if pad.rect.x + pad.rect.width > bg_x:
            pad.rect.x = bg_x - pad.rect.width

    if not paused and not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if pause_button.collidepoint(mouse_pos):
                if not game_over:
                    if paused:
                        pause_duration = pygame.time.get_ticks() - pause_started_at
                        if big_ball_end_time > pause_started_at:
                            big_ball_end_time += pause_duration
                        if big_ball_cooldown_end_time > pause_started_at:
                            big_ball_cooldown_end_time += pause_duration
                        if piercing_end_time > pause_started_at:
                            piercing_end_time += pause_duration
                        if piercing_cooldown_end_time > pause_started_at:
                            piercing_cooldown_end_time += pause_duration
                        if wide_paddle_end_time > pause_started_at:
                            wide_paddle_end_time += pause_duration
                        if wide_paddle_cooldown_end_time > pause_started_at:
                            wide_paddle_cooldown_end_time += pause_duration
                        if invincible_end_time > pause_started_at:
                            invincible_end_time += pause_duration
                        if invincible_cooldown_end_time > pause_started_at:
                            invincible_cooldown_end_time += pause_duration
                        if shake_end_time > pause_started_at:
                            shake_end_time += pause_duration
                        paused = False
                    else:
                        paused = True
                        pause_started_at = pygame.time.get_ticks()
            elif ball_color_button.collidepoint(mouse_pos):
                ball_color_index = (ball_color_index + 1) % len(ball_colors)
                ball_color = ball_colors[ball_color_index]
                for current_ball in balls:
                    current_ball.color = ball_color
            elif not game_over and not paused and big_ball_button.collidepoint(mouse_pos):
                if pygame.time.get_ticks() >= big_ball_cooldown_end_time:
                    big_ball_end_time = pygame.time.get_ticks() + power_duration
                    big_ball_cooldown_end_time = pygame.time.get_ticks() + power_cooldown
            elif not game_over and not paused and piercing_button.collidepoint(mouse_pos):
                if pygame.time.get_ticks() >= piercing_cooldown_end_time:
                    piercing_end_time = pygame.time.get_ticks() + power_duration
                    piercing_cooldown_end_time = pygame.time.get_ticks() + power_cooldown
            elif not game_over and not paused and wide_paddle_button.collidepoint(mouse_pos):
                if pygame.time.get_ticks() >= wide_paddle_cooldown_end_time:
                    wide_paddle_end_time = pygame.time.get_ticks() + paddle_power_duration
                    wide_paddle_cooldown_end_time = pygame.time.get_ticks() + paddle_cooldown
            elif not game_over and not paused and invincible_button.collidepoint(mouse_pos):
                if pygame.time.get_ticks() >= invincible_cooldown_end_time:
                    invincible_end_time = pygame.time.get_ticks() + invincible_duration
                    invincible_cooldown_end_time = pygame.time.get_ticks() + invincible_cooldown
            elif not game_over and not paused:
                for current_ball in balls:
                    if not current_ball.is_moving:
                        current_ball.is_moving = True

    current_time = pause_started_at if paused else pygame.time.get_ticks()

    if not paused and not game_over:
        for brick in bricks:
            if not brick.hit and brick.moving:
                brick.rect.x += brick.move_direction * 2
                if brick.rect.left <= 20 or brick.rect.right >= bg_x - 20:
                    brick.move_direction = -brick.move_direction

    lost_ball = False
    for current_ball in balls[:] if not game_over and not paused else []:
        if current_time < big_ball_end_time:
            current_ball.radius = ball_radius * 2
        else:
            current_ball.radius = ball_radius

        if current_ball.is_moving:
            current_ball.move()
            was_moving = current_ball.is_moving
            hit_brick = current_ball.check_collision(
                bg_x,
                bg_y,
                bricks,
                pad,
                current_time < piercing_end_time,
                current_time < invincible_end_time,
            )
            if was_moving and not current_ball.is_moving:
                lost_ball = True
            if hit_brick is not None:
                score += 10
                if hit_brick.brick_type == "explosive":
                    shake_end_time = pygame.time.get_ticks() + 350
                    for brick in bricks:
                        if (
                            not brick.hit
                            and abs(brick.rect.centerx - hit_brick.rect.centerx) <= brick_w + bricks_gap
                            and abs(brick.rect.centery - hit_brick.rect.centery) <= brick_h + bricks_gap
                        ):
                            brick.hit = True
                            score += 10
                elif hit_brick.brick_type == "add_bricks":
                    add_bricks(bricks, 1)
                elif hit_brick.brick_type == "extra_ball":
                    if len(balls) < max_balls:
                        new_ball = Ball(current_ball.x, current_ball.y, ball_radius, ball_color)
                        new_ball.speed_x = -current_ball.speed_x
                        new_ball.speed_y = current_ball.speed_y
                        new_ball.is_moving = True
                        balls.append(new_ball)
                elif hit_brick.brick_type == "restore":
                    restore_nearby_bricks(bricks, hit_brick)

    balls = [current_ball for current_ball in balls if current_ball is ball or current_ball.is_moving]

    if not paused and lost_ball and not any(current_ball.is_moving for current_ball in balls):
        lives -= 1
        ball.is_moving = False
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius
        balls = [ball]
        if lives <= 0:
            game_over = True

    remaining_bricks = sum(not brick.hit for brick in bricks)
    if not paused and bricks and remaining_bricks <= 5:
        level += 1
        bricks = create_bricks(level)
        level_brick_limit = len(bricks)

    for brick in bricks:
        brick.draw(game_surface)

    pad.draw(game_surface)
    for current_ball in balls:
        current_ball.draw(game_surface)

    pygame.draw.rect(game_surface, (20, 30, 49), (0, 0, bg_x, 136))
    pygame.draw.line(game_surface, (47, 67, 95), (16, 40), (bg_x - 16, 40), 1)
    score_text = info_font.render(f"SCORE  {score}", True, (115, 220, 255))
    game_surface.blit(score_text, (20, 8))
    level_text = info_font.render(f"LEVEL  {level}", True, (205, 175, 255))
    game_surface.blit(level_text, level_text.get_rect(center=(bg_x // 2, 22)))
    lives_text = info_font.render(f"LIVES  {lives}", True, (255, 190, 115))
    game_surface.blit(lives_text, lives_text.get_rect(topright=(bg_x - 20, 8)))

    big_ball_active = current_time < big_ball_end_time
    if big_ball_active:
        big_ball_label = "BIG BALL ACTIVE"
        big_ball_color = (40, 150, 70)
    elif current_time < big_ball_cooldown_end_time:
        cooldown_left = (big_ball_cooldown_end_time - current_time + 999) // 1000
        big_ball_label = f"BIG BALL CD {cooldown_left}s"
        big_ball_color = (80, 80, 80)
    else:
        big_ball_label = "BIG BALL 5s"
        big_ball_color = (70, 70, 100)
    draw_button(game_surface, big_ball_button, big_ball_label, big_ball_color)

    piercing_active = current_time < piercing_end_time
    if piercing_active:
        piercing_label = "PIERCE ACTIVE"
        piercing_color = (180, 90, 30)
    elif current_time < piercing_cooldown_end_time:
        cooldown_left = (piercing_cooldown_end_time - current_time + 999) // 1000
        piercing_label = f"PIERCE CD {cooldown_left}s"
        piercing_color = (80, 80, 80)
    else:
        piercing_label = "PIERCE 5s"
        piercing_color = (100, 65, 45)
    draw_button(game_surface, piercing_button, piercing_label, piercing_color)

    if current_time < wide_paddle_end_time:
        wide_paddle_label = "WIDE PADDLE ACTIVE"
        wide_paddle_color = (40, 150, 70)
    elif current_time < wide_paddle_cooldown_end_time:
        cooldown_left = (wide_paddle_cooldown_end_time - current_time + 999) // 1000
        wide_paddle_label = f"COOLDOWN {cooldown_left}s"
        wide_paddle_color = (80, 80, 80)
    else:
        wide_paddle_label = "WIDE PADDLE 5s"
        wide_paddle_color = (70, 70, 100)
    draw_button(game_surface, wide_paddle_button, wide_paddle_label, wide_paddle_color)

    pause_label = "RESUME" if paused else "PAUSE"
    pause_color = (40, 120, 150) if paused else (70, 70, 100)
    draw_button(game_surface, pause_button, pause_label, pause_color)

    color_label = "BALL COLOR"
    draw_button(game_surface, ball_color_button, color_label, (70, 70, 100))
    pygame.draw.circle(game_surface, ball_color, (ball_color_button.right - 18, ball_color_button.centery), 9)

    if current_time < invincible_end_time:
        invincible_label = "SHIELD ACTIVE"
        invincible_color = (40, 150, 180)
    elif current_time < invincible_cooldown_end_time:
        cooldown_left = (invincible_cooldown_end_time - current_time + 999) // 1000
        invincible_label = f"SHIELD CD {cooldown_left}s"
        invincible_color = (80, 80, 80)
    else:
        invincible_label = "SHIELD 3s"
        invincible_color = (50, 100, 130)
    draw_button(game_surface, invincible_button, invincible_label, invincible_color)
    if current_time < invincible_end_time:
        pygame.draw.line(game_surface, (80, 220, 255), (0, bg_y - 3), (bg_x, bg_y - 3), 5)

    if game_over:
        game_over_text = score_font.render("GAME OVER", True, (255, 80, 80))
        game_surface.blit(game_over_text, game_over_text.get_rect(center=(bg_x // 2, bg_y // 2)))
    elif paused:
        paused_text = score_font.render("PAUSED", True, (255, 255, 255))
        game_surface.blit(paused_text, paused_text.get_rect(center=(bg_x // 2, bg_y // 2)))

    screen.fill((0, 0, 0))
    shake_x = 0
    shake_y = 0
    if pygame.time.get_ticks() < shake_end_time:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)
    screen.blit(game_surface, (shake_x, shake_y))
    pygame.display.update()