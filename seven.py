import pygame
import sys
pygame.init()
WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS - Профиль")
WHITE = (255, 255, 255)
LIGHT_BLUE = (232, 249, 255)
BLUE = (14, 137, 185)
RED = (179, 32, 33)
BLACK = (0, 0, 0)
YELLOW = (232, 230, 116)
GREEN = (101, 189, 100)
title_font = pygame.font.SysFont("Advent Pro", 140, bold=True)
title1_font = pygame.font.SysFont("Advent Pro", 140)
button_font = pygame.font.SysFont("Advent Pro", 35,bold=True)
button1_font = pygame.font.SysFont("Advent Pro", 50 ,bold=True)
text2_font = pygame.font.SysFont("Advent Pro", 60 )
background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
pocoyo_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (70) 1 (1).png").convert_alpha()
pocoyo_img = pygame.transform.smoothscale(pocoyo_img, (200, 370))
choose_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Frame 2.png").convert_alpha()
choose_img = pygame.transform.smoothscale(choose_img, (320, 320))
avatar_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Generic avatar (1).png")
avatar_img = pygame.transform.smoothscale(avatar_img, (170, 170))



running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    mx, my = pygame.mouse.get_pos()
    
    screen.blit(background, (0, 0))
    block_width, block_height = 1350,200
    block_x = WIDTH // 2 - block_width // 2 
    block_y = HEIGHT // 2 - block_height // 2 - 175
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 140), (0, 0, block_width, block_height), border_radius=400)
    screen.blit(center_rect, (block_x, block_y))
    
    block_width, block_height = 990,420
    block_x = WIDTH // 2 - block_width // 2 -500
    block_y = HEIGHT // 2 - block_height // 2 + 170
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 140), (0, 0, block_width, block_height), border_radius=400)
    screen.blit(center_rect, (block_x, block_y))

    block_width, block_height = 900, 570
    pocoyo_x = WIDTH // 2 - block_width // 2 - 200
    pocoyo_y = HEIGHT // 2 - block_height // 2 + 180

    pocoyo_rect = pygame.Rect(pocoyo_x, pocoyo_y, block_width, block_height)

    screen.blit(pocoyo_img, (pocoyo_x - 90, pocoyo_y + 100))
    center = (WIDTH // 2, 200)
  
    title_text = title_font.render("Профиль", True, WHITE)
    title_rect = title_text.get_rect(center=center)
    screen.blit(title_text, title_rect)
    screen.blit(avatar_img, (WIDTH//2 - 650, HEIGHT//2 -260))
    block_width, block_height = 300,50 
    block_x = WIDTH // 2 - block_width // 2 + 450
    block_y = HEIGHT // 2 - block_height // 2 - 215
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (14, 137, 185), (0, 0, block_width, block_height), border_radius=60)
    screen.blit(center_rect, (block_x, block_y))
    block_width, block_height = 300,50 
    block_x = WIDTH // 2 - block_width // 2 + 450
    block_y = HEIGHT // 2 - block_height // 2 - 135
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (14, 137, 185), (0, 0, block_width, block_height), border_radius=60)
    screen.blit(center_rect, (block_x, block_y))
    text1=button_font.render("ИЗМЕНИТЬ ПАРОЛЬ",True, WHITE)
    text1_text=text1.get_rect(center=(WIDTH // 2 +450 , HEIGHT // 2 - 215))
    screen.blit(text1, text1_text)
    text2=button_font.render("ИЗМЕНИТЬ EMAIL",True, WHITE)
    text2_text=text2.get_rect(center=(WIDTH // 2 +458 , HEIGHT // 2 - 135))
    screen.blit(text2, text2_text)
    screen.blit(choose_img, (WIDTH//2 + 220, HEIGHT//2 + 10))
    text3=button1_font.render("ТОЧНОСТЬ ОТВЕТОВ",True, RED )
    text3_text=text3.get_rect(center=(WIDTH // 2 - 270 , HEIGHT // 2 - 225))
    screen.blit(text3, text3_text)
    text4=title1_font.render("100%",True, BLUE )
    text4_text=text4.get_rect(center=(WIDTH // 2 - 270 , HEIGHT // 2 - 150))
    screen.blit(text4, text4_text)
    text5=button1_font.render("УРОВЕНЬ ИГРОКА",True, RED )
    text5_text=text5.get_rect(center=(WIDTH // 2 - 340 , HEIGHT // 2 + 20))
    screen.blit(text5, text5_text)
    text6=title1_font.render("LEVEL 2 ",True, BLUE )
    text6_text=text6.get_rect(center=(WIDTH // 2 - 309 , HEIGHT // 2 + 110))
    screen.blit(text6, text6_text)
    text7=button1_font.render("ЛЮБИМЫЙ ПЕРСОНАЖ",True, RED )
    text7_text=text7.get_rect(center=(WIDTH // 2 - 300 , HEIGHT // 2 + 210))
    screen.blit(text7, text7_text)
    text8=title1_font.render("POCOYO",True, BLUE )
    text8_text=text8.get_rect(center=(WIDTH // 2 - 309 , HEIGHT // 2 + 300))
    screen.blit(text8, text8_text)
    pygame.display.flip()
pygame.quit()
sys.exit() 
    