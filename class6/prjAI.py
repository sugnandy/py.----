######################載入套件######################
import pygame
import sys
import random
######################物件類別######################
class Player:
    def __init__(self, x, y, width, height, color):
        """
        初始化玩家物件
        :param x: 玩家物件的x座標
        :param y: 玩家物件的y座標
        :param width: 玩家物件的寬度
        :param height: 玩家物件的高度
        :param color: 玩家物件的顏色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.speed = 5 # 玩家物件的移動速度
        self.velocity_y = 0 # 玩家物件的垂直速度
        self.jumping_power = -12 # 玩家物件的跳躍力量
        self.gravity = 0.5 # 玩家物件的重力加速度
        self.on_platform = False # 玩家物件是否在地面上
        self.previous_top = self.rect.top
        self.previous_bottom = self.rect.bottom
        self.max_jumps = 5
        self.jump_count = 0

    def draw(self, display_area):
        """
        在遊戲視窗上繪製玩家物件
        :param screen: 遊戲視窗
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        移動玩家物件
        :param direction: 移動方向，'left'表示向左移動，'right'表示向右移動
        :param bg_x: 遊戲視窗的寬度，用於限制玩家物件的移動範圍
        """
        self.rect.x += direction * self.speed
        # 限制玩家物件的移動範圍，避免超出
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0

    def apple_gravity(self):
        """
        讓玩家物件受到重力影響
        """
        self.previous_top = self.rect.top
        self.previous_bottom = self.rect.bottom
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def jump(self):
        if self.jump_count >= self.max_jumps:
            return False
        self.velocity_y = self.jumping_power
        self.jump_count += 1
        return True

    def check_platform_collision(self, platforms):
        """
        檢查玩家物件是否與平台物件碰撞
        :param platform: 平台物件
        """
        if self.velocity_y > 0:
            for platform in platforms:
                if (
                    self.previous_bottom <= platform.rect.top <= self.rect.bottom
                    and self.rect.right > platform.rect.left
                    and self.rect.left < platform.rect.right
                ):
                    self.rect.bottom = platform.rect.top
                    self.jump_count = 0
                    self.jump()
                    self.on_platform = True
                    return platform
        return None


class Platform:
    def __init__(self, x, y, width, height, color):
        """
        初始化平台物件
        :param x: 平台物件的x座標
        :param y: 平台物件的y座標
        :param width: 平台物件的寬度
        :param height: 平台物件的高度
        :param color: 平台物件的顏色
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.scored = False

    def draw(self, display_area):
        """
        在遊戲視窗上繪製平台物件
        :param screen: 遊戲視窗
        """
        pygame.draw.rect(display_area, self.color, self.rect)


class Rocket:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 22, 32)

    def draw(self, display_area):
        center_x = self.rect.centerx
        pygame.draw.polygon(
            display_area,
            (230, 50, 50),
            [(center_x, self.rect.top), (self.rect.left, self.rect.top + 10),
             (self.rect.left, self.rect.bottom - 5), (self.rect.right, self.rect.bottom - 5),
             (self.rect.right, self.rect.top + 10)],
        )
        pygame.draw.rect(
            display_area,
            (200, 220, 255),
            (center_x - 3, self.rect.top + 12, 6, 6),
        )
        pygame.draw.polygon(
            display_area,
            (255, 170, 0),
            [(self.rect.left + 5, self.rect.bottom - 5),
             (center_x, self.rect.bottom + 5),
             (self.rect.right - 5, self.rect.bottom - 5)],
        )


######################初始化設定######################
pygame.init()
FPS = pygame.time.Clock()
######################遊戲視窗設定######################
bg_x = 400
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("Dood Jump")
screen = pygame.display.set_mode(bg_size)
######################主角設定######################
player_w = 30
player_h = 30
player_x = (bg_x - player_w) // 2
player_y = bg_y - player_h - 50
# 創建玩家物件
player = Player(player_x, player_y, player_w, player_h, (0, 255, 0))

######################平台設定######################
platform_w = 60
platform_h = 10
platforms = []
platform_x = (bg_x - platform_w) // 2
platform_y = bg_y - platform_h - 10
platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))
platforms.append(platform)

# 隨機生成其他平台
platform_count = random.randint(8, 15)+10  # 隨機生成平台數量
for i in range(platform_count):
    x = random.randint(0, bg_x - platform_w)
    y = (bg_y - 100) - (i * 60)  # 平台間隔為60像素
    platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
    platforms.append(platform)

rocket_count = 3
rockets = []


