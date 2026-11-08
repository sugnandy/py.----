######################載入套件######################
import pygame
import sys
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
platform_x = (bg_x - platform_w) // 2
platform_y = bg_y - platform_h - 10
platform = Platform(platform_x, platform_y, platform_w, platform_h, (255, 255, 255))




######################主程式######################
while True:
    FPS.tick(60) #設定遊戲迴圈執行速度為每秒60次
    screen.fill((0, 0, 0)) #用黑色填滿整個遊戲視窗

    keys = pygame.key.get_pressed() #取得所有按鍵的狀態

    if keys[pygame.K_LEFT]: #當按下左方向鍵時
        player.move(-1, bg_x) #向左移動玩家物件
    if keys[pygame.K_RIGHT]: #當按下右方向鍵時
        player.move(1, bg_x) #向右移動玩家物件

    for event in pygame.event.get():
        if event.type == pygame.QUIT: #當使用者按下關閉視窗按鈕時
            sys.exit()

    platform.draw(screen) #繪製平台物件
    player.draw(screen) #繪製玩家物件
    pygame.display.update() #更新整個遊戲視窗
