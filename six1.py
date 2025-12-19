import pygame
import sys
import random
import math
import time

from db_questions_utils import load_questions_for_language

pygame.init()
WIDTH, HEIGHT = 1920, 1080 
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ÖSU DOS - игра")
BLUE = (14, 137, 185)
WHITE = (255, 255, 255)
BLUE_BTN = (9, 133, 230)
BLUE_HOVER = (12, 155, 255)
GREEN = (40, 200, 40)
RED = (220, 50, 50)

# Загрузка изображений
background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Текст абзаца (2).png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))
end_background = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Group 22 (1).png")
end_background = pygame.transform.scale(end_background, (WIDTH, HEIGHT))

platform_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (80).webp")
coin_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Текст_абзаца__3_-removebg-preview.png").convert_alpha()
coin_img = pygame.transform.smoothscale(coin_img, (150,150))
image1 = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (81).webp")
image2 = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (82).webp")
scroll_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (78).webp").convert_alpha()
scroll_img = pygame.transform.smoothscale(scroll_img, (80, 80))

# Загрузка изображения бумаги для вопросов
paper_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (68) 1.png")
paper_img = pygame.transform.scale(paper_img, (1200, 800))

heart1_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\sticker (84).webp").convert_alpha()
heart1_img = pygame.transform.smoothscale(heart1_img, (50, 50))

gray_heart_img = heart1_img.copy()
gray_heart_img.fill((100, 100, 100, 180), special_flags=pygame.BLEND_RGBA_MULT)

coin_ui_img = pygame.image.load("C:\\Users\\aiz\\OneDrive\\Desktop\\osudos\\Текст_абзаца__3_-removebg-preview.png").convert_alpha()
coin_ui_img = pygame.transform.smoothscale(coin_ui_img, (80, 80))

image1 = pygame.transform.smoothscale(image1, (100, 150))
image2 = pygame.transform.smoothscale(image2, (100, 150))

# Состояния игры
STATE_INTRO = "intro"
STATE_PLAY = "play"
STATE_QUESTION = "question"
STATE_FALL = "fall"
STATE_COUNTDOWN = "countdown"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_FINISH = "finish"
STATE_LEVEL_START = "level_start"
STATE_WIN_SCREEN = "win_screen"
STATE_LOSE_SCREEN = "lose_screen"
STATE_RESULTS = "results"  # Новое состояние - результаты

game_state = STATE_LEVEL_START
game_started = False

# Фон
x1 = 0
speed = 8
x2 = WIDTH

# Игрок
player_width = 80
player_height = 150
player_x = WIDTH // 2 - 40
player_y = HEIGHT - 450
player_vel_y = 0
player_speed = 12
jump_power = -25
gravity = 1.2
is_jumping = False
on_ground = False
facing_right = True
coins_collected = 0

# Здоровье
hearts = 5
max_hearts = 5
lose_life_timer = 0
lose_life_duration = 90
respawn_timer = 0
respawn_countdown = 180
respawn_count = 3
is_respawning = False
respawn_platform = None
player_hit_timer = 0
player_alpha = 255
player_death_animation = False
death_animation_timer = 0

has_stepped_on_platform = False
was_on_air = False

# Уровни
current_level = 1
tasks_done = 0
max_tasks = 3  # это максимум заданий на уровень, но реально берем min( max_tasks, кол-во вопросов в БД )
level_change_timer = 0
level_changed = False

# Вопросы из базы данных
DB_LANGUAGE_NAME = "SQL"  # язык программирования, для которого берем вопросы
questions = {1: [], 2: [], 3: []}  # сюда загрузим вопросы из БД

# Анимация текста уровня
level_start_timer = 180
level_text_alpha = 0
level_text_scale = 0.5
level_text_growing = True

# Анимация для экранов конца игры
win_scale = 0.1
win_target_scale = 1
win_scale_speed = 0.02
lose_scale = 0.1
lose_target_scale = 1
lose_scale_speed = 0.02

# Цвета для экрана результатов
RESULTS_BLUE = (0, 102, 204)
RESULTS_GREEN = (0, 180, 0)
RESULTS_RED = (200, 50, 50)
DARK_GRAY = (50, 50, 50) 
BLOCK_BG_COLOR = (255, 255, 255, 255) 
LIGHT_GRAY = (255, 255, 255, 255) 

# Шрифты для экрана результатов
font_title = pygame.font.SysFont("arial", 90, True)
font_label = pygame.font.SysFont("arial", 35, True) 
font_number = pygame.font.SysFont("arial", 95, True) 
font_detail_title = pygame.font.SysFont("arial", 60, True) 
font_detail = pygame.font.SysFont("arial", 35) 
font_small = pygame.font.SysFont("arial", 30)
font_question = pygame.font.SysFont("arial", 28)

# Переменные для отслеживания ответов
question_history = []  # Здесь будем хранить историю всех ответов
all_questions_list = []  # Список всех вопросов которые были в игре
correct_count = 0
wrong_count = 0

# Переменные для двойного нажатия
last_tap_time = 0
double_tap_threshold = 300  # 300 мс для двойного нажатия

# Переменные для прокрутки
scroll_offset = 0
max_scroll_offset = 0
scroll_speed = 20
is_dragging = False
drag_start_y = 0

current_question = None
question_active = False
selected_answer = -1
answer_selected = False

# Таймер для показа результата вопроса (2 секунды)
question_result_timer = 0
question_result_duration = 120  # 2 секунды при 60 FPS
show_all_colors = False  # Показываем все цвета или только выбранный

# Прямоугольники для кнопок ответов
answer_rects = [
    pygame.Rect(570, 500, 350, 110),
    pygame.Rect(1000, 500, 350, 110),
    pygame.Rect(570, 650, 350, 110),
    pygame.Rect(1000, 650, 350, 110),
]

# Переменные для экрана результатов
current_view = "MAIN" 
DETAIL_VIEW_RECT = pygame.Rect(100, 180, WIDTH - 200, HEIGHT - 240) 
detail_box = {"active": False, "data_type": None}
current_data = [] 
current_page = 0
items_per_page = 4 
BACK_BUTTON_RECT = pygame.Rect(50, 30, 200, 60)
results_frame = 0

# Блоки для отображения статистики
result_boxes = []

current_letter = None
letter_active = False

FLOOR_HEIGHT = HEIGHT - 180

# Анимация
animation_counter = 0
animation_speed = 5
current_image = image1
is_walking = False
idle_animation_active = True

platforms = []
platform_count = 15
start_x = WIDTH + 200
gap_x = 450
heights = [HEIGHT - 355, HEIGHT - 465, HEIGHT - 520, HEIGHT - 465, HEIGHT - 355, HEIGHT - 465, HEIGHT - 355]

background_counter = 0
letter_for_current_bg_spawned = False

def init_platforms():
    global platforms, has_stepped_on_platform, game_started, letter_for_current_bg_spawned, current_letter, tasks_done, player_x, player_y
    
    platforms = []
    has_stepped_on_platform = False
    game_started = False
    letter_for_current_bg_spawned = False
    current_letter = None
    tasks_done = 0
    
    height_index = 0
    for i in range(platform_count):
        w = random.randint(200, 350)
        h = 70
        x = start_x + i * gap_x
        y = heights[height_index]
        height_index = (height_index + 1) % len(heights)
        rect = pygame.Rect(x, y, w, h)
        coin = None
        if random.random() < 0.5:
            min_x = rect.x + 20
            max_x = rect.x + rect.width - 80
            if max_x > min_x:
                coin_x = random.randint(min_x, max_x)
                coin_y = rect.y - 150
                coin = pygame.Rect(coin_x, coin_y, 80, 80)
        platforms.append({"rect": rect, "coin": coin})
    
    if current_level >= 2 and len(platforms) > 0:
        first_platform = platforms[0]["rect"]
        player_x = first_platform.x + first_platform.width // 2 - player_width // 2
        player_y = first_platform.top - player_height
        has_stepped_on_platform = True
    else:
        player_x = WIDTH // 2 - 40
        player_y = HEIGHT - 450
        has_stepped_on_platform = False

