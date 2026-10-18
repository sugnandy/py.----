######################載入套件/ import packages######################
import random
import pygame
import sys


######################物件類別/ object class######################
class Brick:
    def __init__(self, x, y, width, height, color, brick_type="normal"):
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

    def draw(self, display_area):
        """
        繪製磚塊物件/draw brick object
        display_area: 繪製區域/area to draw
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
            center_x = self.rect.centerx
            center_y = self.rect.centery

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
                    return brick

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

    if brick_type == "explosive":
        color = (255, 80, 40)
    elif brick_type == "add_bricks":
        color = (80, 220, 100)
    elif brick_type == "extra_ball":
        color = (80, 160, 255)
    else:
        color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    return Brick(x, y, brick_w, brick_h, color, brick_type)


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
            y = row * (brick_h + bricks_gap) + 60
            level_bricks.append(create_brick(x, y))

    return level_bricks


level = 1
bricks = create_bricks(level)


def add_bricks(bricks, amount):
    for _ in range(amount):
        empty_positions = []
        for col in range(bricks_col):
            for row in range(bricks_row):
                x = col * (brick_w + bricks_gap) + 70
                y = row * (brick_h + bricks_gap) + 60
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
        bricks.append(Brick(x, y, brick_w, brick_h, color))

######################顯示文字設定/ text display settings######################

######################底板設定/ paddle settings######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (255, 255, 255))
######################球設定/ ball settings######################
ball_radius = 10
ball_color = (255, 215, 0)
ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)
balls = [ball]
score = 0
shake_end_time = 0

######################遊戲結束設定/ game over settings######################

######################主程式/ main program######################
while True:
    FPS.tick(60)
    game_surface.fill((0, 0, 0))#清空畫面
    mos_x, mos_y = pygame.mouse.get_pos()#取得滑鼠位置
    pad.rect.x = mos_x - pad.rect.width // 2#設定底板位置
    if pad.rect.x < 0:
        pad.rect.x = 0

    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width

    if not ball.is_moving:
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball.radius

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            for current_ball in balls:
                if not current_ball.is_moving:
                    current_ball.is_moving = True

    for current_ball in balls[:]:
        if current_ball.is_moving:
            current_ball.move()
            hit_brick = current_ball.check_collision(bg_x, bg_y, bricks, pad)
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
                    add_bricks(bricks, random.randint(3, 5))
                elif hit_brick.brick_type == "extra_ball":
                    new_ball = Ball(current_ball.x, current_ball.y, ball_radius, ball_color)
                    new_ball.speed_x = -current_ball.speed_x
                    new_ball.speed_y = current_ball.speed_y
                    new_ball.is_moving = True
                    balls.append(new_ball)

    balls = [current_ball for current_ball in balls if current_ball is ball or current_ball.is_moving]

    if bricks and all(brick.hit for brick in bricks):
        level += 1
        bricks = create_bricks(level)

    for brick in bricks:
        brick.draw(game_surface)

    pad.draw(game_surface)
    for current_ball in balls:
        current_ball.draw(game_surface)

    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))
    game_surface.blit(score_text, (10, 10))
    level_text = score_font.render(f"Level: {level}", True, (255, 255, 255))
    game_surface.blit(level_text, (bg_x - 110, 10))

    screen.fill((0, 0, 0))
    shake_x = 0
    shake_y = 0
    if pygame.time.get_ticks() < shake_end_time:
        shake_x = random.randint(-5, 5)
        shake_y = random.randint(-5, 5)
    screen.blit(game_surface, (shake_x, shake_y))
    pygame.display.update()