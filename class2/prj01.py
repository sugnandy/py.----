######################匯入模組######################
import pygame
import sys
######################初始化######################
pygame.init() # 啟動pygame
width = 640 #設定視窗寬度
height = 320 #設定視窗高度

######################建立視窗及物件######################
#建立視窗
screen = pygame.display.set_mode((width, height))
#設定視窗名稱
pygame.display.set_caption("My Game")

######################建立畫布######################
#建立畫布
bg = pygame.Surface((width, height))
#畫布顏色
bg.fill((255, 255, 0))

######################繪製圓形######################
#畫圓形,(畫布, 顏色, (圓心x, 圓心y), 半徑)
pygame.draw.circle(bg, (0, 0, 255), (200,100), 30,0)
pygame.draw.circle(bg, (0, 0, 255), (400,100), 30,0)

# 畫矩形,(畫布, 顏色, (左上角x, 左上角y), (寬度, 高度))
pygame.draw.rect(bg, (0, 255, 0), [270, 130,60,40],5)

#畫橢圓,(畫布, 顏色, (左上角x, 左上角y), (寬度, 高度))
pygame.draw.ellipse(bg, (255, 0, 0), [130, 160, 60, 35], 5)
pygame.draw.ellipse(bg, (255, 0, 0), [400, 160, 60, 35], 5)

# 畫線 (畫布, 顏色, 起點, 終點, 線寬)
pygame.draw.line(bg, (255, 0, 255), (280, 220), (320, 220), 3)

######################循環偵測######################
while True:
    x, y = pygame.mouse.get_pos() #取得滑鼠座標
    for event in pygame.event.get():
        if event.type == pygame.QUIT:#如果按下[x]就退出
            sys.exit() #結束程式

        if event.type == pygame.MOUSEBUTTONDOWN:
            print("click!!")
            print("mouse pos: {x}, {y}")

    
    #繪製畫布
    screen.blit(bg, (0, 0))
    #更新畫面
    pygame.display.update()