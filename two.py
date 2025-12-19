import pygame
import sys


pygame.init()

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS - Регистрация")

WHITE = (255, 255, 255)
LIGHT_BLUE = (232, 249, 255)
BLUE = (14, 137, 185)
GRAY = (170, 170, 170)
RED = (179, 32, 33)
ACTIVE_COLOR = (200, 230, 255) 
 
title_font = pygame.font.SysFont("notable", 160)
font_title = pygame.font.SysFont(None, 150)
font_input = pygame.font.SysFont(None, 40)
font_button = pygame.font.SysFont(None, 50)
font_xx=pygame.font.SysFont(None, 30)

background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))


username = ""
email = ""
password = ""
again_password = ""


active_username = False
active_password = False
active_email = False
active_again_password = False

cursor_visible = True
cursor_timer = 0
scroll_offset_day = 0
scroll_offset_month = 0
scroll_offset_year = 0
line_height = 30

days=[str(i) for i in range(1,32)]
months=["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
months_numeric = [str(i) for i in range(1, 13)]
years = [str(i) for i in range(1900, 2025)]
selected_day = ""
selected_month = ""
selected_year = ""
drop_day = False
drop_month = False
drop_year = False
rect_username = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 120, 600, 60)
rect_email = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 50, 600, 60)
rect_password = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 20, 600, 60)
rect_again_password = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 90, 600, 60)
left_block_x = WIDTH//2  - 100
rect_day = pygame.Rect(left_block_x +120+20+5+20, HEIGHT//2 + 190, 70, 40)
rect_month = pygame.Rect(left_block_x + 120 + 20 + 90 + 20, HEIGHT//2 + 190, 70, 40)
rect_year = pygame.Rect(left_block_x + 120 + 20 + 175 + 20, HEIGHT//2 + 190, 70, 40)
day_dropdown_rect = pygame.Rect(rect_day.x, rect_day.y + 45, 120, 160)
month_dropdown_rect = pygame.Rect(rect_month.x, rect_month.y + 45, 120, 220)
year_dropdown_rect = pygame.Rect(rect_year.x, rect_year.y + 45, 120, 220)
checked = False
rect_checkbox = pygame.Rect(WIDTH//2 - 290, HEIGHT//2 + 230, 20, 20)
font_checkbox = pygame.font.SysFont(None, 25)
checkbox_text = "Я согласен с условиями использования"
rect_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 260, 300, 60)
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
        if event.type == pygame.MOUSEWHEEL:
            if drop_day:
                scroll_offset_day += event.y * line_height
                max_scroll=0
                min_scroll=-line_height*(len(days)-day_dropdown_rect.height//line_height)
                scroll_offset_day = max(min_scroll, min(scroll_offset_day, max_scroll))
            elif drop_month:
                scroll_offset_month += event.y * line_height
                max_scroll=0
                min_scroll=-line_height*(len(months)-month_dropdown_rect.height//line_height)
                scroll_offset_month = max(min_scroll, min(scroll_offset_month, max_scroll))
            elif drop_year:
                scroll_offset_year += event.y * line_height
                max_scroll=0
                min_scroll=-line_height*(len(years)-year_dropdown_rect.height//line_height)
                scroll_offset_year = max(min_scroll, min(scroll_offset_year, max_scroll))
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            active_username = rect_username.collidepoint(event.pos)
            active_email = rect_email.collidepoint(event.pos)
            active_password = rect_password.collidepoint(event.pos)
            active_again_password = rect_again_password.collidepoint(event.pos)

            if rect_button.collidepoint(event.pos):
                print("Регистрация", username,email, password, again_password)
                running = False
            if rect_day.collidepoint(event.pos):
                drop_day = not drop_day
                drop_month = drop_year = False

            elif rect_month.collidepoint(event.pos):
                drop_month = not drop_month
                drop_day = drop_year = False

            elif rect_year.collidepoint(event.pos):
                drop_year = not drop_year
                drop_day = drop_month = False
            if drop_day and day_dropdown_rect.collidepoint(event.pos):
                index = (my - day_dropdown_rect.y - scroll_offset_day) // line_height
                if 0 <= index < len(days):
                    selected_day = days[index]
                drop_day = False
            elif drop_month and month_dropdown_rect.collidepoint(event.pos):
                index = (my - month_dropdown_rect.y - scroll_offset_month) // line_height
                if 0 <= index < len(months):
                    selected_month = months[index]
                drop_month = False
            elif drop_year and year_dropdown_rect.collidepoint(event.pos):
                index = (my - year_dropdown_rect.y - scroll_offset_year) // line_height
                if 0 <= index < len(years):
                    selected_year = years[index]
                drop_year = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rect_checkbox.collidepoint(event.pos):
                checked = not checked

        if event.type == pygame.KEYDOWN:
            if active_username:
                if event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                else:
                    username += event.unicode
            elif active_email:
                if event.key == pygame.K_BACKSPACE:
                    email = email[:-1]
                else:
                    email += event.unicode
            elif active_password:
                if event.key == pygame.K_BACKSPACE:
                    password = password[:-1]
                else:
                    password += event.unicode
            elif active_again_password:
                if event.key == pygame.K_BACKSPACE:
                    again_password = again_password[:-1]
                else:
                    again_password += event.unicode
            

    screen.blit(background, (0, 0))

    block = pygame.Surface((1000, 700), pygame.SRCALPHA)
    pygame.draw.rect(block, (255, 255, 255, 180), (0, 0, 800, 700), border_radius=50)
    screen.blit(block, (WIDTH//2 - 400, HEIGHT//2 - 350))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 210))
    screen.blit(title, title_rect)

    color_username = ACTIVE_COLOR if active_username else WHITE
    pygame.draw.rect(screen, color_username, rect_username, border_radius=25)

    if username == "":
        text_surface = font_xx.render("введите имя пользователя", True, GRAY)
    else:
        text_surface = font_input.render(username, True, (0, 0, 0))

    screen.blit(text_surface, (rect_username.x + 20, rect_username.y + 15))

    def draw_input(rect, text, placeholder, active):
        color = ACTIVE_COLOR if active else WHITE
        pygame.draw.rect(screen, color, rect, border_radius=25)
        txt = font_xx.render(placeholder, True, GRAY) if text == "" else font_input.render(text, True, (0, 0, 0))
        screen.blit(txt, (rect.x + 20, rect.y + 15))
        if active and cursor_visible:
            pygame.draw.rect(screen, (0, 0, 0), (rect.x + 20 + txt.get_width() + 3, rect.y + 15, 3, 30))

    color_email = ACTIVE_COLOR if active_email else WHITE
    pygame.draw.rect(screen, color_email, rect_email, border_radius=25)
    if email == "":
        text_surface = font_xx.render("введите email", True, GRAY)
    else:
        text_surface = font_input.render(email, True, (0, 0, 0))
    screen.blit(text_surface, (rect_email.x + 20, rect_email.y + 15))
    color_password = ACTIVE_COLOR if active_password else WHITE
    pygame.draw.rect(screen, color_password, rect_password, border_radius=25)
    if password == "":
        text_surface = font_xx.render("введите пароль", True, GRAY)
    else:
        hidden = "*" * len(password)
        text_surface = font_input.render(hidden, True, (0, 0, 0))
    draw_input(rect_username, username, "введите имя пользователя", active_username)
    draw_input(rect_email, email, "введите email", active_email)
    draw_input(rect_password, "*" * len(password), "введите пароль", active_password)
    draw_input(rect_again_password, "*" * len(again_password), "повторите пароль", active_again_password)
    label = font_xx.render("дата рождения", True, RED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2 +200, HEIGHT // 2 + 170)))

    pygame.draw.rect(screen, BLUE, rect_day, border_radius=20)
    pygame.draw.rect(screen, BLUE, rect_month, border_radius=20)
    pygame.draw.rect(screen, BLUE, rect_year, border_radius=20)

    screen.blit(font_xx.render(selected_day or "dd", True, WHITE), (rect_day.x + 10, rect_day.y + 10))
    screen.blit(font_xx.render(selected_month or "mm", True, WHITE), (rect_month.x + 10, rect_month.y + 10))
    screen.blit(font_xx.render(selected_year or "yyyy", True, WHITE), (rect_year.x + 10, rect_year.y + 10))
    
    pygame.draw.rect(screen, WHITE, rect_checkbox, border_radius=5)
    if checked:
        pygame.draw.line(screen, BLUE, (rect_checkbox.x+4, rect_checkbox.y+10), (rect_checkbox.x+9, rect_checkbox.y+15), 3)
        pygame.draw.line(screen, BLUE, (rect_checkbox.x+9, rect_checkbox.y+15), (rect_checkbox.x+16, rect_checkbox.y+5), 3)
    text_surface = font_checkbox.render(checkbox_text, True, RED)
    screen.blit(text_surface, (rect_checkbox.x + 30, rect_checkbox.y + 2))

    
    
    
    def draw_dropdown(rect, items, scroll_offset):
        pygame.draw.rect(screen, WHITE, rect)
        for i, item in enumerate(items):
            y = rect.y + i * line_height + scroll_offset
            if rect.y <= y <= rect.y + rect.height - line_height:
                text = font_xx.render(item, True, (0, 0, 0))
                screen.blit(text, (rect.x + 5, y))
                
    if drop_day: draw_dropdown(day_dropdown_rect, days, scroll_offset_day)
    if drop_month: draw_dropdown(month_dropdown_rect, months, scroll_offset_month)
    if drop_year: draw_dropdown(year_dropdown_rect, years, scroll_offset_year)
    
    pygame.draw.rect(screen, WHITE, rect_button, border_radius=25)
    btn = font_input.render("Регистрация", True, BLUE)
    screen.blit(btn, btn.get_rect(center=rect_button.center))

    pygame.display.update()

pygame.quit()
sys.exit()