def maintain_rockets():
    rockets[:] = [rocket for rocket in rockets if rocket.rect.top <= bg_y]
    while len(rockets) < rocket_count:
        available_platforms = [
            platform for platform in platforms
            if (
                32 <= platform.rect.top <= bg_y
                and not player.rect.colliderect(
                    pygame.Rect(platform.rect.centerx - 11, platform.rect.top - 32, 22, 32)
                )
                and all(
                    not rocket.rect.colliderect(
                        pygame.Rect(
                            platform.rect.centerx - 11,
                            platform.rect.top - 32,
                            22,
                            32,
                        )
                    )
                    for rocket in rockets
                )
            )
        ]
        if not available_platforms:
            break
        rocket_platform = random.choice(available_platforms)
        rockets.append(
            Rocket(
                rocket_platform.rect.centerx - 11,
                rocket_platform.rect.top - 32,
            )
        )


maintain_rockets()
score = 0
level = 1
level_jumps = 0
level_goal = 5
level_up_until = 0
score_font = pygame.font.Font(None, 32)
level_up_font = pygame.font.Font(None, 64)

######################自訂函式######################
# 更新玩家物件的位置，並檢查是否與平台物件碰撞
def update_camera():
    """
    玩家上升時更新攝影機位置；下落時固定畫面，讓玩家落回畫面內的平台
    """
    screen_middle = bg_y // 2
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        for platform in platforms:
            platform.rect.y += camera_move

        for rocket in rockets:
            rocket.rect.y += camera_move

        platforms[:] = [platform for platform in platforms if platform.rect.top <= bg_y]
        while len(platforms) < platform_count:
            y_min = min((platform.rect.top for platform in platforms), default=0)
            x = random.randint(0, bg_x - platform_w)
            platforms.append(
                Platform(x, y_min - 60, platform_w, platform_h, (255, 255, 255))
            )
        maintain_rockets()
######################主程式######################
while True:
    FPS.tick(60) #設定遊戲迴圈執行速度為每秒60次
    screen.fill((0, 0, 0)) #用黑色填滿整個遊戲視窗

    update_camera() #更新攝影機位置，讓玩家物件保持在視窗中間

    keys = pygame.key.get_pressed() #取得所有按鍵的狀態

    if keys[pygame.K_LEFT]: #當按下左方向鍵時
        player.move(-1, bg_x) #向左移動玩家物件
    if keys[pygame.K_RIGHT]: #當按下右方向鍵時
        player.move(1, bg_x) #向右移動玩家物件

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #當使用者按下關閉視窗按鈕時
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            player.jump()

    ## 讓玩家物件受到重力影響
    player.apple_gravity()
    if player.velocity_y < 0:
        for platform in platforms:
            if (
                not platform.scored
                and player.previous_top >= platform.rect.bottom
                and player.rect.top <= platform.rect.bottom
                and player.rect.right > platform.rect.left
                and player.rect.left < platform.rect.right
            ):
                platform.scored = True
                score += 1
                level_jumps += 1
                if level_jumps >= level_goal:
                    level += 1
                    level_jumps = 0
                    level_goal = level * 5
                    level_up_until = pygame.time.get_ticks() + 1500

    player.check_platform_collision(platforms)

    for rocket in rockets[:]:
        if player.rect.colliderect(rocket.rect):
            rockets.remove(rocket)
            player.velocity_y = -20
            score += 5
    maintain_rockets()

    for platform in platforms:
        platform.draw(screen) #繪製平台物件

    for rocket in rockets:
        rocket.draw(screen)

    player.draw(screen) #繪製玩家物件
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (10, 10))
    level_text = score_font.render(
        f"Level: {level}  Jumps: {level_jumps}/{level_goal}",
        True,
        (255, 255, 255),
    )
    screen.blit(level_text, (10, 42))
    jump_text = score_font.render(
        f"Air Jumps: {player.jump_count}/{player.max_jumps}",
        True,
        (180, 220, 255),
    )
    screen.blit(jump_text, (10, 74))
    level_up_remaining = level_up_until - pygame.time.get_ticks()
    if level_up_remaining > 0:
        effect_progress = 1 - level_up_remaining / 1500
        effect_radius = int(20 + effect_progress * 100)
        effect_center = (bg_x // 2, bg_y // 2)
        pygame.draw.circle(screen, (255, 215, 0), effect_center, effect_radius, 4)
        level_up_text = level_up_font.render("LEVEL UP!", True, (255, 255, 0))
        screen.blit(level_up_text, level_up_text.get_rect(center=(bg_x // 2, bg_y // 2)))
    pygame.display.update() #更新整個遊戲視窗