def spawn_letter():
    global current_letter, letter_active, letter_for_current_bg_spawned
    
    if not letter_for_current_bg_spawned and len(platforms) > 0:
        valid_platforms = []
        for p in platforms:
            if p["rect"].x > player_x + 100:
                valid_platforms.append(p)
        
        if valid_platforms:
            platform = None
            if len(valid_platforms) > 2:
                platform = valid_platforms[len(valid_platforms) // 2]
            else:
                platform = valid_platforms[0]
            
            rect = platform["rect"]
            min_x = rect.x + 30
            max_x = rect.x + rect.width - 80
            if max_x > min_x:
                letter_x = random.randint(min_x, max_x)
                letter_y = rect.y - 120
                current_letter = pygame.Rect(letter_x, letter_y, 80, 100)
                letter_active = True
                letter_for_current_bg_spawned = True
        else:
            if len(platforms) > 0:
                platform = platforms[0]
                rect = platform["rect"]
                min_x = rect.x + 30
                max_x = rect.x + rect.width - 80
                if max_x > min_x:
                    letter_x = random.randint(min_x, max_x)
                    letter_y = rect.y - 120
                    current_letter = pygame.Rect(letter_x, letter_y, 80, 100)
                    letter_active = True
                    letter_for_current_bg_spawned = True

def check_platform_collision(player_rect, platform_rect, player_vel_y):
    if player_vel_y >= 0:
        if player_rect.colliderect(platform_rect):
            bottom_to_top = player_rect.bottom - platform_rect.top
            if 0 <= bottom_to_top <= 30:
                if (player_rect.right > platform_rect.left + 10 and 
                    player_rect.left < platform_rect.right - 10):
                    return True
    return False

def check_coin_collision(player_rect, coin_rect):
    return player_rect.colliderect(coin_rect)

def check_letter_collision(player_rect, letter_rect):
    return player_rect.colliderect(letter_rect)

def start_death_animation():
    global player_death_animation, death_animation_timer, player_alpha
    player_death_animation = True
    death_animation_timer = 90
    player_alpha = 255

def lose_life():
    global hearts, lose_life_timer, is_respawning, respawn_timer, respawn_platform, player_hit_timer
    
    if hearts > 0 and player_hit_timer <= 0 and has_stepped_on_platform:
        hearts -= 1
        lose_life_timer = lose_life_duration
        player_hit_timer = 60
        
        start_death_animation()
        
        respawn_platform = None
        player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
        
        current_platform_index = -1
        for i, p in enumerate(platforms):
            if check_platform_collision(player_rect, p["rect"], 0):
                current_platform_index = i
                break
        
        if current_platform_index >= 1:
            respawn_platform = platforms[current_platform_index - 1]["rect"]
        elif current_platform_index >= 0:
            respawn_platform = platforms[0]["rect"]
        else:
            for p in reversed(platforms):
                if p["rect"].x < player_x:
                    respawn_platform = p["rect"]
                    break
        
        if not respawn_platform and len(platforms) > 0:
            respawn_platform = platforms[0]["rect"]
        
        is_respawning = True
        respawn_timer = respawn_countdown
        return True
    return False

def change_level(new_level):
    global current_level, has_stepped_on_platform, background_counter, letter_for_current_bg_spawned, player_x, player_y, player_vel_y, is_jumping, on_ground, tasks_done, game_state, game_started, current_letter, letter_active, x1, x2, is_respawning, game_paused, idle_animation_active, level_start_timer, level_text_alpha, level_text_scale, level_text_growing, question_result_timer, show_all_colors, question_active, selected_answer, answer_selected
    
    current_level = new_level
    
    # Пересчитываем лимит заданий на уровень по количеству вопросов в БД
    global max_tasks
    level_questions = questions.get(current_level, [])
    if level_questions:
        max_tasks = min(3, len(level_questions))
    else:
        max_tasks = 0
    
    player_vel_y = 0
    is_jumping = False
    on_ground = False
    
    x1 = 0
    x2 = WIDTH
    
    has_stepped_on_platform = False
    game_started = False
    letter_for_current_bg_spawned = False
    background_counter = 0
    
    current_letter = None
    letter_active = False
    tasks_done = 0
    
    is_respawning = False
    game_paused = False
    idle_animation_active = True
    
    # Сброс состояния вопросов
    question_active = False
    selected_answer = -1
    answer_selected = False
    question_result_timer = 0
    show_all_colors = False
    
    level_start_timer = 180
    level_text_alpha = 0
    level_text_scale = 0.5
    level_text_growing = True
    
    init_platforms()
    
    game_state = STATE_LEVEL_START

def show_question():
    global game_state, current_question, question_active, current_letter, letter_active, selected_answer, idle_animation_active, answer_selected, question_result_timer, show_all_colors
    
    level_questions = questions.get(current_level, [])
    if tasks_done < len(level_questions):
        current_question = level_questions[tasks_done]
        game_state = STATE_QUESTION
        question_active = True
        selected_answer = -1
        answer_selected = False
        question_result_timer = 0
        show_all_colors = False
        idle_animation_active = False
        
        current_letter = None
        letter_active = False

def handle_question_input():
    global game_state, tasks_done, question_active, selected_answer, current_level, idle_animation_active, hearts, answer_selected, question_result_timer, show_all_colors, question_history, correct_count, wrong_count, all_questions_list
    
    if not question_active or not current_question:
        return
    
    mouse = pygame.mouse.get_pos()
    mouse_clicked = pygame.mouse.get_pressed()[0]
    
    # Проверяем клик по кнопкам ответов
    if mouse_clicked and not answer_selected:
        for i, rect in enumerate(answer_rects):
            if rect.collidepoint(mouse):
                selected_answer = i
                answer_selected = True
                show_all_colors = True  # Показываем ВСЕ цвета сразу
                question_result_timer = question_result_duration  # Запускаем таймер (2 секунды)
                
                # Помечаем вопрос как отвеченный
                current_question["answered"] = True
                current_question["user_answer"] = selected_answer
                current_question["is_correct"] = (selected_answer == current_question["correct"])
                
                # Добавляем в список всех вопросов игры (если еще не добавлен)
                question_found = False
                for q in all_questions_list:
                    if q["question"] == current_question["question"]:
                        question_found = True
                        break
                
                if not question_found:
                    all_questions_list.append({
                        "id": len(all_questions_list) + 1,
                        "question": current_question["question"],
                        "answers": current_question["answers"],
                        "correct_answer": current_question["answers"][current_question["correct"]],
                        "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                        "is_correct": current_question["is_correct"],
                        "correct_index": current_question["correct"],
                        "user_index": selected_answer
                    })
                
                # Сохраняем в историю ответов для текущего вопроса
                question_history.append({
                    "id": len(question_history) + 1,
                    "text": current_question["question"],
                    "is_correct": current_question["is_correct"],
                    "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                    "correct_answer": current_question["answers"][current_question["correct"]] if 0 <= current_question["correct"] < len(current_question["answers"]) else "Ошибка",
                    "user_index": selected_answer,
                    "correct_index": current_question["correct"]
                })
                
                # ИЗМЕНЕНИЕ 1: Вопрос всегда считается пройденным, даже если ответ неправильный
                tasks_done += 1  # Всегда увеличиваем счетчик выполненных заданий
                
                if selected_answer == current_question["correct"]:
                    correct_count += 1
                    print(f"Правильный ответ! Заданий выполнено: {tasks_done}/{max_tasks}")
                else:
                    lose_life()
                    wrong_count += 1
                    print(f"Неправильный ответ! Теряем жизнь. Заданий выполнено: {tasks_done}/{max_tasks}")
                break

def start_game():
    global game_started, letter_for_current_bg_spawned
    if not game_started and has_stepped_on_platform:
        game_started = True
        letter_for_current_bg_spawned = False
        spawn_letter()

def draw_win_screen():
    global win_scale
    
    screen.blit(end_background, (0, 0))
    
    # Анимация увеличения текста
    if win_scale < win_target_scale:
        win_scale += win_scale_speed
    
    current_size = int(180 * win_scale)
    current_size = max(5, current_size)
    font = pygame.font.SysFont("notable", current_size, bold=True)
    
    text = "ВЫ ПОБЕДИЛИ!"
    
    text_surface = font.render(text, True, (255, 215, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    # Обводка текста
    outline_color = (255, 255, 255)
    offsets = [(-6, 0), (6, 0), (0, -6), (0, 6)]
    
    for ox, oy in offsets:
        outline = font.render(text, True, outline_color)
        outline_rect = outline.get_rect(center=(WIDTH // 2 + ox, HEIGHT // 2 + oy))
        screen.blit(outline, outline_rect)
    
    screen.blit(text_surface, text_rect)
    
    # Текст для продолжения
    continue_font = pygame.font.Font(None, 40)
    continue_text = continue_font.render("Нажмите ПРОБЕЛ чтобы увидеть результаты", True, (255, 255, 255))
    continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
    screen.blit(continue_text, continue_rect)

def draw_lose_screen():
    global lose_scale
    
    screen.blit(end_background, (0, 0))
    
    # Анимация увеличения текста
    if lose_scale < lose_target_scale:
        lose_scale += lose_scale_speed
    
    current_size = int(140 * lose_scale)
    current_size = max(5, current_size)
    font = pygame.font.SysFont("notable", current_size, bold=True)
    
    text1 = "НЕ ПОВЕЗЛО"
    text2 = "ВЫ ПРОИГРАЛИ!"
    
    color = (220, 0, 0)
    outline_color = (255, 255, 255)
    
    t1 = font.render(text1, True, color)
    t2 = font.render(text2, True, color)
    
    t1_rect = t1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
    t2_rect = t2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
    
    # Обводка текста
    offsets = [(-6, 0), (6, 0), (0, -6), (0, 6)]
    
    for ox, oy in offsets:
        s1 = font.render(text1, True, outline_color)
        s1_rect = s1.get_rect(center=(WIDTH // 2 + ox, HEIGHT // 2 - 100 + oy))
        screen.blit(s1, s1_rect)
        
        s2 = font.render(text2, True, outline_color)
        
        s2_rect = s2.get_rect(center=(WIDTH // 2 + ox, HEIGHT // 2 + 80 + oy))
        screen.blit(s2, s2_rect)
    
    screen.blit(t1, t1_rect)
    screen.blit(t2, t2_rect)
    
    # Текст для возврата
    back_font = pygame.font.Font(None, 40)
    back_text = back_font.render("Нажмите ESC для выхода или R для рестарта", True, (255, 255, 255))
    back_rect = back_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
    screen.blit(back_text, back_rect)

def prepare_results_data():
    """Подготавливает данные для экрана результатов"""
    global all_questions_list, correct_count, wrong_count, result_boxes, max_scroll_offset
    
    # Подсчитываем правильные и неправильные ответы из всех вопросов
    total_questions = len(all_questions_list)
    correct_count = 0
    wrong_count = 0
    
    for question in all_questions_list:
        if question["is_correct"]:
            correct_count += 1
        else:
            wrong_count += 1
    
    # Создаем блоки для отображения
    result_boxes = [
        {"x": 250, "y": 450, "w": 420, "h": 260, "title": "ВСЕГО", "num": str(total_questions), "color": RESULTS_BLUE, "phase": 0, "rect": pygame.Rect(250, 450, 420, 260), "type": "total"},
        {"x": 750, "y": 450, "w": 420, "h": 260, "title": "ПРАВИЛЬНЫЕ", "num": f"{correct_count}/{total_questions}", "color": RESULTS_GREEN, "phase": 2, "rect": pygame.Rect(750, 450, 420, 260), "type": "correct"},
        {"x": 1250, "y": 450, "w": 420, "h": 260, "title": "НЕПРАВИЛЬНЫЕ", "num": f"{wrong_count}/{total_questions}", "color": RESULTS_RED, "phase": 4, "rect": pygame.Rect(1250, 450, 420, 260), "type": "wrong"}
    ]
    
    # Рассчитываем максимальную прокрутку
    total_questions_height = len(all_questions_list) * 200  # Высота каждого вопроса
    max_scroll_offset = max(0, total_questions_height - 600)  # 600 - высота видимой области

def draw_text_multiline(surface, text, font, color, rect, x_offset=29):
    """Отрисовывает многострочный текст"""
    line_spacing = 5
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        if font.size(' '.join(current_line + [word]))[0] < rect.width - 2 * x_offset:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    
    y = rect.top + 10 
    for line in lines:
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (rect.left + x_offset, y))
        y += text_surface.get_height() + line_spacing
        if y > rect.bottom: 
             break
    return y

def draw_results_box(box, offset_y):
    """Отрисовывает блок статистики"""
    x, y, w, h = box["x"], box["y"] + offset_y, box["w"], box["h"]
    box["rect"].y = y

    box_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(box_surface, BLOCK_BG_COLOR, (0, 0, w, h), border_radius=40)
    screen.blit(box_surface, (x, y))

    pygame.draw.rect(screen, box["color"], (x, y, w, h), border_radius=40, width=5) 

    label = font_label.render(box["title"], True, RESULTS_BLUE)
    screen.blit(label, (x + w/2 - label.get_width()/2, y + 40)) 

    number = font_number.render(box["num"], True, box["color"])
    screen.blit(number, (x + w/2 - number.get_width()/2, y + 100))



def draw_question_item(q, idx, x, y, width):
    """Отрисовывает один вопрос в списке"""
    # Фон вопроса
    question_rect = pygame.Rect(x, y, width, 170)
    
    # Цвет фона в зависимости от правильности ответа
    if q["is_correct"]:
        bg_color = (0, 180, 0, 100)  # Зеленый для правильных
    else:
        bg_color = (200, 50, 50, 100)  # Красный для неправильных
    
    pygame.draw.rect(screen, bg_color, question_rect, border_radius=15)
    pygame.draw.rect(screen, WHITE, question_rect, border_radius=15, width=2)
    
    # Номер вопроса
    num_font = pygame.font.Font(None, 36)
    num_text = num_font.render(f"{idx + 1}.", True, WHITE)
    screen.blit(num_text, (x + 20, y + 15))
    
    # Текст вопроса (обрезаем если длинный)
    question_font = pygame.font.Font(None, 32)
    question_text = q["question"]
    if len(question_text) > 80:
        question_text = question_text[:80] + "..."
    
    question_surface = question_font.render(question_text, True, WHITE)
    screen.blit(question_surface, (x + 60, y + 15))
    
    # Статус ответа
    status_font = pygame.font.Font(None, 30)
    if q["is_correct"]:
        status_text = status_font.render("✓ Правильный ответ", True, RESULTS_GREEN)
    else:
        status_text = status_font.render("✗ Неправильный ответ", True, RESULTS_RED)
    
    screen.blit(status_text, (x + 60, y + 55))
    
    # Ответ пользователя
    user_answer_text = status_font.render(f"Ваш ответ: {q['user_answer']}", True, WHITE)
    screen.blit(user_answer_text, (x + 60, y + 90))
    
    # Правильный ответ (только для неправильных)
    if not q["is_correct"]:
        correct_answer_text = status_font.render(f"Правильный: {q['correct_answer']}", True, RESULTS_GREEN)
        screen.blit(correct_answer_text, (x + 60, y + 120))
    
    # Сохраняем прямоугольник вопроса для обработки кликов
    q["rect"] = question_rect

def draw_detail_screen():
    """Отрисовывает детальный экран с вопросами"""
    x, y, w, h = DETAIL_VIEW_RECT.x, DETAIL_VIEW_RECT.y, DETAIL_VIEW_RECT.width, DETAIL_VIEW_RECT.height
    
    detail_surface = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(detail_surface, LIGHT_GRAY, (0, 0, w, h), border_radius=40)
    pygame.draw.rect(detail_surface, RESULTS_BLUE, (0, 0, w, h), border_radius=40, width=5) 
    screen.blit(detail_surface, (x, y))
    
    if detail_box["data_type"] == "correct":
        title = font_detail_title.render("ПРАВИЛЬНЫЕ ОТВЕТЫ", True, RESULTS_GREEN)
        detail_color = RESULTS_GREEN
    elif detail_box["data_type"] == "wrong":
        title = font_detail_title.render("НЕПРАВИЛЬНЫЕ ОТВЕТЫ", True, RESULTS_RED)
        detail_color = RESULTS_RED
    else:
        title = font_detail_title.render("ВСЕ ВОПРОСЫ", True, RESULTS_BLUE)
        detail_color = RESULTS_BLUE
         
    screen.blit(title, (x + w/2 - title.get_width()/2, y + 20))

    text_rect = pygame.Rect(x + 60, y + 100, w - 80, h - 140)
    
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page
    display_questions = current_data[start_index:end_index]
    
    current_y = text_rect.top
    
    for q in display_questions:
        question_text = f"Вопрос {q['id']}: {q['question']}"
        current_y = draw_text_multiline(screen, question_text, font_detail, DARK_GRAY, pygame.Rect(text_rect.x + 30, current_y, text_rect.width - 30, 100))

        # Отображаем все варианты ответов
        answers_text = "Варианты ответов:"
        current_y = draw_text_multiline(screen, answers_text, font_small, DARK_GRAY, pygame.Rect(text_rect.x + 30, current_y, text_rect.width - 30, 100))
        
        for i, answer in enumerate(q['answers']):
            if i == q['correct_index']:
                # Правильный ответ - зеленый
                answer_text = f"  {i+1}. {answer} ✓"
                current_y = draw_text_multiline(screen, answer_text, font_small, RESULTS_GREEN, pygame.Rect(text_rect.x + 60, current_y, text_rect.width - 60, 100))
            elif i == q.get('user_index', -1):
                # Ответ пользователя (если неправильный) - красный
                answer_text = f"  {i+1}. {answer} ✗"
                current_y = draw_text_multiline(screen, answer_text, font_small, RESULTS_RED, pygame.Rect(text_rect.x + 60, current_y, text_rect.width - 60, 100))
            else:
                # Остальные ответы - серые
                answer_text = f"  {i+1}. {answer}"
                current_y = draw_text_multiline(screen, answer_text, font_small, (100, 100, 100), pygame.Rect(text_rect.x + 60, current_y, text_rect.width - 60, 100))
        
        current_y += 15

    draw_detail_navigation(x, y, w, h)

def draw_detail_navigation(bx, by, bw, bh):
    """Отрисовывает навигацию по страницам"""
    if len(current_data) > items_per_page:
        total_pages = math.ceil(len(current_data) / items_per_page)
        nav_y = by + bh - 60 
        
        prev_button_rect = pygame.Rect(bx + 50, nav_y, 40, 40)
        if current_page > 0:
            pygame.draw.circle(screen, RESULTS_BLUE, prev_button_rect.center, 20)
            pygame.draw.polygon(screen, WHITE, [
                (prev_button_rect.centerx + 5, prev_button_rect.centery - 10),
                (prev_button_rect.centerx - 5, prev_button_rect.centery),
                (prev_button_rect.centerx + 5, prev_button_rect.centery + 10)
            ])
            
        next_button_rect = pygame.Rect(bx + bw - 90, nav_y, 40, 40)
        if current_page < total_pages - 1:
            pygame.draw.circle(screen, RESULTS_BLUE, next_button_rect.center, 20)
            pygame.draw.polygon(screen, WHITE, [
                (next_button_rect.centerx - 5, next_button_rect.centery - 10),
                (next_button_rect.centerx + 5, next_button_rect.centery),
                (next_button_rect.centerx - 5, next_button_rect.centery + 10)
            ])
        
        page_text = font_small.render(f"Страница {current_page + 1} из {total_pages}", True, RESULTS_BLUE)
        screen.blit(page_text, (bx + bw/2 - page_text.get_width()/2, nav_y + 8))

def draw_back_button():
    """Отрисовывает кнопку Назад"""
    x, y, w, h = BACK_BUTTON_RECT.x, BACK_BUTTON_RECT.y, BACK_BUTTON_RECT.width, BACK_BUTTON_RECT.height
    pygame.draw.rect(screen, RESULTS_RED, BACK_BUTTON_RECT, border_radius=15)
    
    text = font_label.render("← Назад к результатам", True, WHITE)
    screen.blit(text, (x + w/2 - text.get_width()/2, y + h/2 - text.get_height()/2))

def draw_results_screen():
    """Отрисовывает экран результатов"""
    global results_frame
    
    screen.blit(end_background, (0, 0))
    
    title_y = 200
    title = font_title.render("ВАШИ РЕЗУЛЬТАТЫ:", True, WHITE)
    screen.blit(title, (WIDTH/2 - title.get_width()/2, title_y))

    if current_view == "MAIN":
        for box in result_boxes:
            offset_y = math.sin(results_frame * 0.05 + box["phase"]) * 15 
            draw_results_box(box, offset_y)
        
    
            
    elif current_view == "DETAIL":
        draw_detail_screen()
        draw_back_button() 
    
    # Инструкция
    exit_font = pygame.font.Font(None, 40)
    
    if current_view == "MAIN":
        exit_text = exit_font.render("ESC - выход | R - рестарт | Кликните на вопрос для деталей | Колесо мыши - прокрутка", True, (255, 255, 255))
    else:
        exit_text = exit_font.render("ESC - выход | R - рестарт | Двойной клик - назад к результатам", True, (255, 255, 255))
    
    exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT - 50))
    screen.blit(exit_text, exit_rect)

# Инициализация для первого уровня
init_platforms()
clock = pygame.time.Clock()
running = True

game_paused = False

# ===== ЗАГРУЗКА ВОПРОСОВ ИЗ БАЗЫ ДАННЫХ ПЕРЕД СТАРТОМ ИГРЫ =====
try:
    loaded = load_questions_for_language(DB_LANGUAGE_NAME, max_levels=3)
    if not loaded or all(len(v) == 0 for v in loaded.values()):
        print(f"✗ Не удалось загрузить вопросы из БД для языка '{DB_LANGUAGE_NAME}'")
        print("Игра будет завершена, так как нет заданий.")
        pygame.quit()
        sys.exit()
    questions.update(loaded)
    # Актуализируем max_tasks для первого уровня
    level_questions = questions.get(current_level, [])
    if level_questions:
        max_tasks = min(3, len(level_questions))
    else:
        max_tasks = 0
    print(f"✓ Вопросы успешно загружены из БД для языка '{DB_LANGUAGE_NAME}'")
except Exception as e:
    print(f"✗ Критическая ошибка при загрузке вопросов из БД: {e}")
    pygame.quit()
    sys.exit()

while running:
    dt = clock.tick(60) / 16.67
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if game_state == STATE_QUESTION and not answer_selected and current_question:
                # Старая система через клавиши
                if event.key == pygame.K_1:
                    selected_answer = 0
                    answer_selected = True
                    show_all_colors = True  # Показываем ВСЕ цвета сразу
                    question_result_timer = question_result_duration  # Запускаем таймер
                    
                    # Помечаем вопрос как отвеченный
                    current_question["answered"] = True
                    current_question["user_answer"] = selected_answer
                    current_question["is_correct"] = (selected_answer == current_question["correct"])
                    
                    # Добавляем в список всех вопросов игры (если еще не добавлен)
                    question_found = False
                    for q in all_questions_list:
                        if q["question"] == current_question["question"]:
                            question_found = True
                            break
                    
                    if not question_found:
                        all_questions_list.append({
                            "id": len(all_questions_list) + 1,
                            "question": current_question["question"],
                            "answers": current_question["answers"],
                            "correct_answer": current_question["answers"][current_question["correct"]],
                            "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                            "is_correct": current_question["is_correct"],
                            "correct_index": current_question["correct"],
                            "user_index": selected_answer
                        })
                    
                    # Сохраняем в историю ответов для текущего вопроса
                    question_history.append({
                        "id": len(question_history) + 1,
                        "text": current_question["question"],
                        "is_correct": current_question["is_correct"],
                        "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                        "correct_answer": current_question["answers"][current_question["correct"]] if 0 <= current_question["correct"] < len(current_question["answers"]) else "Ошибка",
                        "user_index": selected_answer,
                        "correct_index": current_question["correct"]
                    })
                    
                    # ИЗМЕНЕНИЕ 1: Всегда увеличиваем счетчик выполненных заданий
                    tasks_done += 1
                    
                    if selected_answer == current_question["correct"]:
                        correct_count += 1
                        print(f"Правильный ответ! Заданий выполнено: {tasks_done}/{max_tasks}")
                    else:
                        lose_life()
                        wrong_count += 1
                        print(f"Неправильный ответ! Теряем жизнь. Заданий выполнено: {tasks_done}/{max_tasks}")
                elif event.key == pygame.K_2:
                    selected_answer = 1
                    answer_selected = True
                    show_all_colors = True  # Показываем ВСЕ цвета сразу
                    question_result_timer = question_result_duration  # Запускаем таймер
                    
                    # Помечаем вопрос как отвеченный
                    current_question["answered"] = True
                    current_question["user_answer"] = selected_answer
                    current_question["is_correct"] = (selected_answer == current_question["correct"])
                    
                    # Добавляем в список всех вопросов игры (если еще не добавлен)
                    question_found = False
                    for q in all_questions_list:
                        if q["question"] == current_question["question"]:
                            question_found = True
                            break
                    
                    if not question_found:
                        all_questions_list.append({
                            "id": len(all_questions_list) + 1,
                            "question": current_question["question"],
                            "answers": current_question["answers"],
                            "correct_answer": current_question["answers"][current_question["correct"]],
                            "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                            "is_correct": current_question["is_correct"],
                            "correct_index": current_question["correct"],
                            "user_index": selected_answer
                        })
                    
                    # Сохраняем в историю ответов для текущего вопроса
                    question_history.append({
                        "id": len(question_history) + 1,
                        "text": current_question["question"],
                        "is_correct": current_question["is_correct"],
                        "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                        "correct_answer": current_question["answers"][current_question["correct"]] if 0 <= current_question["correct"] < len(current_question["answers"]) else "Ошибка",
                        "user_index": selected_answer,
                        "correct_index": current_question["correct"]
                    })
                    
                    # ИЗМЕНЕНИЕ 1: Всегда увеличиваем счетчик выполненных заданий
                    tasks_done += 1
                    
                    if selected_answer == current_question["correct"]:
                        correct_count += 1
                        print(f"Правильный ответ! Заданий выполнено: {tasks_done}/{max_tasks}")
                    else:
                        lose_life()
                        wrong_count += 1
                        print(f"Неправильный ответ! Теряем жизнь. Заданий выполнено: {tasks_done}/{max_tasks}")
                elif event.key == pygame.K_3:
                    selected_answer = 2
                    answer_selected = True
                    show_all_colors = True  # Показываем ВСЕ цвета сразу
                    question_result_timer = question_result_duration  # Запускаем таймер
                    
                    # Помечаем вопрос как отвеченный
                    current_question["answered"] = True
                    current_question["user_answer"] = selected_answer
                    current_question["is_correct"] = (selected_answer == current_question["correct"])
                    
                    # Добавляем в список всех вопросов игры (если еще не добавлен)
                    question_found = False
                    for q in all_questions_list:
                        if q["question"] == current_question["question"]:
                            question_found = True
                            break
                    
                    if not question_found:
                        all_questions_list.append({
                            "id": len(all_questions_list) + 1,
                            "question": current_question["question"],
                            "answers": current_question["answers"],
                            "correct_answer": current_question["answers"][current_question["correct"]],
                            "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                            "is_correct": current_question["is_correct"],
                            "correct_index": current_question["correct"],
                            "user_index": selected_answer
                        })
                    
                    # Сохраняем в историю ответов для текущего вопроса
                    question_history.append({
                        "id": len(question_history) + 1,
                        "text": current_question["question"],
                        "is_correct": current_question["is_correct"],
                        "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                        "correct_answer": current_question["answers"][current_question["correct"]] if 0 <= current_question["correct"] < len(current_question["answers"]) else "Ошибка",
                        "user_index": selected_answer,
                        "correct_index": current_question["correct"]
                    })
                    
                    # ИЗМЕНЕНИЕ 1: Всегда увеличиваем счетчик выполненных заданий
                    tasks_done += 1
                    
                    if selected_answer == current_question["correct"]:
                        correct_count += 1
                        print(f"Правильный ответ! Заданий выполнено: {tasks_done}/{max_tasks}")
                    else:
                        lose_life()
                        wrong_count += 1
                        print(f"Неправильный ответ! Теряем жизнь. Заданий выполнено: {tasks_done}/{max_tasks}")
                elif event.key == pygame.K_4:
                    selected_answer = 3
                    answer_selected = True
                    show_all_colors = True  # Показываем ВСЕ цвета сразу
                    question_result_timer = question_result_duration  # Запускаем таймер
                    
                    # Помечаем вопрос как отвеченный
                    current_question["answered"] = True
                    current_question["user_answer"] = selected_answer
                    current_question["is_correct"] = (selected_answer == current_question["correct"])
                    
                    # Добавляем в список всех вопросов игры (если еще не добавлен)
                    question_found = False
                    for q in all_questions_list:
                        if q["question"] == current_question["question"]:
                            question_found = True
                            break
                    
                    if not question_found:
                        all_questions_list.append({
                            "id": len(all_questions_list) + 1,
                            "question": current_question["question"],
                            "answers": current_question["answers"],
                            "correct_answer": current_question["answers"][current_question["correct"]],
                            "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                            "is_correct": current_question["is_correct"],
                            "correct_index": current_question["correct"],
                            "user_index": selected_answer
                        })
                    
                    # Сохраняем в историю ответов для текущего вопроса
                    question_history.append({
                        "id": len(question_history) + 1,
                        "text": current_question["question"],
                        "is_correct": current_question["is_correct"],
                        "user_answer": current_question["answers"][selected_answer] if 0 <= selected_answer < len(current_question["answers"]) else "Не выбран",
                        "correct_answer": current_question["answers"][current_question["correct"]] if 0 <= current_question["correct"] < len(current_question["answers"]) else "Ошибка",
                        "user_index": selected_answer,
                        "correct_index": current_question["correct"]
                    })
                    
                    # ИЗМЕНЕНИЕ 1: Всегда увеличиваем счетчик выполненных заданий
                    tasks_done += 1
                    
                    if selected_answer == current_question["correct"]:
                        correct_count += 1
                        print(f"Правильный ответ! Заданий выполнено: {tasks_done}/{max_tasks}")
                    else:
                        lose_life()
                        wrong_count += 1
                        print(f"Неправильный ответ! Теряем жизнь. Заданий выполнено: {tasks_done}/{max_tasks}")
            
            if (event.key == pygame.K_SPACE or event.key == pygame.K_w or event.key == pygame.K_UP) and not is_jumping and not is_respawning and game_state in [STATE_PLAY, STATE_INTRO] and not player_death_animation and not game_paused:
                is_jumping = True
                player_vel_y = jump_power
                on_ground = False
            
            if event.key == pygame.K_RETURN and game_state == STATE_INTRO and current_level == 1:
                game_state = STATE_PLAY
                has_stepped_on_platform = True
                start_game()
            
            # Обработка клавиши SPACE на экране победы для перехода к результатам
            if event.key == pygame.K_SPACE and game_state == STATE_WIN_SCREEN:
                prepare_results_data()
                game_state = STATE_RESULTS
                current_view = "MAIN"
                detail_box["active"] = False
                current_page = 0
            
            # Обработка клавиш ESC и R на экранах конца игры
            if game_state in [STATE_WIN_SCREEN, STATE_LOSE_SCREEN, STATE_RESULTS]:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Рестарт игры
                    hearts = max_hearts
                    coins_collected = 0
                    current_level = 1
                    player_x = WIDTH // 2 - 40
                    player_y = HEIGHT - 450
                    is_respawning = False
                    lose_life_timer = 0
                    player_hit_timer = 0
                    player_death_animation = False
                    player_alpha = 255
                    has_stepped_on_platform = False
                    game_state = STATE_LEVEL_START
                    level_start_timer = 180
                    level_text_alpha = 0
                    level_text_scale = 0.5
                    level_text_growing = True
                    win_scale = 0.1
                    lose_scale = 0.1
                    game_paused = False
                    idle_animation_active = True
                    
                    # Сброс статистики
                    question_history = []
                    all_questions_list = []
                    correct_count = 0
                    wrong_count = 0
                    current_view = "MAIN"
                    detail_box["active"] = False
                    current_page = 0
                    scroll_offset = 0
                    
                    init_platforms()
        
        # Обработка кликов мыши для экрана результатов
        if event.type == pygame.MOUSEBUTTONDOWN and game_state == STATE_RESULTS:
            mouse_pos = event.pos
            
            if current_view == "MAIN":
                # Проверяем клик по статистическим блокам
                for box in result_boxes:
                    if box["rect"].collidepoint(mouse_pos):
                        current_view = "DETAIL"
                        detail_box["active"] = True
                        detail_box["data_type"] = box["type"]
                        current_page = 0
                        
                        if box["type"] == "correct":
                            current_data = [q for q in all_questions_list if q["is_correct"]]
                        elif box["type"] == "wrong":
                            current_data = [q for q in all_questions_list if not q["is_correct"]]
                        elif box["type"] == "total":
                            current_data = all_questions_list
                        break
                
                # Проверяем клик по вопросам в списке
                for q in all_questions_list:
                    if 'rect' in q and q['rect'].collidepoint(mouse_pos):
                        current_view = "DETAIL"
                        detail_box["active"] = True
                        detail_box["data_type"] = "single_question"
                        current_page = 0
                        current_data = [q]
                        break
                
                # Начало перетаскивания для прокрутки
                if event.button == 1:  # Левая кнопка мыши
                    is_dragging = True
                    drag_start_y = mouse_pos[1]
            
            elif current_view == "DETAIL":
                # ИЗМЕНЕНИЕ 3: Обработка двойного нажатия для возврата к результатам
                if event.button == 1:  # Левая кнопка мыши
                    if current_time - last_tap_time < double_tap_threshold:
                        # Двойное нажатие - возвращаемся к результатам
                        current_view = "MAIN"
                        detail_box["active"] = False
                    last_tap_time = current_time
                    
                    # Также проверяем клик по кнопке "Назад"
                    if BACK_BUTTON_RECT.collidepoint(mouse_pos):
                        current_view = "MAIN"
                        detail_box["active"] = False
                
                # Навигация по страницам
                nav_clicked = False
                
                if len(current_data) > items_per_page:
                    x, y, w, h = DETAIL_VIEW_RECT.x, DETAIL_VIEW_RECT.y, DETAIL_VIEW_RECT.width, DETAIL_VIEW_RECT.height
                    total_pages = math.ceil(len(current_data) / items_per_page)
                    nav_y = y + h - 60 
                    
                    prev_button_rect = pygame.Rect(x + 50, nav_y, 40, 40)
                    next_button_rect = pygame.Rect(x + w - 90, nav_y, 40, 40)
                    
                    if current_page > 0 and prev_button_rect.collidepoint(mouse_pos):
                        current_page -= 1
                        nav_clicked = True
                        
                    elif current_page < total_pages - 1 and next_button_rect.collidepoint(mouse_pos):
                        current_page += 1
                        nav_clicked = True
        
        # Прокрутка колесиком мыши
        elif event.type == pygame.MOUSEWHEEL and game_state == STATE_RESULTS and current_view == "MAIN":
            scroll_offset = max(0, min(max_scroll_offset, scroll_offset - event.y * scroll_speed))
        
        # Окончание перетаскивания
        elif event.type == pygame.MOUSEBUTTONUP and game_state == STATE_RESULTS and current_view == "MAIN":
            if event.button == 1:
                is_dragging = False
        
        # Перетаскивание для прокрутки
        elif event.type == pygame.MOUSEMOTION and game_state == STATE_RESULTS and current_view == "MAIN":
            if is_dragging:
                delta_y = mouse_pos[1] - drag_start_y
                scroll_offset = max(0, min(max_scroll_offset, scroll_offset - delta_y))
                drag_start_y = mouse_pos[1]
    
    # Обновление таймера для показа результата вопроса
    if game_state == STATE_QUESTION and answer_selected and question_result_timer > 0:
        question_result_timer -= 1
        if question_result_timer <= 0:
            # Автоматическое продолжение после 2 секунд
            question_active = False
            selected_answer = -1
            answer_selected = False
            question_result_timer = 0
            show_all_colors = False
            game_state = STATE_PLAY
            idle_animation_active = True
            
            # Проверяем, выполнены ли все задания
            if tasks_done >= max_tasks:
                if current_level < 3:
                    change_level(current_level + 1)
                else:
                    # Завершение игры - переход на экран победы
                    game_state = STATE_WIN_SCREEN
    
    if hearts <= 0 and game_state not in [STATE_LOSE_SCREEN, STATE_GAME_OVER, STATE_RESULTS]:
        game_state = STATE_LOSE_SCREEN
    
    # ========== ОТРИСОВКА В ЗАВИСИМОСТИ ОТ СОСТОЯНИЯ ==========
    if game_state == STATE_WIN_SCREEN:
        draw_win_screen()
        pygame.display.flip()
        continue
    
    elif game_state == STATE_LOSE_SCREEN:
        draw_lose_screen()
        pygame.display.flip()
        continue
    
    elif game_state == STATE_RESULTS:
        results_frame += 1
        draw_results_screen()
        pygame.display.flip()
        continue
    
    elif game_state == STATE_GAME_OVER:
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 100)
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        restart_text = pygame.font.Font(None, 50).render("Нажмите R для рестарта или ESC для выхода", True, (255, 255, 255))
        
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
        
        pygame.display.flip()
        continue
    
    # ========== ОСНОВНОЙ ГЕЙМПЛЕЙ ==========
    if player_hit_timer > 0:
        player_hit_timer -= 1
    
    if lose_life_timer > 0:
        lose_life_timer -= 1
    
    if player_death_animation:
        death_animation_timer -= 1
        if death_animation_timer > 0:
            if death_animation_timer > 60:
                player_alpha = 255 - (death_animation_timer - 60) * 8
            elif death_animation_timer > 30:
                player_alpha = max(0, min(255, (death_animation_timer % 10) * 50))
            else:
                player_alpha = 0
        else:
            player_death_animation = False
            player_alpha = 255
    
    if game_state == STATE_LEVEL_START:
        level_start_timer -= 1
        
        if level_start_timer > 120:
            level_text_alpha = min(255, level_text_alpha + 10)
        elif level_start_timer > 60:
            if level_text_growing:
                level_text_scale = min(1.2, level_text_scale + 0.02)
                if level_text_scale >= 1.2:
                    level_text_growing = False
            else:
                level_text_scale = max(1.0, level_text_scale - 0.02)
                if level_text_scale <= 1.0:
                    level_text_growing = True
        else:
            level_text_alpha = max(0, level_text_alpha - 5)
        
        if level_start_timer <= 0:
            if current_level >= 2:
                game_state = STATE_PLAY
                start_game()
            else:
                game_state = STATE_INTRO
    
    # Обработка вопросов с мышью
    if game_state == STATE_QUESTION and question_active and not answer_selected:
        handle_question_input()
    
    if game_state == STATE_PLAY and not game_paused:
        x1 -= speed
        x2 -= speed
        
        if x1 <= -WIDTH:
            x1 = WIDTH
            background_counter += 1
            letter_for_current_bg_spawned = False
        
        if x2 <= -WIDTH:
            x2 = WIDTH
            background_counter += 1
            letter_for_current_bg_spawned = False
    
    if was_on_air and player_y + player_height >= FLOOR_HEIGHT - 10:
        if player_hit_timer <= 0 and has_stepped_on_platform and game_state == STATE_PLAY:
            lose_life()
        was_on_air = False
    elif player_y + player_height < FLOOR_HEIGHT - 50:
        was_on_air = True
    
    keys = pygame.key.get_pressed()
    player_dx = 0
    
    is_walking = False
    
    if not is_respawning and game_state in [STATE_PLAY, STATE_INTRO] and not player_death_animation and not game_paused:
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_dx = -player_speed
            facing_right = False
            is_walking = True
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_dx = player_speed
            facing_right = True
            is_walking = True
    
    if not is_respawning and game_state in [STATE_PLAY, STATE_INTRO] and not player_death_animation and not game_paused:
        animation_counter += 1
        if animation_counter % animation_speed == 0:
            if is_walking:
                current_image = image2 if current_image == image1 else image1
            else:
                if idle_animation_active:
                    if animation_counter % (animation_speed * 3) == 0:
                        current_image = image2 if current_image == image1 else image1
    
    if not is_respawning and game_state in [STATE_PLAY, STATE_INTRO] and not player_death_animation and not game_paused:
        player_vel_y += gravity
        player_y += player_vel_y
        
        if player_y + player_height > FLOOR_HEIGHT:
            player_y = FLOOR_HEIGHT - player_height
            player_vel_y = 0
            is_jumping = False
            on_ground = True
        
        player_x += player_dx
        player_x = max(100, min(player_x, WIDTH - player_width - 100))
    
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    
    if not is_respawning and game_state in [STATE_PLAY, STATE_INTRO] and not player_death_animation and not game_paused:
        platform_collision = False
        collision_platform_y = 0
        
        for p in platforms:
            rect = p["rect"]
            
            if check_platform_collision(player_rect, rect, player_vel_y):
                platform_collision = True
                collision_platform_y = rect.top
                
                if not has_stepped_on_platform:
                    has_stepped_on_platform = True
                    start_game()
                    game_state = STATE_PLAY
                
                break
        
        if platform_collision and player_vel_y >= 0:
            player_y = collision_platform_y - player_height
            player_vel_y = 0
            is_jumping = False
            on_ground = True
    
    if not is_respawning and game_state == STATE_PLAY and not player_death_animation and not game_paused:
        for p in platforms:
            if p["coin"] and check_coin_collision(player_rect, p["coin"]):
                coins_collected += 1
                p["coin"] = None
        
        if current_letter and check_letter_collision(player_rect, current_letter):
            show_question()
    
    if game_state == STATE_PLAY and not game_paused:
        for p in platforms:
            rect = p["rect"]
            rect.x -= speed
            if p["coin"]:
                p["coin"].x -= speed
            
            if rect.x + rect.width < 0:
                max_x = max([pl["rect"].x for pl in platforms])
                rect.x = max_x + gap_x
                rect.width = random.randint(200, 350)
                rect.y = random.choice(heights)
                
                if random.random() < 0.5:
                    min_x = rect.x + 20
                    max_x = rect.x + rect.width - 80
                    if max_x > min_x:
                        coin_x = random.randint(min_x, max_x)
                        coin_y = rect.y - 150
                        p["coin"] = pygame.Rect(coin_x, coin_y, 80, 80)
                    else:
                        p["coin"] = None
                else:
                    p["coin"] = None
        
        if current_letter:
            current_letter.x -= speed
            if current_letter.x + current_letter.width < 0:
                letter_for_current_bg_spawned = False
                current_letter = None
    
    if game_state == STATE_PLAY and not current_letter and not letter_for_current_bg_spawned and game_started and not game_paused:
        spawn_letter()
    
    # ========== ОТРИСОВКА ИГРЫ ==========
    screen.blit(background, (x1, 0))
    screen.blit(background, (x2, 0))
    
    if game_state in [STATE_PLAY, STATE_INTRO]:
        for p in platforms:
            rect = p["rect"]
            scaled = pygame.transform.scale(platform_img, (rect.width, rect.height))
            screen.blit(scaled, (rect.x, rect.y))
            
            if p["coin"]:
                screen.blit(coin_img, (p["coin"].x, p["coin"].y))
    
    if current_letter:
        screen.blit(scroll_img, (current_letter.x, current_letter.y))
    
    if not is_respawning and game_state in [STATE_PLAY, STATE_INTRO, STATE_LEVEL_START]:
        player_image = current_image
        if not facing_right:
            player_image = pygame.transform.flip(current_image, True, False)
        
        if player_death_animation:
            player_image_copy = player_image.copy()
            player_image_copy.fill((255, 255, 255, player_alpha), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(player_image_copy, (player_x, player_y))
        elif player_hit_timer > 0 and player_hit_timer % 10 < 5:
            pass
        else:
            screen.blit(player_image, (player_x, player_y))
    
    interface_height = 80
    interface_y = 115
    element_y = interface_y + 15
    
    coin_width = -30 +20+ 200
    level_width = 70
    hearts_width = 5 * 70
    total_width = coin_width + level_width + hearts_width
    spacing = 450
    start_x = (WIDTH - (total_width + 2 * spacing)) // 2
    
    coin_icon_x = start_x
    screen.blit(coin_ui_img, (coin_icon_x, element_y - 5))
    
    font_coins = pygame.font.Font(None, 50)
    coins_text = font_coins.render(str(coins_collected), True, (255, 255, 0))
    coins_text_x = coin_icon_x + 100
    coins_text_y = element_y + 20
    screen.blit(coins_text, (coins_text_x, coins_text_y))
    
    font_level = pygame.font.Font(None, 60)
    if current_level == 1:
        level_text = font_level.render("УРОВЕНЬ 1", True, (255, 255, 0))
    elif current_level == 2:
        level_text = font_level.render("УРОВЕНЬ 2", True, (255, 255, 0))
    elif current_level == 3:
        level_text = font_level.render("УРОВЕНЬ 3", True, (255, 255, 0))
    else:
        level_text = font_level.render("УРОВЕНЬ " + str(current_level), True, (255, 255, 0))
    
    level_text_x = start_x + coin_width + spacing
    level_text_y = element_y
    screen.blit(level_text, (level_text_x, level_text_y))
    
    heart_spacing = 65
    heart_start_x = start_x + coin_width + spacing + level_width + spacing
    
    for i in range(5):
        heart_x = heart_start_x + i * heart_spacing
        
        if i < hearts:
            screen.blit(heart1_img, (heart_x, element_y))
        else:
            screen.blit(gray_heart_img, (heart_x, element_y))
    
    font_tasks = pygame.font.Font(None, 40)
    tasks_text = font_tasks.render("Задания: " + str(tasks_done) + "/" + str(max_tasks), True, (255, 255, 0))
    tasks_y = interface_y + interface_height + 5
    screen.blit(tasks_text, (WIDTH//2 - tasks_text.get_width()//2, tasks_y))
    
    # ========== ОТРИСОВКА ВОПРОСОВ ==========
    if game_state == STATE_QUESTION and current_question:
        # Затемнение фона
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        
        # Бумага
        paper_x = WIDTH // 2 - paper_img.get_width() // 2
        paper_y = 150
        screen.blit(paper_img, (paper_x, paper_y))
        
        # Вопрос
        question_font = pygame.font.Font(None, 60)
        question_text = question_font.render(current_question["question"], True, (0, 0, 0))
        question_rect = question_text.get_rect(center=(WIDTH//2, 350))
        screen.blit(question_text, question_rect)
        
        # Кнопки ответов
        mouse = pygame.mouse.get_pos()
        for i, rect in enumerate(answer_rects):
            # Определяем цвет кнопки
            if show_all_colors:
                # Сразу показываем ВСЕ правильные/неправильные ответы
                if i == current_question["correct"]:
                    color = GREEN  # Правильный ответ - зеленый
                else:
                    color = RED  # Неправильные ответы - красные
            else:
                # Обычный режим - подсветка при наведении
                if rect.collidepoint(mouse) and not answer_selected:
                    color = BLUE_HOVER
                else:
                    color = BLUE_BTN
            
            # Рисуем прямоугольник кнопки
            pygame.draw.rect(screen, color, rect, border_radius=40)
            
            # Рисуем текст ответа
            answer_font = pygame.font.Font(None, 40)
            if i < len(current_question["answers"]):
                answer_text = answer_font.render(current_question["answers"][i], True, WHITE)
                answer_rect = answer_text.get_rect(center=rect.center)
                screen.blit(answer_text, answer_rect)
    
    elif game_state == STATE_INTRO:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        intro_font = pygame.font.Font(None, 120)
        
        if current_level == 1:
            intro_text = intro_font.render("УРОВЕНЬ 1", True, (255, 255, 0))
        elif current_level == 2:
            intro_text = intro_font.render("УРОВЕНЬ 2", True, (255, 255, 0))
        elif current_level == 3:
            intro_text = intro_font.render("УРОВЕНЬ 3", True, (255, 255, 0))
        else:
            intro_text = intro_font.render("УРОВЕНЬ " + str(current_level), True, (255, 255, 0))
        
        screen.blit(intro_text, (WIDTH//2 - intro_text.get_width()//2, HEIGHT//2 - 100))
        
        instruction_font = pygame.font.Font(None, 60)
        instruction1 = instruction_font.render("Встаньте на платформу, чтобы начать игру", True, (BLUE))
        instruction2 = instruction_font.render("Или нажмите ENTER для старта", True, (BLUE))
        
        screen.blit(instruction1, (WIDTH//2 - instruction1.get_width()//2, HEIGHT//2 + 50))
        screen.blit(instruction2, (WIDTH//2 - instruction2.get_width()//2, HEIGHT//2 + 120))
    
    elif game_state == STATE_LEVEL_START:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        level_font = pygame.font.Font(None, 150)
        
        if current_level == 1:
            level_text_surface = level_font.render("УРОВЕНЬ 1", True, (255, 255, 0))
        elif current_level == 2:
            level_text_surface = level_font.render("УРОВЕНЬ 2", True, (255, 200, 0))
        elif current_level == 3:
            level_text_surface = level_font.render("УРОВЕНЬ 3", True, (255, 150, 0))
        else:
            level_text_surface = level_font.render("УРОВЕНЬ " + str(current_level), True, (255, 255, 0))
        
        level_text_surface.set_alpha(level_text_alpha)
        
        if level_text_scale != 1.0:
            original_size = level_text_surface.get_size()
            new_size = (int(original_size[0] * level_text_scale), int(original_size[1] * level_text_scale))
            scaled_text = pygame.transform.scale(level_text_surface, new_size)
            text_rect = scaled_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(scaled_text, text_rect)
        else:
            text_rect = level_text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(level_text_surface, text_rect)
    
    if is_respawning:
        respawn_timer -= 1
        game_paused = True
        
        if respawn_timer > 0:
            if respawn_timer > 120:
                countdown_num = 3
            elif respawn_timer > 60:
                countdown_num = 2
            else:
                countdown_num = 1
            
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, 200)
            countdown_text = font.render(str(countdown_num), True, (255, 0, 0))
            
            screen.blit(countdown_text, (WIDTH//2 - countdown_text.get_width()//2, HEIGHT//2 - 100))
            
            message_font = pygame.font.Font(None, 50)
            message = message_font.render("Осталось сердец: " + str(hearts), True, (255, 255, 255))
            screen.blit(message, (WIDTH//2 - message.get_width()//2, HEIGHT//2 + 50))
            
            if respawn_platform:
                platform_info = message_font.render("Возрождение на платформе позади", True, (BLUE))
                screen.blit(platform_info, (WIDTH//2 - platform_info.get_width()//2, HEIGHT//2 + 120))
        else:
            is_respawning = False
            game_paused = False
            idle_animation_active = True
            
            if respawn_platform:
                player_x = respawn_platform.x + respawn_platform.width // 2 - player_width // 2
                player_y = respawn_platform.top - player_height
            else:
                if len(platforms) > 0:
                    first_platform = platforms[0]["rect"]
                    player_x = first_platform.x + first_platform.width // 2 - player_width // 2
                    player_y = first_platform.top - player_height
                else:
                    player_x = WIDTH // 2 - 40
                    player_y = HEIGHT - 450
            
            player_vel_y = 0
            is_jumping = False
            on_ground = True
            player_death_animation = False
            player_alpha = 255
    
    if current_level == 1 and not has_stepped_on_platform and game_state == STATE_PLAY:
        status_font = pygame.font.Font(None, 40)
        status_text = status_font.render("Встаньте на платформу, чтобы активировать жизни", True, (BLUE))
        screen.blit(status_text, (WIDTH//2 - status_text.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()

pygame.quit()
sys.exit()