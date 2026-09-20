######################載入套件/ import packages######################
import random
import pygame
import sys


######################物件類別/ object class######################
class Brick:
    def __init__(self, x, y, width, height, color):
        """
        初始化磚塊物件/initialize brick object
        x,y: 磚塊的位置/position of brick
        width,height: 磚塊的寬度/width and height of brick
        color: 磚塊的顏色/color of brick
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False

    def draw(self, display_area):
        """
        繪製磚塊物件/draw brick object
        display_area: 繪製區域/area to draw
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)

######################定義函式區/ define functions######################

######################初始化設定/ initialize settings######################
pygame.init()

######################載入圖片/ load images######################

######################遊戲視窗設定/ game window settings######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("打磚塊遊戲")
screen = pygame.display.set_mode(bg_size)

######################磚塊設定/ brick settings######################
bricks_row =9
bricks_col = 11
brick_w = 58
brick_h = 16
bricks_gap =2
bricks = []
for col in range(bricks_col):
    for row in range(bricks_row):
        x = col * (brick_w + bricks_gap) + 70
        y = row * (brick_h + bricks_gap) + 60
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        brick = Brick(x, y, brick_w, brick_h, color)
        bricks.append(brick)

######################顯示文字設定/ text display settings######################

######################底板設定/ paddle settings######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定/ ball settings######################

######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    screen.fill((0, 0, 0))#清空畫面
    mos_x, mos_y = pygame.mouse.get_pos()#取得滑鼠位置
    pad.rect.x = mos_x - pad.rect.width // 2#設定底板位置
    if pad.rect.x < 0:
        pad.rect.x = 0

    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)

    pygame.display.update()