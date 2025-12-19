import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS - Войти")

WHITE = (255, 255, 255)
LIGHT_BLUE = (232, 249, 255)
BLUE = (14, 137, 185)
GRAY = (170, 170, 170)
ACTIVE_COLOR = (200, 230, 255) 
 
title_font = pygame.font.SysFont("notable", 160)
font_title = pygame.font.SysFont(None, 150)
font_input = pygame.font.SysFont(None, 40)
font_button = pygame.font.SysFont(None, 50)


background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


login = ""
password = ""

active_login = False
active_password = False

cursor_visible = True
cursor_timer = 0

rect_login = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 40, 600, 60)
rect_password = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 50, 600, 60)
rect_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 60)

clock = pygame.time.Clock()

running = True
while running:
    dt = clock.tick(60)
    cursor_timer += dt
    if cursor_timer >= 500:
        cursor_visible = not cursor_visible
        cursor_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            active_login = rect_login.collidepoint(event.pos)
            active_password = rect_password.collidepoint(event.pos)

            if rect_button.collidepoint(event.pos):
                print("Вход:", login, password)
                running = False

        if event.type == pygame.KEYDOWN:
            if active_login:
                if event.key == pygame.K_BACKSPACE:
                    login = login[:-1]
                else:
                    login += event.unicode

            elif active_password:
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode

    screen.blit(background, (0, 0))

    block_width, block_height = 800, 600
    block_x = WIDTH // 2 - block_width // 2
    block_y = HEIGHT // 2 - block_height // 2
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), 
                     (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)

    color_login = ACTIVE_COLOR if active_login else WHITE
    pygame.draw.rect(screen, color_login, rect_login, border_radius=25)

    if login == "":
        text_surface = font_input.render("введите логин", True, GRAY)
    else:
        text_surface = font_input.render(login, True, (0, 0, 0))

    screen.blit(text_surface, (rect_login.x + 20, rect_login.y + 15))

    if active_login and cursor_visible:
        cursor_x = rect_login.x + 20 + text_surface.get_width() + 3
        cursor_y = rect_login.y + 15
        pygame.draw.rect(screen, (0, 0, 0), (cursor_x, cursor_y, 3, 30))

    color_pass = ACTIVE_COLOR if active_password else WHITE
    pygame.draw.rect(screen, color_pass, rect_password, border_radius=25)

    if password == "":
        text_surface = font_input.render("введите пароль", True, GRAY)
    else:
        hidden = "*" * len(password)
        text_surface = font_input.render(hidden, True, (0, 0, 0))

    screen.blit(text_surface, (rect_password.x + 20, rect_password.y + 15))

    if active_password and cursor_visible:
        cursor_x = rect_password.x + 20 + text_surface.get_width() + 3
        cursor_y = rect_password.y + 15
        pygame.draw.rect(screen, (0, 0, 0), (cursor_x, cursor_y, 3, 30))

    pygame.draw.rect(screen, WHITE, rect_button, border_radius=25)
    btn = font_button.render("Войти", True, BLUE)
    screen.blit(btn, btn.get_rect(center=rect_button.center))

    pygame.display.update()

pygame.quit()
sys.exit()