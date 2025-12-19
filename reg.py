import pygame
import sys
import os
import subprocess
import json
from datetime import datetime
from typing import Optional

GAME_FILES_MAPPING = {
  
    ("Pocoyo", "SQL"): "six1.py",
    ("Pocoyo", "Python"): "eight.py" ,
    ("Pocoyo", "Java"): "six2.py",
    ("Pocoyo", "C#"): "six3.py",

    ("Nina", "SQL"): "seven1.py",
    ("Nina", "Python"): "eight2.py",
    ("Nina", "Java"): "seven2.py",
    ("Nina", "C#"): "seven3.py",
}

db = None
try:
    from bd2 import DatabaseManager
    db = DatabaseManager()
    print("Модуль БД загружен успешно")
except ImportError as e:
    print(f"Ошибка загрузки модуля БД: {e}")
    db = None
except Exception as e:
    print(f"Другая ошибка при создании DatabaseManager: {e}")
    db = None

pygame.init()
pygame.mixer.init()


try:
    pygame.mixer.music.load(r"C:\Users\aiz\OneDrive\Desktop\osudos\retro-game-arcade-236133.mp3")
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.05) 
except Exception as e:
    print(f"Не удалось загрузить музыку: {e}")




WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
LIGHT_BLUE = (232, 249, 255)
BLUE = (14, 137, 185)
DARK_BLUE = (8, 92, 124)
RED = (179, 32, 33)
GREEN = (46, 204, 113)
GRAY = (170, 170, 170)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
ACTIVE_COLOR = (200, 230, 255)
BLACK = (0, 0, 0)
HOVER_BLUE = (100, 180, 255)
LOAD_GREEN = (0, 200, 0)
YELLOW = (232, 230, 116)
TOP_YELLOW = (255, 230, 70)
PANEL_GREEN = (80, 200, 120)
LIGHT_GREEN = (99, 183, 16)

title_font = pygame.font.SysFont("notable", 160)
button_font = pygame.font.SysFont("Advent Pro", 50)
font_input = pygame.font.SysFont(None, 40)
font_button = pygame.font.SysFont(None, 50)
font_xx = pygame.font.SysFont(None, 30)
font_checkbox = pygame.font.SysFont(None, 25)
subtitle_font = pygame.font.SysFont(None, 50)

# Новые шрифты для экрана настроек и профиля
try:
    TITLE_FONT = pygame.font.Font(None, 85)
    BUTTON_FONT = pygame.font.Font(None, 48)
    prof_title_f = pygame.font.SysFont("Advent Pro", 140, bold=True)
    prof_button_f = pygame.font.SysFont("Advent Pro", 35, bold=True)
    prof_stat_f = pygame.font.SysFont("Advent Pro", 50, bold=True)
    prof_value_f = pygame.font.SysFont("Advent Pro", 140)
except:
    prof_title_f = pygame.font.Font(None, 140) 
    prof_button_f = pygame.font.Font(None, 35)





