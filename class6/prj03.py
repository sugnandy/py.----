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
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

    def check_platform_collision(self, platforms):
        """
        檢查玩家物件是否與平台物件碰撞
        :param platform: 平台物件
        """
        if self.velocity_y > 0:
            cheak_points = max(1, int(abs(self.velocity_y)/5))  # 計算檢查點的數量，至少為1
            step_y = self.velocity_y / cheak_points  # 計算每個檢查點的垂直位移
            for platform in platforms:
                for i in range(cheak_points):
                    test_rect = self.rect.copy()
                    test_rect.y += i * step_y  # 計算檢查點的y座標
                if (
                    test_rect.bottom >= platform.rect.top
                    and test_rect.bottom <= platform.rect.bottom
                    and test_rect.right >= platform.rect.left
                    and test_rect.left <= platform.rect.right
                ):
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = self.jumping_power
                    self.on_platform = True
                    return True
        return False

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

    def draw(self, display_area):
        """
        在遊戲視窗上繪製平台物件
        :param screen: 遊戲視窗
        """
        pygame.draw.rect(display_area, self.color, self.rect)
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

######################自訂函式######################
# 更新玩家物件的位置，並檢查是否與平台物件碰撞
def update_camera():
    """
    更新攝影機位置，讓玩家物件保持在視窗中間
    - 當玩家物件的y座標小於視窗高度的一半時，將攝影機向下移動，讓玩家物件保持在視窗中間
    - 當玩家物件的y座標大於視窗高度的一半時，將攝影機向上移動，讓玩家物件保持在視窗中間
    """
    screen_middle = bg_y // 2
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle

        for platform in platforms:
            platform.rect.y += camera_move

        y_min = bg_y
        for platform in platforms:
            if platform.rect.top > bg_y:
                platforms.remove(platform)

            if platform.rect.top < y_min:
                y_min = platform.rect.top
    
        # 隨機生成新的平台，並將其添加到平台列表中
        if len(platforms) < platform_count:
            x = random.randint(0, bg_x - platform_w)
            y = y_min - 60
            platform = Platform(x, y, platform_w, platform_h, (255, 255, 255))
            platforms.append(platform)






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

    ## 讓玩家物件受到重力影響
    player.apple_gravity()
    player.check_platform_collision(platforms) #檢查玩家物件是否與平台物件碰撞

        
    for event in pygame.event.get():
        if event.type == pygame.QUIT: #當使用者按下關閉視窗按鈕時
            sys.exit()

    for platform in platforms:
        platform.draw(screen) #繪製平台物件

    player.draw(screen) #繪製玩家物件
    pygame.display.update() #更新整個遊戲視窗
