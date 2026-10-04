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
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad):
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
            self.is_moving = False

        # 檢查球物件與磚塊物件是否有碰撞
        if(
            self.y + self.radius >= pad.rect.y
            and self.y - self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        for brick in bricks:
            if not brick.hit:
                # 檢查球物件與磚塊物件是否有碰撞
                # 如果有碰撞就設定磚塊物件為已碰撞
                dx = abs(self.x - (brick.rect.x + brick.rect.width / 2))
                dy = abs(self.y - (brick.rect.y + brick.rect.height / 2))

                if dx <= (self.radius + brick.rect.width / 2) and dy <= (self.radius + brick.rect.height / 2):
                    brick.hit = True

                    if self.x < brick.rect.x or self.x > brick.rect.x + brick.rect.width:
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y


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
ball_radius = 10
ball_color = (255, 215, 0)
ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)

######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))#清空畫面
    mos_x, mos_y = pygame.mouse.get_pos()#取得滑鼠位置
    pad.rect.x = mos_x - pad.rect.width // 2#設定底板位置
    if pad.rect.x < 0:
        pad.rect.x = 0

    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width

    if not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius
    else:
        ball.move()
        ball.check_collision(bg_x, bg_y, bricks, pad)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not ball.is_moving:
                ball.is_moving = True

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)
    ball.draw(screen)

    pygame.display.update()