def check_all_game_files():
    """Проверяет существование всех файлов игр"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    all_files_exist = True
    
    print("=" * 60)
    print("ПРОВЕРКА ФАЙЛОВ ИГР")
    print("=" * 60)
    
    for (character, language), filename in GAME_FILES_MAPPING.items():
        filepath = os.path.join(script_dir, filename)
        exists = os.path.exists(filepath)
        
        status = "✓" if exists else "✗"
        print(f"{status} {character:10} + {language:10} -> {filename:15} {'(НЕ НАЙДЕН!)' if not exists else ''}")
        
        if not exists:
            all_files_exist = False
    
    print("=" * 60)
    
    if not all_files_exist:
        print("ВНИМАНИЕ: Некоторые файлы игр не найдены!")
        print("Игра может не запуститься для некоторых комбинаций.")
        print("=" * 60)
    
    return all_files_exist


# Функция для безопасной загрузки изображений
def load_image_safe(path, default_size=None):
    try:
        img = pygame.image.load(path).convert_alpha()
        if default_size:
            img = pygame.transform.scale(img, default_size)
        return img
    except Exception as e:
        print(f"Не удалось загрузить изображение {path}: {e}")
        if default_size:
            img = pygame.Surface(default_size, pygame.SRCALPHA)
            img.fill((150, 150, 150, 200))
        else:
            img = pygame.Surface((100, 100), pygame.SRCALPHA)
            img.fill((150, 150, 150, 200))
        return img

# Загрузка фонов
main_bg = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Group 1 (3).png", (WIDTH, HEIGHT))
character = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Group 1 (4).png", (1260, 390))
login_bg = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg", (WIDTH, HEIGHT))

# Загрузка изображений для экрана "Как играть"
pals_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (76) 1.png", (550, 450))
scroll_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (78).webp", (50, 50))
coin_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (79).webp", (40, 40))
heart_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5280649977220763483_x 3.png", (220, 40))
shap_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Group 2.png", (380, 270))

# Загрузка изображений для выбора персонажа
character_bg = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg", (WIDTH, HEIGHT))
pocoyo_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (70) 1 (1).png", (220, 410))
nina_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (71) 1.png", (290, 400))

# Загрузка изображений для экрана выбора языка
language_bg = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\photo_5294226523462241209_x.jpg", (WIDTH, HEIGHT))
back_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Disclosure Button.png", (50, 50))
choose_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Frame 2.png", (220, 220))
setting_img = load_image_safe(r"C:\Users\aiz\OneDrive\Desktop\osudos\image 5.png", (60, 60))
pocoyo_language_img = load_image_safe("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (70) 1.png", (240, 400))

# Изображения для экрана настроек и профиля
settings_bg = load_image_safe(r"C:\Users\aiz\OneDrive\Desktop\osudos\photo_5294226523462241209_x.jpg", (WIDTH, HEIGHT))

def load_img_asset(path_name, size):
    return load_image_safe(path_name, size)

ICON_PROFILE = load_img_asset(r"C:\Users\aiz\OneDrive\Desktop\osudos\sticker (91).webp", (60, 60))
ICON_LANG = load_img_asset(r"C:\Users\aiz\OneDrive\Desktop\osudos\sticker (90).webp", (60, 60))
ICON_SOUND = load_img_asset(r"C:\Users\aiz\OneDrive\Desktop\osudos\sticker (92).webp", (60, 60))
ICON_RESULTS = load_img_asset(r"C:\Users\aiz\OneDrive\Desktop\osudos\sticker (89).webp", (60, 60))
ICON_BACK = load_img_asset("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Disclosure Button.png", (45, 45))

avatar_img = load_img_asset(r"C:\Users\aiz\OneDrive\Desktop\osudos\sticker (91).webp", (170, 170))
profile_pocoyo_img = load_img_asset("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (70) 1.png", (200, 370))
profile_nina_img = load_img_asset("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (71) 1.png", (280, 370))
profile_choose_img = load_img_asset("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Frame 2.png", (320, 320))

STATE_MAIN_MENU = 0
STATE_LOGIN = 1
STATE_REGISTER = 2
STATE_GAME_MENU = 3
STATE_EXIT_CONFIRM = 4
STATE_LOADING_SCREEN = 5
STATE_HOW_TO_PLAY = 6
STATE_CHARACTER_SELECT = 7
STATE_LANGUAGE_SELECT = 8
STATE_FINAL_LOADING = 9
STATE_SETTINGS = 10
STATE_PROFILE = 11

current_player = None
player_stats = None
db_connected = False

def init_database():
    global db_connected
    
    if db is None:
        print("Игра в режиме офлайн: Модуль БД недоступен")
        db_connected = False
        return False
    
    try:
        success, message = db.connect(
            dbname='osudos',
            user='postgres',
            password='87780455396',
            host='localhost',
            port='5432'
        )
        
        if success:
            print(message)
            db.initialize_database()
            db_connected = True
            return True
        else:
            print(f"Ошибка подключения к БД: {message}")
            db_connected = False
            return False
    except Exception as e:
        print(f"Исключение при подключении к БД: {e}")
        db_connected = False
        return False

def register_player_in_db(username, password, email, birth_date_str):
    if db is None or not db_connected:
        return False, "База недоступна"
    
    try:
        success, result = db.register_player(
            username=username,
            password=password,
            full_name=username,
            email=email if email else None,
            birth_date=birth_date_str if birth_date_str else None
        )
        return success, result
    except Exception as e:
        return False, f"Ошибка при регистрации: {e}"

def login_player_in_db(username, password):
    if db is None or not db_connected:
        return False, "База недоступна"
    
    try:
        success, result = db.login_player(username, password)
        return success, result
    except Exception as e:
        return False, f"Ошибка при входе: {e}"

def get_player_stats_from_db(player_id):
    if db is None or not db_connected or not player_id:
        return {}
    
    try:
        return db.get_player_stats(player_id)
    except Exception as e:
        print(f"Ошибка при загрузке статистики: {e}")
        return {}

class FlatButton:
    def __init__(self, y, text, icon, action):
        self.rect = pygame.Rect(WIDTH//2 - 400, y, 800, 100)
        self.text = text
        self.icon = icon
        self.action = action
        self.hover = False

    def draw(self, s):
        mouse = pygame.mouse.get_pos()
        self.hover = self.rect.collidepoint(mouse)
        color = HOVER_BLUE if self.hover else (75, 195, 255)
        pygame.draw.rect(s, color, self.rect, border_radius=40)
        s.blit(self.icon, (self.rect.x + 35, self.rect.y + 20))
        txt = BUTTON_FONT.render(self.text, True, WHITE)
        s.blit(txt, (self.rect.x + 140, self.rect.centery - txt.get_height()//2))

    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover: return self.action

class SettingsScreen:
    def __init__(self):
        self.languages = ["Русский", "Қазақша", "English"]
        self.lang_idx = 0
        self.music = True
        base = HEIGHT // 2 - 180
        self.buttons = [
            FlatButton(base, "Профиль", ICON_PROFILE, "open_profile"),
            FlatButton(base+130, "Язык: Русский", ICON_LANG, "lang"),
            FlatButton(base+260, "Музыка: Включена", ICON_SOUND, "music"),
            FlatButton(base+390, "Мои результаты", ICON_RESULTS, "results"),
        ]
        self.back_rect = pygame.Rect(50, 30, 80, 80)
        

    def draw(self, screen):
        screen.blit(settings_bg, (0, 0))
        panel = pygame.Rect(WIDTH//2 - 550, HEIGHT//2 - 310, 1100, 700)
        pygame.draw.rect(screen, (60, 150, 90), panel.inflate(18, 18), border_radius=55)
        pygame.draw.rect(screen, PANEL_GREEN, panel, border_radius=55)
        
        top = pygame.Rect(panel.x, panel.y - 90, panel.width, 90)
        pygame.draw.rect(screen, (235, 200, 40), top.inflate(18, 18), border_radius=45)
        pygame.draw.rect(screen, TOP_YELLOW, top, border_radius=45)
        
        title = TITLE_FONT.render("НАСТРОЙКИ", True, WHITE)
        screen.blit(title, (top.centerx - title.get_width()//2, top.y -10))
        for b in self.buttons: b.draw(screen)
        
        # Кнопка назад
        screen.blit(ICON_BACK, (self.back_rect.x, self.back_rect.y))

    def handle_event(self, event, mouse_pos):
        for b in self.buttons:
            a = b.click(event)
            if a: return a
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(mouse_pos):
                return "back"
        
        return None

class ProfileScreen:
    def __init__(self, selected_character: Optional[str] = None):
        if selected_character is None:
            selected_character = "Pocoyo"
        self.back_rect = pygame.Rect(50, 30, 80, 80)
        self.selected_character = selected_character
        # Добавляем прямоугольник для кнопки выбора персонажа
        self.choose_rect = pygame.Rect(WIDTH // 2 + 220, HEIGHT // 2 + 10, 320, 320)
        self.choose_hover = False
        
    def draw(self, screen):
        screen.blit(settings_bg, (0, 0))
        
        title_text = prof_title_f.render("Профиль", True, WHITE)
        screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, 185)))
        top_block = pygame.Surface((1350, 200), pygame.SRCALPHA)
        pygame.draw.rect(top_block, (255, 255, 255, 140), (0, 0, 1350, 200), border_radius=100)
        screen.blit(top_block, (WIDTH // 2 - 675, HEIGHT // 2 - 275))

        bot_block = pygame.Surface((990, 420), pygame.SRCALPHA)
        pygame.draw.rect(bot_block, (255, 255, 255, 140), (0, 0, 990, 420), border_radius=100)
        screen.blit(bot_block, (WIDTH // 2 - 995, HEIGHT // 2 -40))

        screen.blit(avatar_img, (WIDTH // 2 - 650, HEIGHT // 2 - 260))
        
        # Отображаем выбранного персонажа
        if self.selected_character == "Pocoyo":
            screen.blit(profile_pocoyo_img, (WIDTH // 2 - 750, HEIGHT // 2 + 10))
            character_name = "POCOYO"
            character_color = BLUE
        else:  # Nina
            screen.blit(profile_nina_img, (WIDTH // 2 - 770, HEIGHT // 2 + 10))
            character_name = "NINA"
            character_color = GREEN
        
        # Подсветка при наведении
        if self.choose_hover:
            # Рисуем полупрозрачный оверлей
            overlay = pygame.Surface((320, 320), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 50))
            screen.blit(overlay, (self.choose_rect.x, self.choose_rect.y))
            
            # Текст подсказки
            choose_text = prof_button_f.render("Выбрать персонажа", True, character_color)
            choose_text_rect = choose_text.get_rect(center=(WIDTH // 2 + 380, HEIGHT // 2 - 20))
            screen.blit(choose_text, choose_text_rect)
        
        # Картинка для выбора персонажа (кликабельная) - ТОЛЬКО ОДИН РАЗ
        screen.blit(profile_choose_img, (WIDTH // 2 + 220, HEIGHT // 2 + 10))

        for y, txt in [(HEIGHT//2 - 215, "ИЗМЕНИТЬ ПАРОЛЬ"), (HEIGHT//2 - 135, "ИЗМЕНИТЬ EMAIL")]:
            btn_surf = pygame.Surface((300, 50), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, character_color, (0, 0, 300, 50), border_radius=25)
            screen.blit(btn_surf, (WIDTH // 2 + 300, y - 25))
            label = prof_button_f.render(txt, True, WHITE)
            screen.blit(label, label.get_rect(center=(WIDTH // 2 + 450, y)))

        t3 = prof_stat_f.render("ТОЧНОСТЬ ОТВЕТОВ", True, RED)
        screen.blit(t3, t3.get_rect(center=(WIDTH // 2 - 270, HEIGHT // 2 - 225)))
        t4 = prof_value_f.render("100%", True, character_color)
        screen.blit(t4, t4.get_rect(center=(WIDTH // 2 - 270, HEIGHT // 2 - 150)))
        
        t5 = prof_stat_f.render("УРОВЕНЬ ИГРОКА", True, RED)
        screen.blit(t5, t5.get_rect(center=(WIDTH // 2 - 340, HEIGHT // 2 + 40)))
        t6 = prof_value_f.render("LEVEL 2", True, character_color)
        screen.blit(t6, t6.get_rect(center=(WIDTH // 2 - 309, HEIGHT // 2 + 130)))
        
        t7 = prof_stat_f.render("ЛЮБИМЫЙ ПЕРСОНАЖ", True, RED)
        screen.blit(t7, t7.get_rect(center=(WIDTH // 2 - 300, HEIGHT // 2 + 210)))
        t8 = prof_value_f.render(character_name, True, character_color)
        screen.blit(t8, t8.get_rect(center=(WIDTH // 2 - 309, HEIGHT // 2 + 300)))
        
        # Кнопка назад
        screen.blit(ICON_BACK, (self.back_rect.x, self.back_rect.y))

    def handle_event(self, event, mouse_pos):
        # Обновляем состояние наведения
        self.choose_hover = self.choose_rect.collidepoint(mouse_pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_rect.collidepoint(mouse_pos):
                return "back"
            elif self.choose_rect.collidepoint(mouse_pos):
                return "choose_character"
        return None

def draw_main_menu(screen, mouse_pos, buttons):
    screen.blit(main_bg, (0, 0))
    
    block_width, block_height = 800, 600
    block_x = WIDTH // 2 - block_width // 2
    block_y = HEIGHT // 2 - block_height // 2
    
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))
    
    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)
    
    char_x = WIDTH // 2 - character.get_width() // 2
    char_y = HEIGHT // 2 - character.get_height() // 2 + 180
    screen.blit(character, (char_x - 10, char_y))
    
    for btn in buttons:
        text, rect, color = btn
        
        if rect.collidepoint(mouse_pos):
            color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        
        pygame.draw.rect(screen, color, rect, border_radius=20)
        
        text_color = BLUE if text != "Выход" else WHITE
        text_surface = button_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

def draw_login_screen(screen, login, password, active_login, active_password, cursor_visible, rect_login, rect_password, rect_button, back_button):
    screen.blit(login_bg, (0, 0))

    block_width, block_height = 800, 600
    block_x = WIDTH // 2 - block_width // 2
    block_y = HEIGHT // 2 - block_height // 2
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)

    color_login = ACTIVE_COLOR if active_login else WHITE
    pygame.draw.rect(screen, color_login, rect_login, border_radius=25)
    pygame.draw.rect(screen, DARK_GRAY if active_login else GRAY, rect_login, 2, border_radius=25)

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
    pygame.draw.rect(screen, DARK_GRAY if active_password else GRAY, rect_password, 2, border_radius=25)

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
    pygame.draw.rect(screen, BLUE, rect_button, 2, border_radius=25)
    btn = font_button.render("Войти", True, BLUE)
    screen.blit(btn, btn.get_rect(center=rect_button.center))
    
    pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
    back_text = font_xx.render("Назад", True, WHITE)
    screen.blit(back_text, (back_button.x + 20, back_button.y + 10))

def draw_loading_screen(screen, player_name, load_width, load_bar_width, load_bar_height, 
                        load_x, load_y, block_width, block_height, block_x, block_y):
    """Отрисовка экрана загрузки"""
    screen.blit(login_bg, (0, 0))

    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)

    # Приветствие с именем игрока
    if player_name:
        welcome_text = subtitle_font.render(f"Добро пожаловать, {player_name}!", True, BLUE)
    else:
        welcome_text = subtitle_font.render("Добро пожаловать!", True, BLUE)
    
    welcome_rect = welcome_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
    screen.blit(welcome_text, welcome_rect)

    info_text = subtitle_font.render("Проверь свои знания и узнай новое!", True, BLUE)
    info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    screen.blit(info_text, info_rect)

    # Полоса загрузки
    pygame.draw.rect(screen, WHITE, (load_x, load_y, load_bar_width, load_bar_height), 3, border_radius=15)
    pygame.draw.rect(screen, LOAD_GREEN, (load_x, load_y, load_width, load_bar_height), border_radius=15)

def draw_how_to_play_screen(screen, mouse_pos, back_button_rect, pals_img_rect):
    """Отрисовка экрана 'Как играть?'"""
    screen.blit(main_bg, (0, 0))
    
    block_width, block_height = 1550, 800
    block_x = WIDTH // 2 - block_width // 2
    block_y = HEIGHT // 2 - block_height // 2 + 180
    
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), 
                     (0, 0, block_width, block_height), border_radius=100)
    screen.blit(center_rect, (block_x, block_y))
    
    # Позиция для картинки персонажа
    pals_x = WIDTH//2 + 200
    pals_y = HEIGHT//2 - 50
    screen.blit(pals_img, (pals_x, pals_y))
    
    # Создаем прямоугольник для клика по картинке
    if pals_img_rect is None:
        pals_img_rect = pygame.Rect(pals_x, pals_y, 550, 450)
    
    # Заголовок
    title_font_how = pygame.font.SysFont("notable", 200)
    title = title_font_how.render("ÖSU DOS", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 310))
    screen.blit(title, title_rect)
    
    # Текст "Как играть"
    title1 = font_input.render("Движение:", True, BLACK)
    title1_rect = title1.get_rect(center=(WIDTH // 2 - 560, HEIGHT // 2-160))
    screen.blit(title1, title1_rect)
    
    screen.blit(shap_img, (WIDTH//2 - 550, HEIGHT//2 - 230))
    
    title2 = font_input.render("Цель игры:", True, BLACK)
    title2_rect = title2.get_rect(center=(WIDTH // 2 - 560, HEIGHT // 2 -20))
    screen.blit(title2, title2_rect)
    
    line1 = font_input.render("Цель игры — пройти уровень, собирая письма с вопросами ", True, RED)
    line2 = font_input.render("по программированию и правильно отвечая на них.", True, RED)
    line1_rect = line1.get_rect(center=(WIDTH // 2 - 180, HEIGHT // 2 + 20))
    line2_rect = line2.get_rect(center=(WIDTH // 2 - 236, HEIGHT // 2 + 60))
    screen.blit(line1, line1_rect)
    screen.blit(line2, line2_rect)
    
    title3 = font_input.render("Игрок должен:", True, BLACK)
    title3_rect = title3.get_rect(center=(WIDTH // 2 - 535, HEIGHT // 2 + 100))
    screen.blit(title3, title3_rect)
    
    # Список задач игрока
    line3 = font_input.render("— находить письма;", True, RED)
    screen.blit(scroll_img, (WIDTH//2 - 140, HEIGHT//2 + 115))
    
    line4 = font_input.render("— открывать вопросы;", True, RED)
    line5 = font_input.render("— выбирать правильные ответы;", True, RED)
    line6 = font_input.render("— собирать монеты;", True, RED)
    screen.blit(coin_img, (WIDTH//2 - 150, HEIGHT//2 + 240))
    
    line7 = font_input.render("— использовать монеты для жизней;", True, RED)
    line8 = font_input.render("— не потерять все 5 жизней.", True, RED)
    screen.blit(heart_img, (WIDTH//2 - 20, HEIGHT//2 + 320))
    
    line3_rect = line3.get_rect(center=(WIDTH // 2 - 300, HEIGHT // 2 + 140))
    line4_rect = line4.get_rect(center=(WIDTH // 2 - 282, HEIGHT // 2 + 180))
    line5_rect = line5.get_rect(center=(WIDTH // 2 - 215, HEIGHT // 2 + 220))
    line6_rect = line6.get_rect(center=(WIDTH // 2 - 300, HEIGHT // 2 + 260))
    line7_rect = line7.get_rect(center=(WIDTH // 2 - 95, HEIGHT // 2 + 300))
    line8_rect = line8.get_rect(center=(WIDTH // 2 - 245, HEIGHT // 2 + 340))
    
    screen.blit(line3, line3_rect)
    screen.blit(line4, line4_rect)
    screen.blit(line5, line5_rect)
    screen.blit(line6, line6_rect)
    screen.blit(line7, line7_rect)
    screen.blit(line8, line8_rect)
    
    # Кнопка "НАЖМИТЕ НА НАС"
    title5 = font_button.render("НАЖМИТЕ НА НАС", True, BLUE)
    title5_rect = title5.get_rect(center=(WIDTH // 2 + 490, HEIGHT // 2 - 100))
    screen.blit(title5, title5_rect)
    
    # Кнопка "Продолжить" (вместо "Назад")
    if back_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_BLUE, back_button_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BLUE, back_button_rect, border_radius=10)
    
    continue_text = font_xx.render("Продолжить", True, WHITE)
    screen.blit(continue_text, (back_button_rect.x + 15, back_button_rect.y + 10))
    
    return back_button_rect, pals_img_rect

def draw_character_select_screen(screen, mouse_pos, pocoyo_offset, nina_offset):
    """Отрисовка экрана выбора персонажа"""
    screen.blit(character_bg, (0, 0))
    
    block_width, block_height = 900, 570
    pocoyo_x = WIDTH // 2 - block_width // 2 - 550
    pocoyo_y = HEIGHT // 2 - block_height // 2 + 80 + pocoyo_offset

    pocoyo_rect = pygame.Rect(pocoyo_x, pocoyo_y, block_width, block_height)

    nina_x = WIDTH // 2 - block_width // 2 + 550
    nina_y = HEIGHT // 2 - block_height // 2 + 80 + nina_offset

    nina_rect = pygame.Rect(nina_x, nina_y, block_width, block_height)
    
    # Определяем шрифты для этого экрана
    char_title_font = pygame.font.SysFont("Advent Pro", 140, bold=True)
    char_button_font = pygame.font.SysFont("Advent Pro", 35, bold=True)
    char_button1_font = pygame.font.SysFont("Advent Pro", 50, bold=True)
    char_text2_font = pygame.font.SysFont("Advent Pro", 60)

    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180),
                     (0, 0, block_width, block_height), border_radius=70)
    screen.blit(center_rect, (pocoyo_x, pocoyo_y))

    center1_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center1_rect, (255, 255, 255, 180),
                     (0, 0, block_width, block_height), border_radius=70)
    screen.blit(center1_rect, (nina_x, nina_y))

    title = char_title_font.render("ВЫБЕРИТЕ ПЕРСОНАЖА", True, WHITE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 310))
    screen.blit(title, title_rect)
    
    text1 = char_title_font.render("POCOYO", True, BLUE)
    text1_rect = text1.get_rect(center=(WIDTH // 2 - 520, HEIGHT // 2 + 300 + pocoyo_offset))
    screen.blit(text1, text1_rect)
    
    text2 = char_title_font.render("NINA", True, GREEN)
    text2_rect = text2.get_rect(center=(WIDTH // 2 + 500, HEIGHT // 2 + 300 + nina_offset))
    screen.blit(text2, text2_rect)
    
    screen.blit(pocoyo_img, (WIDTH//2 - 350, HEIGHT//2 - 50 + pocoyo_offset))
    screen.blit(nina_img, (WIDTH//2 + 120, HEIGHT//2 - 50 + nina_offset))
    
    # Энергичный, быстрый, решительный.
    text3 = char_button_font.render("Энергичный, быстрый, решительный.", True, BLACK)
    text3_rect = text3.get_rect(center=(WIDTH // 2 - 510, HEIGHT // 2 - 90 + pocoyo_offset))
    screen.blit(text3, text3_rect)
    
    # Спокойный, внимательный, точный.
    text4 = char_button_font.render("Спокойный, внимательный, точный.", True, BLACK)
    text4_rect = text4.get_rect(center=(WIDTH // 2 + 520, HEIGHT // 2 - 90 + nina_offset))
    screen.blit(text4, text4_rect)
    
    # Особенность:
    text5 = char_button1_font.render("Особенность: ", True, BLACK)
    text5_rect = text5.get_rect(center=(WIDTH // 2 - 620, HEIGHT // 2 + 20 + pocoyo_offset))
    screen.blit(text5, text5_rect)
    
    # +5% скорость
    text6 = char_text2_font.render("+5% скорость", True, BLUE)
    text6_rect = text6.get_rect(center=(WIDTH // 2 - 600, HEIGHT // 2 + 80 + pocoyo_offset))
    screen.blit(text6, text6_rect)
    
    # Особенность:
    text7 = char_button1_font.render("Особенность: ", True, BLACK)
    text7_rect = text7.get_rect(center=(WIDTH // 2 + 620, HEIGHT // 2 + 20 + nina_offset))
    screen.blit(text7, text7_rect)
    
    # +5% точность
    text8 = char_text2_font.render("+5% точность", True, GREEN)
    text8_rect = text8.get_rect(center=(WIDTH // 2 + 600, HEIGHT // 2 + 80 + nina_offset))
    screen.blit(text8, text8_rect)
    
    # Кнопка "Назад"
    back_button = pygame.Rect(50, 50, 100, 40)
    pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
    back_text = font_xx.render("Назад", True, WHITE)
    screen.blit(back_text, (back_button.x + 20, back_button.y + 10))
    
    return pocoyo_rect, nina_rect, back_button

def draw_language_select_screen(screen, mouse_pos, selected_character, block_size, block_y_offsets, clicked_block):
    """Отрисовка экрана выбора языка программирования"""
    screen.blit(language_bg, (0, 0))
    
    mx, my = mouse_pos
    
    # Позиции блоков с языками
    blocks_pos = [
        (WIDTH // 2 - 550, HEIGHT // 2),  # SQL
        (WIDTH // 2 - 200, HEIGHT // 2),  # Python
        (WIDTH // 2 + 150, HEIGHT // 2),  # C#
        (WIDTH // 2 + 500, HEIGHT // 2)   # Java
    ]
    labels = ["SQL", "Python", "C#", "JAVA"]
    
    block_rects = []  # Будем хранить прямоугольники всех блоков
    
    # Отображаем блоки с анимацией при наведении и нажатии
    for i, (bx, by) in enumerate(blocks_pos):
        size = block_size[i]
        y_offset = block_y_offsets[i]
        
        rect = pygame.Rect(
            bx - size // 2, by - size // 2 + y_offset, size, size
        )
        block_rects.append(rect)  # Сохраняем прямоугольник
        
        # Определяем цвет блока
        block_color = (255, 255, 255, 180)
        if clicked_block == i:
            # Подсветка для выбранного блока
            block_color = (200, 230, 255, 200)
        elif rect.collidepoint(mx, my):
            # Подсветка при наведении
            block_color = (230, 245, 255, 200)
        
        center_rect = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(center_rect, block_color,
                         (0, 0, size, size), border_radius=60)
        screen.blit(center_rect, (rect.x, rect.y))
        
        font_scaled = pygame.font.SysFont("notable", int(80 * (size / 300)))
        label = font_scaled.render(labels[i], True, BLUE)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)
    
    # Верхний блок с текстом
    block_width, block_height = 1200, 100
    block_x = WIDTH // 2 - block_width // 2 + 50
    block_y = HEIGHT // 2 - block_height // 2 - 330
    
    center4_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center4_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=40)
    screen.blit(center4_rect, (block_x, block_y))
    
    block_width, block_height = 1150, 100
    block_x = WIDTH // 2 - block_width // 2 + 80
    block_y = HEIGHT // 2 - block_height // 2 - 330
    
    center5_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center5_rect, YELLOW, (0, 0, block_width, block_height), border_radius=40)
    screen.blit(center5_rect, (block_x, block_y))
    
    # Текст
    title_font_lang = pygame.font.SysFont("Advent Pro", 40)
    title = title_font_lang.render("Выберите язык программирования, на котором хотите пройти игру... ", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2 + 50, HEIGHT // 2 - 330))
    screen.blit(title, title_rect)
    
    # Кнопка "Назад"
    screen.blit(back_img, (WIDTH//2 - 680, HEIGHT//2 - 360))
    back_button = pygame.Rect(WIDTH//2 - 680, HEIGHT//2 - 360, 50, 50)
    
    # Иконка настроек
    setting_button_rect = pygame.Rect(WIDTH//2 + 680, HEIGHT//2 - 365, 60, 60)
    screen.blit(setting_img, (setting_button_rect.x, setting_button_rect.y))
    
    # Кнопка choose_img
    choose_x = WIDTH//2 - 110
    choose_y = HEIGHT//2 + 180
    screen.blit(choose_img, (choose_x, choose_y))
    choose_button = pygame.Rect(choose_x, choose_y, 220, 220)
    
    # Отображаем выбранного персонажа
    if selected_character == "Pocoyo":
        screen.blit(pocoyo_language_img, (WIDTH//2 + 500, HEIGHT//2 + 20))
    elif selected_character == "Nina":
        screen.blit(nina_img, (WIDTH//2 + 500, HEIGHT//2 + 20))
    
    return blocks_pos, labels, back_button, choose_button, setting_button_rect, block_rects

def draw_final_loading_screen(screen, load_width, load_bar_width, load_bar_height, 
                              load_x, load_y, block_width, block_height, block_x, block_y,
                              mouse_pos, selected_character, selected_language):
    
    screen.blit(main_bg, (0, 0))
    
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)

    # Полоса загрузки
    pygame.draw.rect(screen, WHITE, (load_x, load_y, load_bar_width, load_bar_height), 3, border_radius=15)
    pygame.draw.rect(screen, YELLOW, (load_x, load_y, load_width, load_bar_height), border_radius=15)

    # Текст с информацией о выборе
    if selected_character and selected_language:
        info_text = subtitle_font.render(f"{selected_character} - {selected_language}", True, BLUE)
        info_rect = info_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(info_text, info_rect)
    
    # Текст
    start_text = subtitle_font.render("ВЫ ГОТОВЫ НАЧАТЬ?", True, WHITE)
    start_rect = start_text.get_rect(center=(WIDTH // 2, block_y + block_height - 180))
    screen.blit(start_text, start_rect)

    # Кнопки ДА и НЕТ
    button_width = 150
    button_height = 60
    button_padding = 50
    button_y_pos = block_y + block_height - 120
    
    # Кнопка ДА
    yes_button_rect = pygame.Rect(WIDTH // 2 - button_width - button_padding // 2, button_y_pos, button_width, button_height)
    if yes_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_BLUE, yes_button_rect, border_radius=30)
    else:
        pygame.draw.rect(screen, WHITE, yes_button_rect, border_radius=30)
    pygame.draw.rect(screen, BLUE, yes_button_rect, 2, border_radius=30)
    yes_text = button_font.render("ДА", True, BLUE)
    yes_rect = yes_text.get_rect(center=(yes_button_rect.x + button_width // 2, yes_button_rect.y + button_height // 2))
    screen.blit(yes_text, yes_rect)
    
    # Кнопка НЕТ
    no_button_rect = pygame.Rect(WIDTH // 2 + button_padding // 2, button_y_pos, button_width, button_height)
    if no_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, HOVER_BLUE, no_button_rect, border_radius=30)
    else:
        pygame.draw.rect(screen, WHITE, no_button_rect, border_radius=30)
    pygame.draw.rect(screen, BLUE, no_button_rect, 2, border_radius=30)
    no_text = button_font.render("НЕТ", True, BLUE)
    no_rect = no_text.get_rect(center=(no_button_rect.x + button_width // 2, no_button_rect.y + button_height // 2))
    screen.blit(no_text, no_rect)
    
    return yes_button_rect, no_button_rect

class DatePicker:
    def __init__(self, x, y, width, height, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.dropdown_open = False
        self.value = ""
        self.items = []
        self.scroll_offset = 0
        self.max_visible_items = 5
        self.item_height = 40
        
    def set_items(self, items):
        self.items = items
        
    def draw(self, screen, mouse_pos):
        # Рисуем основную кнопку
        bg_color = HOVER_BLUE if self.rect.collidepoint(mouse_pos) else LIGHT_GRAY
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2, border_radius=8)
        
        # Текст выбранного значения
        display_text = self.value if self.value else self.label
        text_color = BLACK if self.value else GRAY
        text_surface = font_xx.render(display_text, True, text_color)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        
        # Стрелочка
        arrow_x = self.rect.right - 30
        arrow_y = self.rect.centery
        if self.dropdown_open:
            pygame.draw.polygon(screen, DARK_BLUE, [
                (arrow_x, arrow_y - 5),
                (arrow_x + 10, arrow_y - 5),
                (arrow_x + 5, arrow_y + 5)
            ])
        else:
            pygame.draw.polygon(screen, DARK_BLUE, [
                (arrow_x, arrow_y + 5),
                (arrow_x + 10, arrow_y + 5),
                (arrow_x + 5, arrow_y - 5)
            ])
        
        # Рисуем выпадающий список
        if self.dropdown_open and self.items:
            dropdown_height = min(len(self.items), self.max_visible_items) * self.item_height
            dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, dropdown_height)
            
            # Фон выпадающего списка
            pygame.draw.rect(screen, WHITE, dropdown_rect)
            pygame.draw.rect(screen, DARK_GRAY, dropdown_rect, 2)
            
            # Элементы списка
            start_idx = max(0, min(len(self.items) - self.max_visible_items, 
                                  self.scroll_offset // self.item_height))
            end_idx = min(start_idx + self.max_visible_items, len(self.items))
            
            for i in range(start_idx, end_idx):
                item_rect = pygame.Rect(
                    dropdown_rect.x,
                    dropdown_rect.y + (i - start_idx) * self.item_height,
                    dropdown_rect.width,
                    self.item_height
                )
                
                # Подсветка при наведении
                if item_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, HOVER_BLUE, item_rect)
                
                # Текст элемента
                item_text = font_xx.render(str(self.items[i]), True, BLACK)
                screen.blit(item_text, (item_rect.x + 10, item_rect.y + 10))
    
    def handle_event(self, event, mouse_pos):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Проверяем клик по основной кнопке
            if self.rect.collidepoint(mouse_pos):
                self.dropdown_open = not self.dropdown_open
                return True
            
            # Проверяем клик по элементам выпадающего списка
            if self.dropdown_open and self.items:
                dropdown_height = min(len(self.items), self.max_visible_items) * self.item_height
                dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, dropdown_height)
                
                if dropdown_rect.collidepoint(mouse_pos):
                    start_idx = max(0, min(len(self.items) - self.max_visible_items, 
                                          self.scroll_offset // self.item_height))
                    relative_y = mouse_pos[1] - dropdown_rect.y
                    clicked_index = start_idx + (relative_y // self.item_height)
                    
                    if 0 <= clicked_index < len(self.items):
                        self.value = str(self.items[clicked_index])
                        self.dropdown_open = False
                        return True
            
            # Закрываем выпадающий список при клике вне его области
            if self.dropdown_open:
                dropdown_height = min(len(self.items), self.max_visible_items) * self.item_height if self.items else 0
                dropdown_rect = pygame.Rect(self.rect.x, self.rect.bottom, self.rect.width, dropdown_height)
                # Закрываем только если клик был вне основной кнопки и вне выпадающего списка
                if not self.rect.collidepoint(mouse_pos) and not dropdown_rect.collidepoint(mouse_pos):
                    self.dropdown_open = False
        
        # Прокрутка колесиком мыши
        if event.type == pygame.MOUSEWHEEL and self.dropdown_open:
            self.scroll_offset -= event.y * 20
            self.scroll_offset = max(0, min(self.scroll_offset, 
                                           len(self.items) * self.item_height - 
                                           self.max_visible_items * self.item_height))
        
        return False

def draw_register_screen(screen, username, email, password, again_password, checked, 
                         active_username, active_email, active_password, active_again_password, 
                         cursor_visible, rect_username, rect_email, rect_password, 
                         rect_again_password, rect_checkbox, rect_button, back_button,
                         day_picker, month_picker, year_picker):
    screen.blit(login_bg, (0, 0))

    block = pygame.Surface((1000, 700), pygame.SRCALPHA)
    pygame.draw.rect(block, (255, 255, 255, 180), (0, 0, 800, 700), border_radius=50)
    screen.blit(block, (WIDTH//2 - 400, HEIGHT//2 - 350))

    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 210))
    screen.blit(title, title_rect)

    def draw_input_field(rect, text, placeholder, active, is_password=False):
        color = ACTIVE_COLOR if active else WHITE
        pygame.draw.rect(screen, color, rect, border_radius=25)
        pygame.draw.rect(screen, DARK_GRAY if active else GRAY, rect, 2, border_radius=25)
        if text == "":
            txt = font_xx.render(placeholder, True, GRAY)
        else:
            if is_password:
                txt = font_input.render("*" * len(text), True, (0, 0, 0))
            else:
                txt = font_input.render(text, True, (0, 0, 0))
        screen.blit(txt, (rect.x + 20, rect.y + 15))
        if active and cursor_visible:
            pygame.draw.rect(screen, (0, 0, 0), (rect.x + 20 + txt.get_width() + 3, rect.y + 15, 3, 30))

    # Поля ввода
    draw_input_field(rect_username, username, "введите имя пользователя", active_username)
    draw_input_field(rect_email, email, "введите email", active_email)
    draw_input_field(rect_password, password, "введите пароль", active_password, True)
    draw_input_field(rect_again_password, again_password, "повторите пароль", active_again_password, True)
    
    # Заголовок для даты рождения
    label = font_xx.render("дата рождения", True, RED)
    screen.blit(label, label.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2 + 160)))
    
    # Рисуем пикеры даты
    mouse_pos = pygame.mouse.get_pos()
    day_picker.draw(screen, mouse_pos)
    month_picker.draw(screen, mouse_pos)
    year_picker.draw(screen, mouse_pos)
    
    # Разделители
    sep_y = day_picker.rect.y + 5
    pygame.draw.line(screen, DARK_GRAY, (month_picker.rect.x - 5, sep_y),  
                     (month_picker.rect.x - 5, sep_y + 30), 2)
    pygame.draw.line(screen, DARK_GRAY, (year_picker.rect.x - 5, sep_y), 
                     (year_picker.rect.x - 5, sep_y + 30), 2)
    
    # Чекбокс
    pygame.draw.rect(screen, WHITE, rect_checkbox, border_radius=5)
    pygame.draw.rect(screen, BLUE if checked else GRAY, rect_checkbox, 2, border_radius=5)
    if checked:
        pygame.draw.line(screen, BLUE, (rect_checkbox.x+4, rect_checkbox.y+10), 
                         (rect_checkbox.x+9, rect_checkbox.y+15), 3)
        pygame.draw.line(screen, BLUE, (rect_checkbox.x+9, rect_checkbox.y+15), 
                         (rect_checkbox.x+16, rect_checkbox.y+5), 3)
    checkbox_text = "Я согласен с условиями использования"
    text_surface = font_checkbox.render(checkbox_text, True, RED)
    screen.blit(text_surface, (rect_checkbox.x + 30, rect_checkbox.y + 2))
    
    # Кнопка регистрации - ВСЕГДА ТЕКСТ "Регистрация"
    pygame.draw.rect(screen, WHITE, rect_button, border_radius=25)
    pygame.draw.rect(screen, DARK_GRAY, rect_button, 2, border_radius=25)  
    
    # Всегда отображаем текст "Регистрация"
    btn_text = "Регистрация"
    btn = font_input.render(btn_text, True, BLUE)
    screen.blit(btn, btn.get_rect(center=rect_button.center))
    
    # Кнопка назад
    pygame.draw.rect(screen, BLUE, back_button, border_radius=10)
    back_text = font_xx.render("Назад", True, WHITE)
    screen.blit(back_text, (back_button.x + 20, back_button.y + 10))



def draw_exit_confirmation(screen, mouse_pos):
    screen.blit(main_bg, (0, 0))
    
    block_width, block_height = 800, 600
    block_x = WIDTH // 2 - block_width // 2
    block_y = HEIGHT // 2 - block_height // 2
    
    center_rect = pygame.Surface((block_width, block_height), pygame.SRCALPHA)
    pygame.draw.rect(center_rect, (255, 255, 255, 180), (0, 0, block_width, block_height), border_radius=50)
    screen.blit(center_rect, (block_x, block_y))
    
    title = title_font.render("ÖSU DOS", True, BLUE)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 170))
    screen.blit(title, title_rect)
    
    text_surface = subtitle_font.render("Вы уверены, что хотите выйти?", True, RED)
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 0))
    screen.blit(text_surface, text_rect)
    
    button_width, button_height = 150, 60
    button_spacing = 50
    button_y = HEIGHT // 2 + 100
    
    yes_button_x = WIDTH // 2 - button_width - button_spacing // 2
    yes_button_rect = pygame.Rect(yes_button_x, button_y, button_width, button_height)
    
    no_button_x = WIDTH // 2 + button_spacing // 2
    no_button_rect = pygame.Rect(no_button_x, button_y, button_width, button_height)
    
    button_color = WHITE
    button_hover_color = (220, 220, 220)
    text_color = BLUE
    
    # Рисуем кнопку "Да"
    if yes_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, yes_button_rect, border_radius=15)
    else:
        pygame.draw.rect(screen, button_color, yes_button_rect, border_radius=15)
    pygame.draw.rect(screen, DARK_GRAY, yes_button_rect, 2, border_radius=15)
    
    yes_text = subtitle_font.render("Да", True, text_color)
    yes_text_rect = yes_text.get_rect(center=yes_button_rect.center)
    screen.blit(yes_text, yes_text_rect)
    
    # Рисуем кнопку "Нет"
    if no_button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, button_hover_color, no_button_rect, border_radius=15)
    else:
        pygame.draw.rect(screen, button_color, no_button_rect, border_radius=15)
    pygame.draw.rect(screen, DARK_GRAY, no_button_rect, 2, border_radius=15)
    
    no_text = subtitle_font.render("Нет", True, text_color)
    no_text_rect = no_text.get_rect(center=no_button_rect.center)
    screen.blit(no_text, no_text_rect)
    
    return yes_button_rect, no_button_rect

def main():
    global current_player, player_stats, db_connected
    
    db_initialized = init_database()
    if not db_initialized:
        print("Игра в режиме офлайн")
    
    current_state = STATE_MAIN_MENU
    
    # Кнопки главного меню
    buttons = []
    button_texts = ["Войти", "Регистрация", "Выход"]
    button_colors = [LIGHT_BLUE, LIGHT_BLUE, RED]
    button_width = 400
    button_height = 60
    button_spacing = 40
    start_y = HEIGHT // 2 - ((button_height + button_spacing) * len(button_texts)) // 2 + 100 
    
    for i, text in enumerate(button_texts):
        x = WIDTH // 2 - button_width // 2
        y = start_y + i * (button_height + button_spacing)
        rect = pygame.Rect(x, y, button_width, button_height)
        buttons.append([text, rect, button_colors[i]])
    
    # Переменные для экрана входа
    login = ""
    password = ""
    active_login = False
    active_password = False
    cursor_visible = True
    cursor_timer = 0
    
    rect_login = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 40, 600, 60)
    rect_password = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 50, 600, 60)
    rect_login_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 160, 300, 60)
    back_button_login = pygame.Rect(50, 50, 100, 40)
    
    # Переменные для экрана регистрации
    username = ""
    email = ""
    reg_password = ""
    again_password = ""
    checked = False
    
    active_username = False
    active_email = False
    active_reg_password = False
    active_again_password = False
    
    rect_username = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 120, 600, 60)
    rect_email = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 50, 600, 60)
    rect_reg_password = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 20, 600, 60)
    rect_again_password_reg = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 + 90, 600, 60)
    rect_checkbox = pygame.Rect(WIDTH//2 - 290, HEIGHT//2 + 230, 20, 20)
    rect_register_button = pygame.Rect(WIDTH//2 - 150, HEIGHT//2 + 260, 300, 60)
    back_button_register = pygame.Rect(50, 50, 100, 40)
    
    # Создаем пикеры даты с современным интерфейсом
    date_picker_x = WIDTH//2 + 200 - 90  # Центрируем группу пикеров
    date_picker_y = HEIGHT//2 + 180
    picker_width = 80
    picker_height = 40
    
    day_picker = DatePicker(date_picker_x, date_picker_y, picker_width, picker_height, "День")
    day_picker.set_items([str(i).zfill(2) for i in range(1, 32)])  # 01, 02, ... 31
    
    month_picker = DatePicker(date_picker_x + picker_width + 10, date_picker_y, picker_width + 20, picker_height, "Месяц")
    month_picker.set_items(["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                           "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"])
    
    year_picker = DatePicker(date_picker_x + (picker_width + 10) * 2 + 20, date_picker_y, picker_width + 20, picker_height, "Год")
    year_picker.set_items([str(i) for i in range(1900, 2025)])
    
    # Переменные для экрана загрузки
    loading = False
    load_width = 0
    load_speed = 5
    block_width_load, block_height_load = 800, 600
    block_x_load = WIDTH // 2 - block_width_load // 2
    block_y_load = HEIGHT // 2 - block_height_load // 2
    load_bar_width = block_width_load - 200
    load_bar_height = 30
    load_x = block_x_load + 100
    load_y = block_y_load + block_height_load // 2 - load_bar_height // 2 + 50
    
    # Переменные для финального экрана загрузки
    final_loading = False
    final_load_width = 0
    final_load_speed = 2
    block_width_final, block_height_final = 800, 600
    block_x_final = WIDTH // 2 - block_width_final // 2
    block_y_final = HEIGHT // 2 - block_height_final // 2
    final_load_bar_width = block_width_final - 200
    final_load_bar_height = 30
    final_load_x = block_x_final + 100
    final_load_y = block_y_final + block_height_final // 2 - final_load_bar_height // 2
    final_yes_button_rect = None
    final_no_button_rect = None
    
    # Переменные для экрана "Как играть"
    show_how_to_play = True
    back_button_how_to_play = pygame.Rect(50, 50, 130, 40)
    pals_img_rect = None
    
    # Переменные для экрана выбора персонажа
    pocoyo_offset = 0
    nina_offset = 0
    HOVER_LIFT = 40
    LIFT_SPEED = 5
    selected_character = None
    
    # Переменные для экрана выбора языка
    block_size = [300, 300, 300, 300]
    hover_size = 350
    base_size = 300
    speed = 10
    selected_language = None
    
    # Переменные для анимации блоков с языками
    block_y_offsets = [0, 0, 0, 0]  # Смещение по Y для каждого блока
    HOVER_LIFT_LANG = -50  # Насколько поднимается блок при наведении
    LIFT_SPEED_LANG = 8    # Скорость поднятия
    clicked_block = -1     # Индекс нажатого блока (-1 = нет нажатого)
    
    # Экран настроек и профиля
    settings_screen = SettingsScreen()
    profile_screen = None
    
    # Кнопки игрового меню
    play_button_rect = None
    logout_button_rect = None
    
    # Кнопки подтверждения выхода
    yes_button_rect = None
    no_button_rect = None
    
    running = True
    
    while running:
        dt = clock.tick(60)
        cursor_timer += dt
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif current_state == STATE_MAIN_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for btn in buttons:
                        if btn[1].collidepoint(event.pos): 
                            if btn[0] == "Войти":
                                login = ""
                                password = ""
                                active_login = False
                                active_password = False
                                current_state = STATE_LOGIN
                            elif btn[0] == "Регистрация":
                                username = ""
                                email = ""
                                reg_password = ""
                                again_password = ""
                                checked = False
                                active_username = False
                                active_email = False
                                active_reg_password = False
                                active_again_password = False
                                day_picker.value = ""
                                month_picker.value = ""
                                year_picker.value = ""
                                day_picker.dropdown_open = False
                                month_picker.dropdown_open = False
                                year_picker.dropdown_open = False
                                current_state = STATE_REGISTER
                            elif btn[0] == "Выход":
                                current_state = STATE_EXIT_CONFIRM
                                
            elif current_state == STATE_LOGIN:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button_login.collidepoint(event.pos):
                        current_state = STATE_MAIN_MENU
                        continue
                        
                    active_login = rect_login.collidepoint(event.pos)
                    active_password = rect_password.collidepoint(event.pos)

                    if rect_login_button.collidepoint(event.pos):
                        if db_initialized:
                            success, result = login_player_in_db(login, password)
                            
                            if success:
                                print("Вход выполнен")
                                current_player = result
                                # Активируем экран загрузки
                                loading = True
                                load_width = 0
                                current_state = STATE_LOADING_SCREEN
                            else:
                                print(result)
                        else:
                            # Офлайн режим - тестовый вход
                            if login == "test" and password == "123456":
                                current_player = {'username': 'test', 'id': 1}
                                # Активируем экран загрузки
                                loading = True
                                load_width = 0
                                current_state = STATE_LOADING_SCREEN
                            else:
                                print("Неверные данные для офлайн режима")

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
                            
            elif current_state == STATE_REGISTER:
                # Обрабатываем события пикеров даты (они обрабатываются первыми)
                date_picker_handled = False
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEWHEEL:
                    if day_picker.handle_event(event, mouse_pos):
                        date_picker_handled = True
                    if month_picker.handle_event(event, mouse_pos):
                        date_picker_handled = True
                    if year_picker.handle_event(event, mouse_pos):
                        date_picker_handled = True
                
                if event.type == pygame.MOUSEBUTTONDOWN and not date_picker_handled:
                    if back_button_register.collidepoint(event.pos):
                        current_state = STATE_MAIN_MENU
                        continue
                        
                    active_username = rect_username.collidepoint(event.pos)
                    active_email = rect_email.collidepoint(event.pos)
                    active_reg_password = rect_reg_password.collidepoint(event.pos)
                    active_again_password = rect_again_password_reg.collidepoint(event.pos)

                    if rect_checkbox.collidepoint(event.pos):
                        checked = not checked

                    if rect_register_button.collidepoint(event.pos):
                        if not username:
                            print("Введите имя")
                            continue
                        if not email:
                            print("Введите email")
                            continue
                        if not reg_password:
                            print("Введите пароль")
                            continue
                        if reg_password != again_password:
                            print("Пароли не совпадают")
                            continue
                        if not checked:
                            print("Примите условия")
                            continue
                        if not day_picker.value or not month_picker.value or not year_picker.value:
                            print("Выберите дату рождения")
                            continue
                        
                        # Конвертируем месяц в число
                        months_ru = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", 
                                    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
                        try:
                            month_num = months_ru.index(month_picker.value) + 1
                            birth_date = year_picker.value + "-" + str(month_num).zfill(2) + "-" + str(int(day_picker.value)).zfill(2)
                        except:
                            print("Ошибка в дате рождения")
                            continue
                        
                        if db_initialized:
                            success, result = register_player_in_db(username, reg_password, email, birth_date)
                            
                            if success:
                                print("Регистрация успешна")
                                # Активируем экран загрузки
                                loading = True
                                load_width = 0
                                current_state = STATE_LOADING_SCREEN
                                
                                # Автоматический вход после регистрации
                                success_login, result_login = login_player_in_db(username, reg_password)
                                if success_login:
                                    current_player = result_login
                                else:
                                    # Если не удалось войти, используем имя из регистрации
                                    current_player = {'username': username, 'id': None}
                            else:
                                print(result)
                        else:
                            print("База недоступна")
                            # В офлайн режиме все равно переходим к загрузке
                            current_player = {'username': username, 'id': None}
                            loading = True
                            load_width = 0
                            current_state = STATE_LOADING_SCREEN

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
                    elif active_reg_password:
                        if event.key == pygame.K_BACKSPACE:
                            reg_password = reg_password[:-1]
                        else:
                            reg_password += event.unicode
                    elif active_again_password:
                        if event.key == pygame.K_BACKSPACE:
                            again_password = again_password[:-1]
                        else:
                            again_password += event.unicode
                
            elif current_state == STATE_HOW_TO_PLAY:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_button_how_to_play.collidepoint(event.pos):
                        # Переходим к игровому меню
                        current_state = STATE_GAME_MENU
                    
                    # Проверяем клик по картинке персонажа
                    if pals_img_rect and pals_img_rect.collidepoint(event.pos):
                        print("Переход к выбору персонажа")
                        current_state = STATE_CHARACTER_SELECT
                
            elif current_state == STATE_CHARACTER_SELECT:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pocoyo_rect, nina_rect, back_button = draw_character_select_screen(screen, mouse_pos, pocoyo_offset, nina_offset)
                    
                    # Проверяем клик по кнопке "Назад"
                    if back_button.collidepoint(event.pos):
                        current_state = STATE_HOW_TO_PLAY
                    
                    # Проверяем выбор персонажа
                    if pocoyo_rect.collidepoint(event.pos):
                        selected_character = "Pocoyo"
                        print(f"Выбран персонаж: {selected_character}")
                        current_state = STATE_LANGUAGE_SELECT
                    
                    if nina_rect.collidepoint(event.pos):
                        selected_character = "Nina"
                        print(f"Выбран персонаж: {selected_character}")
                        current_state = STATE_LANGUAGE_SELECT
            elif current_state == STATE_LANGUAGE_SELECT:
                    if event.type == pygame.MOUSEBUTTONDOWN:
        # Получаем блоки для проверки кликов
                        blocks_pos, labels, back_button, choose_button, setting_button_rect, block_rects = draw_language_select_screen(
            screen, mouse_pos, selected_character, block_size, block_y_offsets, clicked_block
        )
                        if back_button.collidepoint(event.pos):
                            block_y_offsets = [0, 0, 0, 0]
                            clicked_block = -1
                            selected_language = None
                            current_state = STATE_CHARACTER_SELECT
                        elif setting_button_rect.collidepoint(event.pos):
                            current_state = STATE_SETTINGS
                        elif choose_button.collidepoint(event.pos):
                            if not selected_language:
                                print("Сначала выберите язык программирования!")
                                continue
                            if not selected_character:
                                print("Сначала выберите персонажа!")
                                continue
                            final_loading = True
                            final_load_width = 0
                            current_state = STATE_FINAL_LOADING
                        for i, rect in enumerate(block_rects):
                            if rect.collidepoint(event.pos):
                                selected_language = labels[i]
                                clicked_block = i 
                                print(f"Выбран язык: {selected_language}")
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if clicked_block != -1:
                            pass

            elif current_state == STATE_SETTINGS:
    # Обработка событий для настроек
                result = settings_screen.handle_event(event, mouse_pos)
                if result == "back":
                    current_state = STATE_LANGUAGE_SELECT
                elif result == "open_profile":
                    profile_screen = ProfileScreen(selected_character)
                    current_state = STATE_PROFILE
                elif result == "lang":
                    settings_screen.lang_idx = (settings_screen.lang_idx + 1) % len(settings_screen.languages)
                    settings_screen.buttons[1].text = f"Язык: {settings_screen.languages[settings_screen.lang_idx]}"
                elif result == "music":
                    settings_screen.music = not settings_screen.music
                    settings_screen.buttons[2].text = "Музыка: Включена" if settings_screen.music else "Музыка: Выключена"

            elif current_state == STATE_PROFILE and profile_screen:
    # Обработка событий для профиля
                result = profile_screen.handle_event(event, mouse_pos)
                if result == "back":
                    current_state = STATE_SETTINGS
                elif result == "choose_character":
        # Возвращаемся к выбору языка с уже выбранным персонажем
                    current_state = STATE_LANGUAGE_SELECT
                
            elif current_state == STATE_LOADING_SCREEN:
                # Обновляем прогресс загрузки
                if loading:
                    if load_width < load_bar_width:
                        load_width += load_speed
                    else:
                        # Загрузка завершена
                        loading = False
                        
                        # Загружаем статистику игрока (если есть подключение)
                        player_id = None
                        if current_player and isinstance(current_player, dict):
                            player_id = current_player.get('id')
                        player_stats = get_player_stats_from_db(player_id)
                        
                        # Если нужно показать экран "Как играть"
                        if show_how_to_play:
                            current_state = STATE_HOW_TO_PLAY
                            show_how_to_play = False  # Показываем только один раз
                        else:
                            current_state = STATE_GAME_MENU
            
            elif current_state == STATE_FINAL_LOADING:
                # Обновляем прогресс загрузки
                if final_loading:
                    if final_load_width < final_load_bar_width:
                        final_load_width += final_load_speed
                    else:
                        # Загрузка завершена - ждем нажатия кнопки
                        final_loading = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Получаем актуальные прямоугольники кнопок
                    final_yes_button_rect, final_no_button_rect = draw_final_loading_screen(
                        screen, final_load_width, final_load_bar_width, final_load_bar_height,
                        final_load_x, final_load_y, block_width_final, block_height_final,
                        block_x_final, block_y_final, mouse_pos, selected_character, selected_language
                    )
                    
                    # Проверяем клик по кнопке ДА
                    if final_yes_button_rect and final_yes_button_rect.collidepoint(event.pos):
                        print("=" * 60)
                        print("ЗАПУСК ИГРЫ")
                        print("=" * 60)
                        
                        try:
                            script_dir = os.path.dirname(os.path.abspath(__file__))
                            
                            # Проверяем, что все выбрано
                            if not selected_character:
                                print("ОШИБКА: Не выбран персонаж!")
                                continue
                            
                            if not selected_language:
                                print("ОШИБКА: Не выбран язык программирования!")
                                continue
                            
                            # Получаем имя файла игры
                            game_file_key = (selected_character, selected_language)
                            game_file_name = GAME_FILES_MAPPING.get(game_file_key)
                            
                            if not game_file_name:
                                print(f"ОШИБКА: Нет файла для комбинации:")
                                print(f"  Персонаж: {selected_character}")
                                print(f"  Язык: {selected_language}")
                                continue
                            
                            # Полный путь к файлу
                            game_path = os.path.join(script_dir, game_file_name)
                            
                            # Проверяем существование файла
                            if not os.path.exists(game_path):
                                print(f"ОШИБКА: Файл не найден: {game_path}")
                                print(f"Проверьте, что файл {game_file_name} существует в папке")
                                continue
                            
                            print(f"✓ Персонаж: {selected_character}")
                            print(f"✓ Язык программирования: {selected_language}")
                            print(f"✓ Файл игры: {game_file_name}")
                            print(f"✓ Путь: {game_path}")
                            
                            # Сохраняем конфигурацию игрока (БЕЗ БД)
                            player_config = {
                                'selected_character': selected_character,
                                'selected_language': selected_language,
                                'player_name': current_player.get('username') if isinstance(current_player, dict) else 'Гость',
                                'player_id': current_player.get('id') if isinstance(current_player, dict) else None,
                                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            
                            # Сохраняем в файл
                            config_file = os.path.join(script_dir, 'player_config.json')
                            with open(config_file, 'w', encoding='utf-8') as f:
                                json.dump(player_config, f, ensure_ascii=False, indent=2)
                            
                            print(f"✓ Конфигурация сохранена в: {config_file}")
                            
                            # Запускаем игру
                            print("=" * 60)
                            print("🚀 ЗАПУСКАЕМ ИГРУ...")
                            print("=" * 60)
                            
                            # Пауза для чтения сообщений
                            pygame.time.delay(1000)
                            
                            # Запускаем игру как отдельный процесс
                            process = subprocess.Popen([sys.executable, game_path])
                            
                            # Можно оставить меню открытым или перейти в другое состояние
                            current_state = STATE_GAME_MENU
                            
                            print(f"✓ Игра запущена (PID: {process.pid})")
                            print("=" * 60)
                            
                        except Exception as e:
                            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ:")
                            print(str(e))
                            import traceback
                            traceback.print_exc()
                            print("=" * 60)
                    
                    # Проверяем клик по кнопке НЕТ
                    elif final_no_button_rect and final_no_button_rect.collidepoint(event.pos):
                        # Возвращаемся к выбору языка
                        current_state = STATE_LANGUAGE_SELECT
                        final_loading = False
                        final_load_width = 0

            elif current_state == STATE_GAME_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_button_rect and play_button_rect.collidepoint(event.pos):
                        print("Начинаем игру")
                        # Здесь можно добавить переход к выбору языка/уровня
                        
                    elif logout_button_rect and logout_button_rect.collidepoint(event.pos):
                        current_player = None
                        player_stats = None
                        selected_character = None
                        selected_language = None
                        current_state = STATE_MAIN_MENU
            
            elif current_state == STATE_EXIT_CONFIRM:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if yes_button_rect and yes_button_rect.collidepoint(event.pos):
                        running = False
                    elif no_button_rect and no_button_rect.collidepoint(event.pos):
                        current_state = STATE_MAIN_MENU
        
        # Обновляем анимацию поднятия персонажей
        if current_state == STATE_CHARACTER_SELECT:
            mx, my = mouse_pos
            
            # Проверяем наведение на персонажей
            pocoyo_x = WIDTH // 2 - 900 // 2 - 550
            pocoyo_y = HEIGHT // 2 - 570 // 2 + 80 + pocoyo_offset
            pocoyo_rect = pygame.Rect(pocoyo_x, pocoyo_y, 900, 570)
            
            nina_x = WIDTH // 2 - 900 // 2 + 550
            nina_y = HEIGHT // 2 - 570 // 2 + 80 + nina_offset
            nina_rect = pygame.Rect(nina_x, nina_y, 900, 570)
            
            if pocoyo_rect.collidepoint(mx, my):
                if pocoyo_offset > -HOVER_LIFT:
                    pocoyo_offset -= LIFT_SPEED
            else:
                if pocoyo_offset < 0:
                    pocoyo_offset += LIFT_SPEED

            if nina_rect.collidepoint(mx, my):
                if nina_offset > -HOVER_LIFT:
                    nina_offset -= LIFT_SPEED
            else:
                if nina_offset < 0:
                    nina_offset += LIFT_SPEED
        # Обновляем анимацию блоков с языками
        if current_state == STATE_LANGUAGE_SELECT:
            mx, my = mouse_pos
            blocks_pos = [
        (WIDTH // 2 - 550, HEIGHT // 2),  # SQL
        (WIDTH // 2 - 200, HEIGHT // 2),  # Python
        (WIDTH // 2 + 150, HEIGHT // 2),  # C#
        (WIDTH // 2 + 500, HEIGHT // 2)   # Java
    ]
    
            for i, (bx, by) in enumerate(blocks_pos):
                size = block_size[i]
                rect = pygame.Rect(
                bx - size // 2, by - size // 2 + block_y_offsets[i], size, size
        )
        
        # Если этот блок нажат (кликнут), не двигаем его
                if i == clicked_block:
            # Оставляем блок поднятым пока он выбран
                    if block_y_offsets[i] > HOVER_LIFT_LANG:
                        block_y_offsets[i] = HOVER_LIFT_LANG
                        continue
        
        # Проверяем наведение мыши на другие блоки
                if rect.collidepoint(mx, my):
            # Поднимаем блок при наведении
                    if block_y_offsets[i] > HOVER_LIFT_LANG:
                        block_y_offsets[i] -= LIFT_SPEED_LANG
                else:
            # Опускаем блок, если не наведено
                    if block_y_offsets[i] < 0:
                        block_y_offsets[i] += LIFT_SPEED_LANG
        
        # Анимация увеличения при наведении
                if rect.collidepoint(mx, my):
                    if size < hover_size:
                        block_size[i] += speed
                else:
                    if size > base_size:
                        block_size[i] -= speed
        
        
        # Обработка отпускания нажатого блока с языком
        if current_state == STATE_LANGUAGE_SELECT and clicked_block != -1:
            # Медленно опускаем нажатый блок обратно
            if block_y_offsets[clicked_block] < 0:
                block_y_offsets[clicked_block] += LIFT_SPEED_LANG // 2
            else:
                # Если блок полностью опустился, сбрасываем clicked_block
                block_y_offsets[clicked_block] = 0
                clicked_block = -1
        
        # Отрисовка в зависимости от текущего состояния
        if current_state == STATE_MAIN_MENU:
            draw_main_menu(screen, mouse_pos, buttons)
        elif current_state == STATE_LOGIN:
            draw_login_screen(screen, login, password, active_login, active_password, cursor_visible, 
                             rect_login, rect_password, rect_login_button, back_button_login)
        elif current_state == STATE_REGISTER:
            draw_register_screen(screen, username, email, reg_password, again_password, checked,
                               active_username, active_email, active_reg_password, active_again_password,
                               cursor_visible, rect_username, rect_email, rect_reg_password,
                               rect_again_password_reg, rect_checkbox, rect_register_button, 
                               back_button_register, day_picker, month_picker, year_picker)
        elif current_state == STATE_HOW_TO_PLAY:
            back_button_how_to_play, pals_img_rect = draw_how_to_play_screen(screen, mouse_pos, back_button_how_to_play, pals_img_rect)
        elif current_state == STATE_CHARACTER_SELECT:
            pocoyo_rect, nina_rect, back_button = draw_character_select_screen(screen, mouse_pos, pocoyo_offset, nina_offset)
        elif current_state == STATE_LANGUAGE_SELECT:
            blocks_pos, labels, back_button, choose_button, setting_button_rect, block_rects = draw_language_select_screen(
        screen, mouse_pos, selected_character, block_size, block_y_offsets, clicked_block
    )
        elif current_state == STATE_LOADING_SCREEN:
            # Получаем имя игрока для отображения
            player_name = ""
            if current_player and isinstance(current_player, dict):
                player_name = current_player.get('username', '')
            
            draw_loading_screen(screen, player_name, load_width, load_bar_width, load_bar_height, 
                               load_x, load_y, block_width_load, block_height_load, 
                               block_x_load, block_y_load)
        elif current_state == STATE_FINAL_LOADING:
            final_yes_button_rect, final_no_button_rect = draw_final_loading_screen(
                screen, final_load_width, final_load_bar_width, final_load_bar_height,
                final_load_x, final_load_y, block_width_final, block_height_final,
                block_x_final, block_y_final, mouse_pos, selected_character, selected_language
            )
        elif current_state == STATE_SETTINGS:
            settings_screen.draw(screen)
        elif current_state == STATE_PROFILE and profile_screen:
            profile_screen.draw(screen)
        elif current_state == STATE_EXIT_CONFIRM:
            yes_button_rect, no_button_rect = draw_exit_confirmation(screen, mouse_pos)
        
        pygame.display.update()
    
    # Закрываем соединение с БД если оно было
    if db_connected and db and hasattr(db, 'disconnect'):
        try:
            db.disconnect()
            print("Соединение с БД закрыто")
        except Exception as e:
            print(f"Ошибка при закрытии соединения с БД: {e}")
    
    pygame.quit()
    sys.exit()
    

if __name__ == "__main__":
    main()