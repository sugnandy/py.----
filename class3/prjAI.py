######################載入套件/ import packages######################
import random
import sys

import pygame


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
        pygame.draw.circle(display_area, self.color, (self.x, self.y), self.radius)

    def move(self):
        """
        移動球物件/move ball object
        """
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def launch(self, paddle):
        """從底板上發射球/launch ball from the paddle."""
        self.is_moving = True
        self.x = paddle.rect.x + paddle.rect.width // 2
        self.y = paddle.rect.y - self.radius
        self.speed_x = random.choice((-1, 1)) * 5
        self.speed_y = -5

    def reset_position(self, paddle):
        """把球放回底板上/return ball to the paddle."""
        self.is_moving = False
        self.x = paddle.rect.x + paddle.rect.width // 2
        self.y = paddle.rect.y - self.radius

    def check_collision(self, bg_x, bg_y, bricks, pad):
        """
        檢查球物件與磚塊與底板是否有碰撞/check collision between ball and wall, bricks, and paddle
        bg_x, bg_y: 背景的寬度/width of background
        bricks: 磚塊物件的陣列/array of brick objects
        pad: 底板物件/paddle object
        """
        if self.x - self.radius <= 0 or self.x + self.radius >= bg_x:
            self.speed_x *= -1

        if self.y - self.radius <= 0:
            self.speed_y *= -1

        if self.y + self.radius >= bg_y:
            self.is_moving = False
            return False

        if (
            self.y + self.radius >= pad.rect.y
            and self.y - self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)
            impact = (self.x - (pad.rect.x + pad.rect.width / 2)) / (pad.rect.width / 2)
            self.speed_x = impact * 7

        for brick in bricks:
            if brick.hit:
                continue

            nearest_x = max(brick.rect.left, min(self.x, brick.rect.right))
            nearest_y = max(brick.rect.top, min(self.y, brick.rect.bottom))
            dx = self.x - nearest_x
            dy = self.y - nearest_y
            distance_sq = dx * dx + dy * dy

            if distance_sq <= self.radius * self.radius:
                brick.hit = True

                if self.x < brick.rect.left or self.x > brick.rect.right:
                    self.speed_x *= -1
                elif self.y < brick.rect.top or self.y > brick.rect.bottom:
                    self.speed_y *= -1
                else:
                    self.speed_x *= -1
                    self.speed_y *= -1
                return True

        return True


######################定義函式區/ define functions######################
def build_bricks():
    """建立磚塊陣列/build brick array."""
    bricks = []
    bricks_row = 9
    bricks_col = 11
    brick_w = 58
    brick_h = 16
    bricks_gap = 2

    for col in range(bricks_col):
        for row in range(bricks_row):
            x = col * (brick_w + bricks_gap) + 70
            y = row * (brick_h + bricks_gap) + 60
            color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
            bricks.append(Brick(x, y, brick_w, brick_h, color))
    return bricks


def handle_ai_paddle(pad, ball, bg_x):
    """AI 控制底板跟隨球的位置/AI paddle tracks the ball."""
    target_x = ball.x - pad.rect.width / 2
    if target_x < pad.rect.x:
        pad.rect.x -= 7
    elif target_x > pad.rect.x:
        pad.rect.x += 7

    if pad.rect.x < 0:
        pad.rect.x = 0
    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width


def draw_text(screen, message, x, y, color=(255, 255, 255), size=28):
    """顯示文字/draw text."""
    font = pygame.font.SysFont(None, size)
    text = font.render(message, True, color)
    screen.blit(text, (x, y))


def main():
    ######################初始化設定/ initialize settings######################
    pygame.init()
    FPS = pygame.time.Clock()

    ######################遊戲視窗設定/ game window settings######################
    bg_x = 800
    bg_y = 600
    bg_size = (bg_x, bg_y)
    pygame.display.set_caption("打磚塊遊戲")
    screen = pygame.display.set_mode(bg_size)

    ######################磚塊設定/ brick settings######################
    bricks = build_bricks()

    ######################底板設定/ paddle settings######################
    pad = Brick(0, bg_y - 48, 58, 16, (255, 255, 255))
    pad.rect.x = bg_x // 2 - pad.rect.width // 2

    ######################球設定/ ball settings######################
    ball_radius = 10
    ball_color = (255, 215, 0)
    ball = Ball(pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color)

    ######################主程式/ main program######################
    game_over = False
    game_clear = False

    while True:
        FPS.tick(60)
        screen.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and not ball.is_moving and not game_over and not game_clear:
                ball.launch(pad)

        if not game_over and not game_clear:
            handle_ai_paddle(pad, ball, bg_x)

            if not ball.is_moving:
                ball.reset_position(pad)
            else:
                ball.move()
                if not ball.check_collision(bg_x, bg_y, bricks, pad):
                    game_over = True

            if all(brick.hit for brick in bricks):
                game_clear = True

        for brick in bricks:
            brick.draw(screen)

        pad.draw(screen)
        ball.draw(screen)

        if game_over:
            draw_text(screen, "Game Over", 330, 250, size=48)
            draw_text(screen, "Click to restart", 290, 320, size=28)
            if pygame.mouse.get_pressed()[0]:
                bricks = build_bricks()
                pad.rect.x = bg_x // 2 - pad.rect.width // 2
                ball.reset_position(pad)
                game_over = False
                game_clear = False
        elif game_clear:
            draw_text(screen, "You Win!", 330, 250, size=48)
            draw_text(screen, "Click to play again", 260, 320, size=28)
            if pygame.mouse.get_pressed()[0]:
                bricks = build_bricks()
                pad.rect.x = bg_x // 2 - pad.rect.width // 2
                ball.reset_position(pad)
                game_over = False
                game_clear = False

        pygame.display.update()


if __name__ == "__main__":
    main()