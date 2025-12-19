import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS - Главное меню")

WHITE = (255, 255, 255)
LIGHT_BLUE = (232, 249, 255)
BLUE = (14, 137, 185)
RED = (179, 32, 33)
BLACK = (0, 0, 0)
YELLOW = (232, 230, 116)

title_font = pygame.font.SysFont("notable", 80)
button_font = pygame.font.SysFont("Advent Pro", 40)
button1_font = pygame.font.SysFont("Advent Pro", 50)

background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
back = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Disclosure Button.png")
back = pygame.transform.scale(back, (50, 50))
choose_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Frame 2.png").convert_alpha()
choose_img = pygame.transform.smoothscale(choose_img, (220, 220))
setting_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\image 5.png").convert_alpha()
setting_img = pygame.transform.smoothscale(setting_img, (60, 60))
pocoyo_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (70) 1.png").convert_alpha()
pocoyo_img = pygame.transform.smoothscale(pocoyo_img, (240, 400))
block_size = [300, 300, 300, 300]
hover_size = 350
base_size = 300
speed = 10

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    mx, my = pygame.mouse.get_pos()
        

    screen.blit(background, (0, 0))
    blocks_pos = [
        (WIDTH // 2 - 550, HEIGHT // 2),  # SQL
        (WIDTH // 2 - 200, HEIGHT // 2),  # Python
        (WIDTH // 2 + 150, HEIGHT // 2),  # C#
        (WIDTH // 2 + 500, HEIGHT // 2)   # Java
    ]
    labels = ["SQL", "Python", "C#", "JAVA"]
    for i, (bx, by) in enumerate(blocks_pos):

        size = block_size[i]
        rect = pygame.Rect(
            bx - size // 2, by - size // 2, size, size
        )
        if rect.collidepoint(mx, my):
            if size < hover_size:
                block_size[i] += speed
        else:
            if size > base_size:
                block_size[i] -= speed
        center_rect = pygame.Surface((block_size[i], block_size[i]), pygame.SRCALPHA)
        pygame.draw.rect(center_rect, (255, 255, 255, 180),
                         (0, 0, block_size[i], block_size[i]), border_radius=60)
        screen.blit(center_rect, rect)
        font_scaled = pygame.font.SysFont("notable", int(80 * (block_size[i] / base_size)))
        label = font_scaled.render(labels[i], True, BLUE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)

    screen.blit(back,  (WIDTH//2 - 680, HEIGHT//2 - 360))
    block_width, block_height = 1200,100
    block_x = WIDTH // 2 - block_width // 2  + 50
    block_y = HEIGHT // 2 - block_height // 2 - 330
    center4_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center4_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=40)
    screen.blit(center4_rect, (block_x, block_y))
    block_width, block_height = 1150,100
    block_x = WIDTH // 2 - block_width // 2  + 80
    block_y = HEIGHT // 2 - block_height // 2 - 330
    center5_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center5_rect, YELLOW, (0, 0, block_width, block_height), border_radius=40)
    screen.blit(center5_rect, (block_x, block_y))

    title = button_font.render("Выберите язык программирования, на котором хотите пройти игру... ", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2 + 50, HEIGHT // 2 - 330))
    screen.blit(title, title_rect)
    screen.blit(setting_img, (WIDTH//2  + 680, HEIGHT//2  - 365))
    screen.blit(choose_img, (WIDTH//2 - 110, HEIGHT//2 + 180))
    screen.blit(pocoyo_img, (WIDTH//2  + 500, HEIGHT//2 + 20))

    
    pygame.display.flip()
pygame.quit()
sys.exit()