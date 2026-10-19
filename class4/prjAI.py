######################載入套件/ import packages######################
import random
import pygame
import sys
import math


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
window_height = bg_y + 50
bg_size = (bg_x, window_height)
pygame.display.set_caption("打磚塊遊戲")
screen = pygame.display.set_mode(bg_size)
game_surface = pygame.Surface(bg_size)
score_font = pygame.font.SysFont("Microsoft JhengHei", 28)
button_font = pygame.font.SysFont("Microsoft JhengHei", 16)
info_font = pygame.font.SysFont("Microsoft JhengHei", 30)
level_clear_font = pygame.font.SysFont("Microsoft JhengHei", 48, bold=True)
home_title_font = pygame.font.SysFont("Microsoft JhengHei", 46, bold=True)
home_body_font = pygame.font.SysFont("Microsoft JhengHei", 21)
home_small_font = pygame.font.SysFont("Microsoft JhengHei", 18)
power_duration = 5000
button_y = bg_y + 10
button_width = 104
button_height = 28
button_gap = 6
big_ball_button = pygame.Rect(8, button_y, button_width, button_height)
piercing_button = pygame.Rect(8 + (button_width + button_gap), button_y, button_width, button_height)
wide_paddle_button = pygame.Rect(8 + (button_width + button_gap) * 2, button_y, button_width, button_height)
invincible_button = pygame.Rect(8 + (button_width + button_gap) * 3, button_y, button_width, button_height)
pause_button = pygame.Rect(8 + (button_width + button_gap) * 4, button_y, button_width, button_height)
ball_color_button = pygame.Rect(8 + (button_width + button_gap) * 5, button_y, button_width, button_height)
shop_button = pygame.Rect(8 + (button_width + button_gap) * 6, button_y, button_width, button_height)
shop_panel = pygame.Rect(140, 70, 520, 500)
shop_close_button = pygame.Rect(shop_panel.right - 42, shop_panel.y + 12, 30, 30)
shop_buy_buttons = [
    pygame.Rect(shop_panel.x + 370, shop_panel.y + 115 + index * 46, 120, 34)
    for index in range(8)
]
ball_colors = [
    (255, 215, 0),
    (100, 220, 255),
    (255, 100, 150),
    (150, 255, 100),
    (255, 255, 255),
]
ball_color_index = 0
paddle_power_duration = 5000
invincible_duration = 3000
start_button = pygame.Rect(bg_x // 2 - 110, 558, 220, 54)
shop_items = [
    ("big_ball", "大球"),
    ("piercing", "穿透"),
    ("wide_paddle", "底板加寬"),
    ("invincible", "護盾"),
    ("life", "生命值 +1"),
    ("level", "直接通關"),
    ("ball_color", "球的顏色"),
    ("aiming", "拖曳瞄準"),
]
shop_item_prices = {
    "big_ball": 500,
    "piercing": 500,
    "wide_paddle": 500,
    "invincible": 500,
    "life": 100,
    "level": 500,
    "ball_color": 50,
    "aiming": 50,
}


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
brick_colors = {
    "normal": (135, 175, 225),
    "explosive": (255, 80, 40),
    "add_bricks": (80, 220, 100),
    "extra_ball": (80, 160, 255),
    "restore": (180, 100, 230),
}


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

    color = brick_colors[brick_type]

    hits_left = 2 if random.randint(1, 8) == 1 else 1
    moving = random.randint(1, 10) == 1
    return Brick(x, y, brick_w, brick_h, color, brick_type, hits_left, moving)


def create_bricks(level):
    level_bricks = []
    grid_positions = [
        (
            col * (brick_w + bricks_gap) + 70,
            row * (brick_h + bricks_gap) + 140,
        )
        for col in range(bricks_col)
        for row in range(bricks_row)
    ]
    while True:
        positions = frozenset(random.sample(grid_positions, random.randint(55, 90)))
        if positions not in generated_layouts:
            generated_layouts.add(positions)
            break

    for x, y in positions:
        level_bricks.append(create_brick(x, y))

    return level_bricks


level = 1
generated_layouts = set()
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
        bricks.append(
            Brick(
                x,
                y,
                brick_w,
                brick_h,
                brick_colors["normal"],
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
pad_width = 90
pad_height = 20
wide_pad_width = 140
pad = Brick(0, bg_y - 48, pad_width, pad_height, (255, 255, 255))
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
piercing_end_time = 0
wide_paddle_end_time = 0
invincible_end_time = 0
level_clear_end_time = 0
is_aiming = False
aim_start_pos = None
aim_current_pos = None
game_started = False
keyboard_controls_paddle = False
power_uses = {power_name: 3 for power_name, _ in shop_items}
shop_open = False
shop_opened_at = 0
shop_message = ""
unlocked_features = set()
aim_mode_enabled = False


def activate_power(power_name, current_time):
    global big_ball_end_time, piercing_end_time, wide_paddle_end_time, invincible_end_time
    if power_uses[power_name] <= 0:
        return

    power_uses[power_name] -= 1
    if power_name == "big_ball":
        big_ball_end_time = current_time + power_duration
    elif power_name == "piercing":
        piercing_end_time = current_time + power_duration
    elif power_name == "wide_paddle":
        wide_paddle_end_time = current_time + paddle_power_duration
    elif power_name == "invincible":
        invincible_end_time = current_time + invincible_duration


def close_shop(current_time):
    global shop_open
    global big_ball_end_time, piercing_end_time, wide_paddle_end_time, invincible_end_time
    global shake_end_time, level_clear_end_time
    shop_duration = current_time - shop_opened_at
    if big_ball_end_time > shop_opened_at:
        big_ball_end_time += shop_duration
    if piercing_end_time > shop_opened_at:
        piercing_end_time += shop_duration
    if wide_paddle_end_time > shop_opened_at:
        wide_paddle_end_time += shop_duration
    if invincible_end_time > shop_opened_at:
        invincible_end_time += shop_duration
    if shake_end_time > shop_opened_at:
        shake_end_time += shop_duration
    if level_clear_end_time > shop_opened_at:
        level_clear_end_time += shop_duration
    shop_open = False


def advance_level(current_time):
    global level, bricks, level_brick_limit, lives, ball, balls
    global is_aiming, aim_start_pos, aim_current_pos, level_clear_end_time
    level += 1
    bricks = create_bricks(level)
    level_brick_limit = len(bricks)
    lives += 2
    ball.is_moving = False
    ball.radius = ball_radius
    ball.x = pad.rect.x + pad.rect.width // 2
    ball.y = pad.rect.y - ball.radius
    balls = [ball]
    is_aiming = False
    aim_start_pos = None
    aim_current_pos = None
    level_clear_end_time = current_time + 2500


######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    if not game_started:
        screen.fill((10, 16, 29))
        title = home_title_font.render("打磚塊遊戲", True, (115, 220, 255))
        screen.blit(title, title.get_rect(center=(bg_x // 2, 58)))
        subtitle = home_body_font.render("瞄準方向，擊碎磚塊，善用特殊效果！", True, (205, 215, 230))
        screen.blit(subtitle, subtitle.get_rect(center=(bg_x // 2, 108)))
        section_title = home_body_font.render("磚塊效果", True, (255, 225, 130))
        screen.blit(section_title, (104, 145))

        brick_guide = [
            ((135, 175, 225), "一般磚塊", "普通磚塊；部分磚塊有白框，需要擊中兩次。"),
            (brick_colors["normal"], "移動磚塊", "磚面有雙箭頭，會在場上左右移動。"),
            ((255, 80, 40), "爆炸磚塊", "擊中後會炸掉附近磚塊，並增加分數。"),
            ((80, 220, 100), "增加磚塊", "擊中後會在空位新增一塊普通磚。"),
            ((80, 160, 255), "分身球", "擊中後增加一顆球，同時最多有 10 顆。"),
            ((180, 100, 230), "修復磚塊", "擊中後會復原附近已被打掉的磚塊。"),
        ]
        guide_y = 178
        for index, (brick_color, label, description) in enumerate(brick_guide):
            row_y = guide_y + index * 44
            pygame.draw.rect(screen, (20, 29, 46), (96, row_y, 608, 38), border_radius=6)
            sample_rect = pygame.Rect(112, row_y + 7, 54, 24)
            pygame.draw.rect(screen, brick_color, sample_rect)
            if index == 0:
                pygame.draw.rect(screen, (255, 255, 255), sample_rect, 2)
            elif index == 1:
                pygame.draw.line(screen, (255, 255, 255), (sample_rect.centerx - 10, sample_rect.centery), (sample_rect.centerx + 10, sample_rect.centery), 2)
                pygame.draw.polygon(screen, (255, 255, 255), [(sample_rect.centerx - 10, sample_rect.centery), (sample_rect.centerx - 5, sample_rect.centery - 4), (sample_rect.centerx - 5, sample_rect.centery + 4)])
                pygame.draw.polygon(screen, (255, 255, 255), [(sample_rect.centerx + 10, sample_rect.centery), (sample_rect.centerx + 5, sample_rect.centery - 4), (sample_rect.centerx + 5, sample_rect.centery + 4)])
            elif index == 2:
                pygame.draw.circle(screen, (255, 255, 255), sample_rect.center, 4)
            elif index == 3:
                pygame.draw.line(screen, (255, 255, 255), (sample_rect.centerx - 5, sample_rect.centery), (sample_rect.centerx + 5, sample_rect.centery), 3)
                pygame.draw.line(screen, (255, 255, 255), (sample_rect.centerx, sample_rect.centery - 5), (sample_rect.centerx, sample_rect.centery + 5), 3)
            elif index == 4:
                pygame.draw.circle(screen, (255, 255, 255), sample_rect.center, 6)
                pygame.draw.circle(screen, brick_color, sample_rect.center, 3)
            else:
                pygame.draw.circle(screen, (255, 255, 255), sample_rect.center, 7, 2)
            label_text = home_body_font.render(label, True, (245, 248, 255))
            description_text = home_small_font.render(description, True, (185, 198, 218))
            screen.blit(label_text, (184, row_y + 4))
            screen.blit(description_text, (290, row_y + 8))

        controls = home_small_font.render("操作：滑鼠或方向鍵左右移動底板；購買瞄準後按E切換，拖曳可往任意方向發射。", True, (150, 220, 245))
        screen.blit(controls, controls.get_rect(center=(bg_x // 2, 462)))
        power_controls = home_small_font.render("功能鍵：W 大球　A 穿透　S 底板加寬　D 護盾（各3次，可至商店購買）", True, (255, 190, 115))
        screen.blit(power_controls, power_controls.get_rect(center=(bg_x // 2, 490)))
        feature_controls = home_small_font.render("商店可解鎖球色與拖曳瞄準，各50分。", True, (185, 205, 225))
        screen.blit(feature_controls, feature_controls.get_rect(center=(bg_x // 2, 516)))
        mouse_pos = pygame.mouse.get_pos()
        start_color = (45, 145, 180) if start_button.collidepoint(mouse_pos) else (35, 105, 145)
        pygame.draw.rect(screen, start_color, start_button, border_radius=10)
        pygame.draw.rect(screen, (130, 220, 255), start_button, 2, border_radius=10)
        start_text = home_body_font.render("開始遊戲", True, (255, 255, 255))
        screen.blit(start_text, start_text.get_rect(center=start_button.center))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_button.collidepoint(event.pos):
                    game_started = True

        pygame.display.update()
        continue

    current_time = pause_started_at if paused else shop_opened_at if shop_open else pygame.time.get_ticks()
    game_surface.fill((10, 16, 29))#清空畫面
    if current_time < wide_paddle_end_time:
        pad.rect.width = wide_pad_width
    else:
        pad.rect.width = pad_width

    if not paused and not shop_open and not is_aiming:
        if keyboard_controls_paddle:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                pad.rect.x -= 8
            if keys[pygame.K_RIGHT]:
                pad.rect.x += 8
        else:
            mos_x, mos_y = pygame.mouse.get_pos()#取得滑鼠位置
            pad.rect.x = mos_x - pad.rect.width // 2#設定底板位置
        pad.rect.x = max(0, min(pad.rect.x, bg_x - pad.rect.width))

    if not paused and not shop_open and not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if shop_open and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            close_shop(pygame.time.get_ticks())
        elif shop_open and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            if shop_close_button.collidepoint(mouse_pos):
                close_shop(pygame.time.get_ticks())
            else:
                for index, (power_name, _) in enumerate(shop_items):
                    if shop_buy_buttons[index].collidepoint(mouse_pos):
                        item_price = shop_item_prices[power_name]
                        if power_name in ("ball_color", "aiming") and power_name in unlocked_features:
                            shop_message = f"「{shop_items[index][1]}」已解鎖"
                        elif score >= item_price:
                            score -= item_price
                            if power_name in power_uses:
                                power_uses[power_name] += 1
                                shop_message = f"已購買「{shop_items[index][1]}」使用次數"
                            elif power_name == "life":
                                lives += 1
                                if game_over:
                                    game_over = False
                                    ball.is_moving = False
                                    ball.x = pad.rect.x + pad.rect.width // 2
                                    ball.y = pad.rect.y - ball.radius
                                    balls = [ball]
                                shop_message = "已購買 1 條生命值"
                            elif power_name == "level":
                                advance_level(pygame.time.get_ticks())
                                shop_message = f"已通關，進入第 {level} 關"
                            elif power_name in ("ball_color", "aiming"):
                                unlocked_features.add(power_name)
                                shop_message = f"已解鎖「{shop_items[index][1]}」"
                        else:
                            shop_message = "分數不足，無法購買"
                        break
        elif shop_open:
            continue
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                keyboard_controls_paddle = True
            elif not game_over and not paused:
                key_time = pygame.time.get_ticks()
                if event.key == pygame.K_w:
                    activate_power("big_ball", key_time)
                elif event.key == pygame.K_a:
                    activate_power("piercing", key_time)
                elif event.key == pygame.K_s:
                    activate_power("wide_paddle", key_time)
                elif event.key == pygame.K_d:
                    activate_power("invincible", key_time)
                elif event.key == pygame.K_e and "aiming" in unlocked_features:
                    aim_mode_enabled = not aim_mode_enabled
                    if not aim_mode_enabled:
                        is_aiming = False
                        aim_start_pos = None
                        aim_current_pos = None
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            keyboard_controls_paddle = False
            mouse_pos = event.pos
            if shop_button.collidepoint(mouse_pos) and not paused:
                shop_open = True
                shop_opened_at = pygame.time.get_ticks()
                shop_message = ""
            elif pause_button.collidepoint(mouse_pos):
                if not game_over:
                    if paused:
                        pause_duration = pygame.time.get_ticks() - pause_started_at
                        if big_ball_end_time > pause_started_at:
                            big_ball_end_time += pause_duration
                        if piercing_end_time > pause_started_at:
                            piercing_end_time += pause_duration
                        if wide_paddle_end_time > pause_started_at:
                            wide_paddle_end_time += pause_duration
                        if invincible_end_time > pause_started_at:
                            invincible_end_time += pause_duration
                        if shake_end_time > pause_started_at:
                            shake_end_time += pause_duration
                        if level_clear_end_time > pause_started_at:
                            level_clear_end_time += pause_duration
                        paused = False
                    else:
                        paused = True
                        pause_started_at = pygame.time.get_ticks()
            elif ball_color_button.collidepoint(mouse_pos):
                if "ball_color" in unlocked_features:
                    ball_color_index = (ball_color_index + 1) % len(ball_colors)
                    ball_color = ball_colors[ball_color_index]
                    for current_ball in balls:
                        current_ball.color = ball_color
                else:
                    shop_open = True
                    shop_opened_at = pygame.time.get_ticks()
                    shop_message = "球色尚未解鎖，請至商店購買"
            elif not game_over and not paused and big_ball_button.collidepoint(mouse_pos):
                activate_power("big_ball", pygame.time.get_ticks())
            elif not game_over and not paused and piercing_button.collidepoint(mouse_pos):
                activate_power("piercing", pygame.time.get_ticks())
            elif not game_over and not paused and wide_paddle_button.collidepoint(mouse_pos):
                activate_power("wide_paddle", pygame.time.get_ticks())
            elif not game_over and not paused and invincible_button.collidepoint(mouse_pos):
                activate_power("invincible", pygame.time.get_ticks())
            elif not game_over and not paused:
                if mouse_pos[1] < bg_y and any(not current_ball.is_moving for current_ball in balls):
                    if aim_mode_enabled and "aiming" in unlocked_features:
                        is_aiming = True
                        aim_start_pos = mouse_pos
                        aim_current_pos = mouse_pos
                    else:
                        for current_ball in balls:
                            if not current_ball.is_moving:
                                current_ball.speed_x = random.choice((-5, 5))
                                current_ball.speed_y = -5
                                current_ball.is_moving = True
        elif event.type == pygame.MOUSEMOTION:
            keyboard_controls_paddle = False
            if is_aiming and "aiming" in unlocked_features:
                aim_current_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and is_aiming:
            aim_dx = aim_current_pos[0] - aim_start_pos[0]
            aim_dy = aim_current_pos[1] - aim_start_pos[1]
            direction_x = aim_dx
            direction_y = aim_dy
            if direction_x == 0 and direction_y == 0:
                direction_y = -1
            direction_length = math.hypot(direction_x, direction_y)
            ball_speed = math.hypot(5, 5)
            for current_ball in balls:
                if not current_ball.is_moving:
                    current_ball.speed_x = direction_x / direction_length * ball_speed
                    current_ball.speed_y = direction_y / direction_length * ball_speed
                    current_ball.is_moving = True
            is_aiming = False
            aim_start_pos = None
            aim_current_pos = None

    current_time = pause_started_at if paused else shop_opened_at if shop_open else pygame.time.get_ticks()

    if not paused and not shop_open and not game_over:
        for brick in bricks:
            if not brick.hit and brick.moving:
                brick.rect.x += brick.move_direction * 2
                if brick.rect.left <= 20 or brick.rect.right >= bg_x - 20:
                    brick.move_direction = -brick.move_direction

    lost_ball = False
    for current_ball in balls[:] if not game_over and not paused and not shop_open else []:
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

    if not paused and not shop_open and lost_ball and not any(current_ball.is_moving for current_ball in balls):
        lives -= 1
        ball.is_moving = False
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius
        balls = [ball]
        if lives <= 0:
            game_over = True

    remaining_bricks = sum(not brick.hit for brick in bricks)
    if not paused and not shop_open and not game_over and bricks and remaining_bricks <= 5:
        advance_level(pygame.time.get_ticks())

    for brick in bricks:
        brick.draw(game_surface)

    pad.draw(game_surface)
    for current_ball in balls:
        current_ball.draw(game_surface)

    if is_aiming and "aiming" in unlocked_features:
        aim_dx = aim_current_pos[0] - aim_start_pos[0]
        aim_dy = aim_current_pos[1] - aim_start_pos[1]
        direction_x = aim_dx
        direction_y = aim_dy
        if direction_x == 0 and direction_y == 0:
            direction_y = -1
        direction_length = math.hypot(direction_x, direction_y)
        arrow_length = 85
        arrow_end = (
            int(ball.x + direction_x / direction_length * arrow_length),
            int(ball.y + direction_y / direction_length * arrow_length),
        )
        pygame.draw.line(game_surface, (80, 220, 255), (ball.x, ball.y), arrow_end, 3)
        arrow_angle = math.atan2(direction_y, direction_x)
        arrow_head_length = 12
        for offset in (-math.pi / 6, math.pi / 6):
            arrow_point = (
                int(arrow_end[0] - arrow_head_length * math.cos(arrow_angle + offset)),
                int(arrow_end[1] - arrow_head_length * math.sin(arrow_angle + offset)),
            )
            pygame.draw.line(game_surface, (80, 220, 255), arrow_end, arrow_point, 3)
        aim_text = score_font.render("拖曳瞄準，放開發射", True, (150, 220, 245))
        game_surface.blit(aim_text, aim_text.get_rect(center=(bg_x // 2, 70)))

    pygame.draw.rect(game_surface, (20, 30, 49), (0, bg_y, bg_x, window_height - bg_y))
    score_text = info_font.render(f"分數 {score}", True, (115, 220, 255))
    game_surface.blit(score_text, (20, 8))
    level_text = info_font.render(f"關卡 {level}", True, (205, 175, 255))
    game_surface.blit(level_text, level_text.get_rect(center=(bg_x // 2, 22)))
    lives_text = info_font.render(f"生命 {lives}", True, (255, 190, 115))
    game_surface.blit(lives_text, lives_text.get_rect(topright=(bg_x - 20, 8)))

    big_ball_active = current_time < big_ball_end_time
    big_ball_label = f"大球啟動 {power_uses['big_ball']}" if big_ball_active else f"大球 {power_uses['big_ball']}"
    big_ball_color = (40, 150, 70) if big_ball_active else (70, 70, 100)
    draw_button(game_surface, big_ball_button, big_ball_label, big_ball_color)

    piercing_active = current_time < piercing_end_time
    piercing_label = f"穿透啟動 {power_uses['piercing']}" if piercing_active else f"穿透 {power_uses['piercing']}"
    piercing_color = (180, 90, 30) if piercing_active else (100, 65, 45)
    draw_button(game_surface, piercing_button, piercing_label, piercing_color)

    wide_paddle_active = current_time < wide_paddle_end_time
    wide_paddle_label = f"加寬啟動 {power_uses['wide_paddle']}" if wide_paddle_active else f"底板加寬 {power_uses['wide_paddle']}"
    wide_paddle_color = (40, 150, 70) if wide_paddle_active else (70, 70, 100)
    draw_button(game_surface, wide_paddle_button, wide_paddle_label, wide_paddle_color)

    pause_label = "繼續" if paused else "暫停"
    pause_color = (40, 120, 150) if paused else (70, 70, 100)
    draw_button(game_surface, pause_button, pause_label, pause_color)

    color_unlocked = "ball_color" in unlocked_features
    color_label = "球色" if color_unlocked else "球色鎖"
    draw_button(game_surface, ball_color_button, color_label, (70, 100, 120) if color_unlocked else (65, 65, 75))
    pygame.draw.circle(game_surface, ball_color, (ball_color_button.right - 18, ball_color_button.centery), 9)

    invincible_active = current_time < invincible_end_time
    invincible_label = f"護盾啟動 {power_uses['invincible']}" if invincible_active else f"護盾 {power_uses['invincible']}"
    invincible_color = (40, 150, 180) if invincible_active else (50, 100, 130)
    draw_button(game_surface, invincible_button, invincible_label, invincible_color)
    if current_time < invincible_end_time:
        pygame.draw.line(game_surface, (80, 220, 255), (0, bg_y - 3), (bg_x, bg_y - 3), 5)
    draw_button(game_surface, shop_button, "商店", (115, 85, 35))
    if "aiming" in unlocked_features:
        aim_mode_label = "瞄準開" if aim_mode_enabled else "瞄準關"
        aim_mode_color = (40, 150, 180) if aim_mode_enabled else (70, 70, 100)
        aim_mode_text = button_font.render(f"E {aim_mode_label}", True, (245, 248, 255))
        game_surface.blit(aim_mode_text, (bg_x - 118, 65))

    if game_over:
        game_over_text = score_font.render("遊戲結束", True, (255, 80, 80))
        game_surface.blit(game_over_text, game_over_text.get_rect(center=(bg_x // 2, bg_y // 2)))
    elif paused:
        paused_text = score_font.render("暫停中", True, (255, 255, 255))
        game_surface.blit(paused_text, paused_text.get_rect(center=(bg_x // 2, bg_y // 2)))
    elif current_time < level_clear_end_time:
        level_clear_text = level_clear_font.render("過關！", True, (255, 225, 100))
        game_surface.blit(level_clear_text, level_clear_text.get_rect(center=(bg_x // 2, bg_y // 2)))

    if shop_open:
        shop_overlay = pygame.Surface(bg_size, pygame.SRCALPHA)
        shop_overlay.fill((0, 0, 0, 175))
        game_surface.blit(shop_overlay, (0, 0))
        pygame.draw.rect(game_surface, (25, 36, 56), shop_panel, border_radius=12)
        pygame.draw.rect(game_surface, (115, 220, 255), shop_panel, 2, border_radius=12)
        shop_title = home_title_font.render("功能商店", True, (255, 225, 130))
        game_surface.blit(shop_title, shop_title.get_rect(center=(shop_panel.centerx, shop_panel.y + 42)))
        balance_text = home_body_font.render(f"目前分數：{score}", True, (220, 230, 245))
        game_surface.blit(balance_text, balance_text.get_rect(center=(shop_panel.centerx, shop_panel.y + 78)))
        price_text = home_small_font.render("技能/通關500分　生命100分　球色/瞄準50分", True, (185, 205, 225))
        game_surface.blit(price_text, price_text.get_rect(center=(shop_panel.centerx, shop_panel.y + 99)))
        pygame.draw.rect(game_surface, (120, 55, 55), shop_close_button, border_radius=5)
        close_text = home_body_font.render("×", True, (255, 255, 255))
        game_surface.blit(close_text, close_text.get_rect(center=shop_close_button.center))
        for index, (power_name, item_label) in enumerate(shop_items):
            row_y = shop_buy_buttons[index].y - 4
            pygame.draw.rect(game_surface, (35, 49, 72), (shop_panel.x + 22, row_y, shop_panel.width - 44, 42), border_radius=6)
            item_text = home_body_font.render(item_label, True, (245, 248, 255))
            if power_name in power_uses:
                item_status = f"持有：{power_uses[power_name]} 次"
            elif power_name == "life":
                item_status = f"目前：{lives} 條"
            elif power_name == "level":
                item_status = f"前往第 {level + 1} 關"
            else:
                item_status = "已解鎖" if power_name in unlocked_features else "尚未解鎖"
            count_text = home_small_font.render(item_status, True, (185, 205, 225))
            game_surface.blit(item_text, (shop_panel.x + 40, row_y + 3))
            game_surface.blit(count_text, (shop_panel.x + 150, row_y + 9))
            item_price = shop_item_prices[power_name]
            if power_name in ("ball_color", "aiming") and power_name in unlocked_features:
                button_label = "已解鎖"
                button_color = (65, 75, 85)
            else:
                button_label = f"購買 {item_price}分"
                button_color = (45, 115, 85)
            draw_button(game_surface, shop_buy_buttons[index], button_label, button_color)
        if shop_message:
            message_text = home_small_font.render(shop_message, True, (255, 190, 115))
            game_surface.blit(message_text, message_text.get_rect(center=(shop_panel.centerx, shop_panel.bottom - 18)))

    screen.fill((0, 0, 0))
    shake_x = 0
    shake_y = 0
    if pygame.time.get_ticks() < shake_end_time:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)
    screen.blit(game_surface, (shake_x, shake_y))
    pygame.display.update()