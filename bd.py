import sys
import hashlib
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QDialog, QLabel, QTabWidget, QGroupBox, QGridLayout, 
                             QFormLayout, QTextEdit, QSpinBox, QCheckBox, QComboBox, QSplitter,
                             QFrame, QStackedWidget, QListWidget, QListWidgetItem, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
import psycopg2
from psycopg2 import sql
import json
import os

CONFIG_FILE = "osudos_db_config.json"
DEFAULT_CONFIG = {
    'dbname': 'osudos',
    'user': 'postgres',
    'password': '87780455396',
    'host': 'localhost',
    'port': '5432'
}

class DBManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connected = False
        
    def connect(self, dbname, user, password, host, port):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.cursor = self.conn.cursor()
            self.connected = True
            return True, "Подключено к " + dbname + "@" + host + ":" + port
        except Exception as e:
            return False, "Ошибка подключения: " + str(e)
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn:
            self.conn.close()
            self.conn = None
        self.connected = False
        return "Отключено от базы данных"
    
    def execute_query(self, query, params=(), fetch=False):
        if not self.connected or not self.cursor:
            return None
        
        try:
            # Проверяем, не в состоянии ошибки ли транзакция
            try:
                self.cursor.execute("SELECT 1")
            except:
                # Если транзакция в состоянии ошибки, откатываем
                if self.conn:
                    try:
                        self.conn.rollback()
                    except:
                        pass
            
            self.cursor.execute(query, params)
            if fetch:
                rows = self.cursor.fetchall()
                return rows
            else:
                if self.conn:
                    self.conn.commit()
                return self.cursor.rowcount
        except Exception as e:
            print("Ошибка запроса: " + str(e))
            # Откатываем транзакцию при ошибке
            if self.conn:
                try:
                    self.conn.rollback()
                except:
                    pass
            if fetch:
                return []
            return None
    
    def initialize_database(self):
        if not self.connected or not self.cursor or not self.conn:
            return False, "Нет подключения"
        
        try:
            sql_commands = [
                """
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(100),
                    email VARCHAR(100),
                    birth_date DATE,
                    interface_language VARCHAR(10) DEFAULT 'ru',
                    sound_enabled BOOLEAN DEFAULT TRUE,
                    music_enabled BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS languages (
                    id SERIAL PRIMARY KEY,
                    language_name VARCHAR(50) NOT NULL,
                    language_code VARCHAR(10) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS characters (
                    id SERIAL PRIMARY KEY,
                    character_name VARCHAR(50) NOT NULL,
                    description TEXT,
                    image_path VARCHAR(255),
                    base_health INTEGER DEFAULT 100,
                    base_speed INTEGER DEFAULT 5,
                    unlock_level INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS levels (
                    id SERIAL PRIMARY KEY,
                    language_id INTEGER REFERENCES languages(id),
                    level_number INTEGER NOT NULL,
                    level_name VARCHAR(100),
                    difficulty VARCHAR(20) DEFAULT 'easy',
                    required_score INTEGER DEFAULT 0,
                    unlock_threshold INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS quiz_questions (
                    id SERIAL PRIMARY KEY,
                    language_id INTEGER REFERENCES languages(id),
                    level_id INTEGER REFERENCES levels(id),
                    question_text TEXT NOT NULL,
                    hint TEXT,
                    question_type VARCHAR(20) DEFAULT 'multiple_choice',
                    difficulty_score INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS answer_options (
                    id SERIAL PRIMARY KEY,
                    question_id INTEGER REFERENCES quiz_questions(id),
                    option_text TEXT NOT NULL,
                    is_correct BOOLEAN DEFAULT FALSE,
                    explanation TEXT,
                    order_num INTEGER DEFAULT 0
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS game_progress (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    language_id INTEGER REFERENCES languages(id),
                    character_id INTEGER REFERENCES characters(id),
                    current_level INTEGER DEFAULT 1,
                    total_score INTEGER DEFAULT 0,
                    lives_left INTEGER DEFAULT 3,
                    coins INTEGER DEFAULT 0,
                    experience INTEGER DEFAULT 0,
                    games_played INTEGER DEFAULT 0,
                    correct_answers INTEGER DEFAULT 0,
                    total_answers INTEGER DEFAULT 0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(player_id, language_id)
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS player_answers (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    question_id INTEGER REFERENCES quiz_questions(id),
                    selected_option_id INTEGER REFERENCES answer_options(id),
                    is_correct BOOLEAN DEFAULT FALSE,
                    time_spent INTEGER DEFAULT 0,
                    answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]
            
            for sql in sql_commands:
                self.cursor.execute(sql)
            
            if self.conn:
                self.conn.commit()
            
            # Вызываем миграцию перед добавлением тестовых данных
            self.migrate_database()
            self.add_sample_data()
            return True, "Таблицы созданы"
            
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, "Ошибка: " + str(e)
    
    def migrate_database(self):
        """Добавляет недостающие колонки в существующие таблицы"""
        if not self.connected or not self.cursor or not self.conn:
            return
        
        try:
            cursor = self.cursor
            
            # Функция для проверки и добавления колонки
            def add_column_if_not_exists(table_name, column_name, column_type):
                try:
                    cursor.execute(
                        "SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s",
                        (table_name, column_name)
                    )
                    if not cursor.fetchone():
                        print(f"Добавляем колонку {column_name} в таблицу {table_name}")
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                        cursor.execute(sql)
                        return True
                except Exception as e:
                    print(f"Ошибка при проверке/добавлении колонки {column_name} в {table_name}: {e}")
                    return False
                return False
            
            # Миграция таблицы players
            add_column_if_not_exists("players", "email", "VARCHAR(100)")
            add_column_if_not_exists("players", "birth_date", "DATE")
            add_column_if_not_exists("players", "interface_language", "VARCHAR(10)")
            add_column_if_not_exists("players", "sound_enabled", "BOOLEAN")
            add_column_if_not_exists("players", "music_enabled", "BOOLEAN")
            add_column_if_not_exists("players", "created_at", "TIMESTAMP")
            add_column_if_not_exists("players", "last_login", "TIMESTAMP")
            
            # Миграция таблицы languages
            add_column_if_not_exists("languages", "language_code", "VARCHAR(10)")
            add_column_if_not_exists("languages", "is_active", "BOOLEAN")
            
            # Миграция таблицы characters
            add_column_if_not_exists("characters", "base_health", "INTEGER")
            add_column_if_not_exists("characters", "base_speed", "INTEGER")
            add_column_if_not_exists("characters", "unlock_level", "INTEGER")
            add_column_if_not_exists("characters", "is_active", "BOOLEAN")
            
            # Миграция таблицы levels
            add_column_if_not_exists("levels", "required_score", "INTEGER")
            add_column_if_not_exists("levels", "unlock_threshold", "INTEGER")
            add_column_if_not_exists("levels", "is_active", "BOOLEAN")
            
            # Миграция таблицы quiz_questions
            add_column_if_not_exists("quiz_questions", "difficulty_score", "INTEGER")
            add_column_if_not_exists("quiz_questions", "is_active", "BOOLEAN")
            
            # Миграция таблицы answer_options
            add_column_if_not_exists("answer_options", "explanation", "TEXT")
            add_column_if_not_exists("answer_options", "order_num", "INTEGER")
            
            # Миграция таблицы game_progress
            add_column_if_not_exists("game_progress", "character_id", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET character_id = 1 WHERE character_id IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "lives_left", "INTEGER")
            add_column_if_not_exists("game_progress", "coins", "INTEGER")
            add_column_if_not_exists("game_progress", "experience", "INTEGER")
            add_column_if_not_exists("game_progress", "games_played", "INTEGER")
            add_column_if_not_exists("game_progress", "correct_answers", "INTEGER")
            add_column_if_not_exists("game_progress", "total_answers", "INTEGER")
            add_column_if_not_exists("game_progress", "last_played", "TIMESTAMP")
            
            # Миграция таблицы player_answers
            add_column_if_not_exists("player_answers", "selected_option_id", "INTEGER")
            add_column_if_not_exists("player_answers", "is_correct", "BOOLEAN")
            add_column_if_not_exists("player_answers", "time_spent", "INTEGER")
            add_column_if_not_exists("player_answers", "answered_at", "TIMESTAMP")
            
            # Коммитим все изменения миграции
            if self.conn:
                self.conn.commit()
                
        except Exception as e:
            print(f"Ошибка при миграции базы данных: {e}")
            if self.conn:
                try:
                    self.conn.rollback()
                except:
                    pass
    
    def add_sample_data(self):
        if not self.connected or not self.cursor or not self.conn:
            return
        try:
            # Сначала проверяем наличие колонки language_code
            self.cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='languages' AND column_name='language_code'")
            if not self.cursor.fetchone():
                # Если колонки нет, добавляем её
                self.cursor.execute("ALTER TABLE languages ADD COLUMN language_code VARCHAR(10)")
                if self.conn:
                    self.conn.commit()
            
            # Проверяем, есть ли уже языки
            self.cursor.execute("SELECT COUNT(*) FROM languages")
            result = self.cursor.fetchone()
            if result and result[0] == 0:
                # Добавляем 4 языка программирования
                languages = [
                    ('Python', 'python'), 
                    ('Java', 'java'), 
                    ('C#', 'csharp'), 
                    ('SQL', 'sql')
                ]
                for name, code in languages:
                    self.cursor.execute(
                        "INSERT INTO languages (language_name, language_code) VALUES (%s, %s)",
                        (name, code)
                    )
                
                # Добавляем персонажей
                characters = [
                    ('Новичок', 'Начинающий программист', 100, 5, 1),
                    ('Опытный', 'Опытный разработчик', 120, 7, 5),
                    ('Мастер', 'Мастер программирования', 150, 10, 10)
                ]
                for name, desc, health, speed, unlock in characters:
                    self.cursor.execute(
                        """INSERT INTO characters (character_name, description, base_health, 
                           base_speed, unlock_level) VALUES (%s, %s, %s, %s, %s)""",
                        (name, desc, health, speed, unlock)
                    )
                
                # Для каждого языка добавляем 3 уровня
                self.cursor.execute("SELECT id FROM languages")
                language_ids = self.cursor.fetchall()
                
                for lang_id in language_ids:
                    for i in range(1, 4):  # 3 уровня
                        level_name = f"Уровень {i}"
                        difficulty = "easy" if i == 1 else "medium" if i == 2 else "hard"
                        required_score = i * 100
                        
                        self.cursor.execute(
                            """INSERT INTO levels (language_id, level_number, level_name, 
                               difficulty, required_score) VALUES (%s, %s, %s, %s, %s)""",
                            (lang_id[0], i, level_name, difficulty, required_score)
                        )
                
                # Добавляем администратора
                password_hash = hashlib.sha256("admin123".encode()).hexdigest()
                self.cursor.execute(
                    "INSERT INTO players (username, password_hash, full_name) VALUES (%s, %s, %s)",
                    ("admin", password_hash, "Администратор")
                )
                
                if self.conn:
                    self.conn.commit()
                print("Добавлены тестовые данные")
        except Exception as e:
            print("Ошибка при добавлении данных: " + str(e))
            if self.conn:
                self.conn.rollback()
    
    def get_all_players(self):
        query = """
        SELECT id, username, full_name, email, interface_language, 
               sound_enabled, music_enabled, created_at, last_login 
        FROM players 
        ORDER BY created_at DESC
        """
        result = self.execute_query(query, fetch=True)
        return result or []
    
    def get_player_details(self, player_id):
        query = """
        SELECT id, username, full_name, email, birth_date, interface_language,
               sound_enabled, music_enabled, created_at, last_login
        FROM players 
        WHERE id = %s
        """
        result = self.execute_query(query, (player_id,), fetch=True)
        return result[0] if result and isinstance(result, list) and len(result) > 0 else None
    
    def get_player_statistics(self, player_id):
        query = """
        SELECT 
            gp.language_id,
            l.language_name,
            gp.current_level,
            gp.total_score,
            gp.lives_left,
            gp.coins,
            gp.experience,
            gp.games_played,
            gp.correct_answers,
            gp.total_answers,
            ROUND((gp.correct_answers::DECIMAL / NULLIF(gp.total_answers, 0) * 100), 2) as accuracy,
            gp.character_id
        FROM game_progress gp
        JOIN languages l ON gp.language_id = l.id
        WHERE gp.player_id = %s
        ORDER BY l.language_name
        """
        return self.execute_query(query, (player_id,), fetch=True)
    
    def get_all_languages(self):
        query = "SELECT id, language_name, language_code, is_active FROM languages ORDER BY id"
        return self.execute_query(query, fetch=True) or []
    
    def get_all_characters(self):
        query = "SELECT id, character_name, description, base_health, base_speed, unlock_level, is_active FROM characters ORDER BY id"
        return self.execute_query(query, fetch=True) or []
    
    def get_levels_by_language(self, language_id):
        query = """
        SELECT id, level_number, level_name, difficulty, required_score, unlock_threshold, is_active
        FROM levels 
        WHERE language_id = %s
        ORDER BY level_number
        """
        return self.execute_query(query, (language_id,), fetch=True) or []
    
    def get_questions_by_level(self, level_id):
        query = """
        SELECT id, question_text, hint, question_type, difficulty_score, is_active
        FROM quiz_questions 
        WHERE level_id = %s
        ORDER BY id
        """
        return self.execute_query(query, (level_id,), fetch=True) or []
    
    def get_options_by_question(self, question_id):
        query = """
        SELECT id, option_text, is_correct, explanation, order_num
        FROM answer_options 
        WHERE question_id = %s
        ORDER BY order_num
        """
        return self.execute_query(query, (question_id,), fetch=True) or []
    
    def get_all_game_progress(self):
        query = """
        SELECT gp.id, p.username, l.language_name, 
               COALESCE(c.character_name, 'Не выбран') as character_name,
               gp.current_level, gp.total_score, gp.coins, gp.last_played,
               gp.correct_answers, gp.total_answers, gp.games_played
        FROM game_progress gp
        JOIN players p ON gp.player_id = p.id
        JOIN languages l ON gp.language_id = l.id
        LEFT JOIN characters c ON gp.character_id = c.id
        ORDER BY gp.last_played DESC
        """
        return self.execute_query(query, fetch=True) or []
    
    def get_all_answers(self):
        query = """
        SELECT pa.id, p.username, q.question_text, ao.option_text, 
               pa.is_correct, pa.time_spent, pa.answered_at
        FROM player_answers pa
        JOIN players p ON pa.player_id = p.id
        JOIN quiz_questions q ON pa.question_id = q.id
        LEFT JOIN answer_options ao ON pa.selected_option_id = ao.id
        ORDER BY pa.answered_at DESC
        """
        return self.execute_query(query, fetch=True) or []
    
    def update_player(self, player_id, field, value):
        query = sql.SQL("UPDATE players SET {} = %s WHERE id = %s").format(sql.Identifier(field))
        return self.execute_query(query, (value, player_id))
    
    def delete_player(self, player_id):
        query = "DELETE FROM players WHERE id = %s"
        return self.execute_query(query, (player_id,))
    
    def add_language(self, name, code):
        query = "INSERT INTO languages (language_name, language_code) VALUES (%s, %s)"
        return self.execute_query(query, (name, code))
    
    def delete_language(self, language_id):
        query = "DELETE FROM languages WHERE id = %s"
        return self.execute_query(query, (language_id,))
    
    def add_character(self, name, description, health, speed, unlock_level):
        query = """
        INSERT INTO characters (character_name, description, base_health, base_speed, unlock_level)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (name, description, health, speed, unlock_level))
    
    def delete_character(self, character_id):
        query = "DELETE FROM characters WHERE id = %s"
        return self.execute_query(query, (character_id,))
    
    def add_level(self, language_id, level_number, name, difficulty, required_score):
        query = """
        INSERT INTO levels (language_id, level_number, level_name, difficulty, required_score)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (language_id, level_number, name, difficulty, required_score))
    
    def delete_level(self, level_id):
        query = "DELETE FROM levels WHERE id = %s"
        return self.execute_query(query, (level_id,))
    
    def add_question(self, language_id, level_id, question_text, hint):
        if not self.connected or not self.cursor or not self.conn:
            return None
        query = """
        INSERT INTO quiz_questions (language_id, level_id, question_text, hint)
        VALUES (%s, %s, %s, %s) RETURNING id
        """
        try:
            self.cursor.execute(query, (language_id, level_id, question_text, hint))
            result = self.cursor.fetchone()
            if self.conn:
                self.conn.commit()
            return result[0] if result else None
        except Exception as e:
            print(f"Error adding question: {e}")
            if self.conn:
                self.conn.rollback()
            return None
    
    def add_answer_option(self, question_id, option_text, is_correct, order_num):
        query = """
        INSERT INTO answer_options (question_id, option_text, is_correct, order_num)
        VALUES (%s, %s, %s, %s)
        """
        return self.execute_query(query, (question_id, option_text, is_correct, order_num))
    
    def delete_question(self, question_id):
        query = "DELETE FROM quiz_questions WHERE id = %s"
        return self.execute_query(query, (question_id,))
    
    def delete_answer_option(self, option_id):
        query = "DELETE FROM answer_options WHERE id = %s"
        return self.execute_query(query, (option_id,))

class AuthWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setWindowTitle("Авторизация - ÖSU DOS")
        self.setGeometry(300, 300, 400, 200)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("ÖSU DOS - Админ Панель")
        title_label.setAlignment(getattr(Qt, 'AlignCenter', 4 | 32))  # type: ignore
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3; margin: 20px; padding: 10px; background-color: #E3F2FD; border-radius: 5px;")
        layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        
        self.dbname_input = QLineEdit()
        self.dbname_input.setPlaceholderText("osudos")
        self.dbname_input.setText("osudos")
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("postgres")
        self.user_input.setText("postgres")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("87780455396")
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost")
        self.host_input.setText("localhost")
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("5432")
        self.port_input.setText("5432")
        
        form_layout.addRow("База данных:", self.dbname_input)
        form_layout.addRow("Пользователь:", self.user_input)
        form_layout.addRow("Пароль:", self.password_input)
        form_layout.addRow("Хост:", self.host_input)
        form_layout.addRow("Порт:", self.port_input)
        
        layout.addLayout(form_layout)
        
        buttons_layout = QHBoxLayout()
        
        self.btn_connect = QPushButton("Подключиться")
        self.btn_connect.setStyleSheet("QPushButton {background-color: #2196F3; color: white; padding: 8px 16px; border-radius: 4px; font-weight: bold;} QPushButton:hover {background-color: #1976D2;}")
        self.btn_connect.clicked.connect(self.connect_to_db)
        
        self.btn_auto = QPushButton("Автоподключение")
        self.btn_auto.clicked.connect(self.auto_connect)
        
        buttons_layout.addWidget(self.btn_connect)
        buttons_layout.addWidget(self.btn_auto)
        
        layout.addLayout(buttons_layout)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #f44336; padding: 5px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)

    def connect_to_db(self):
        config = {
            'dbname': self.dbname_input.text(),
            'user': self.user_input.text(),
            'password': self.password_input.text(),
            'host': self.host_input.text(),
            'port': self.port_input.text()
        }
        
        success, message = self.main_window.db_manager.connect(**config)
        self.status_label.setText(message)
        
        if success:
            self.main_window.config = config
            self.main_window.save_config()
            self.main_window.initialize_database()
            self.main_window.show()
            self.close()

    def auto_connect(self):
        common_passwords = ['87780455396', 'password', 'postgres', 'admin', 'root', '']
        config = {
            'dbname': self.dbname_input.text(),
            'user': self.user_input.text(),
            'password': '',
            'host': self.host_input.text(),
            'port': self.port_input.text()
        }
        
        for password in common_passwords:
            config['password'] = password
            success, message = self.main_window.db_manager.connect(**config)
            if success:
                self.dbname_input.setText(config['dbname'])
                self.user_input.setText(config['user'])
                self.password_input.setText(password)
                self.host_input.setText(config['host'])
                self.port_input.setText(config['port'])
                
                self.status_label.setText("Автоподключение успешно! Пароль: " + password)
                self.main_window.config = config
                self.main_window.save_config()
                self.main_window.initialize_database()
                self.main_window.show()
                self.close()
                return
        
        self.status_label.setText("Автоподключение не удалось")

class StatisticsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_statistics()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Статистика OSUDOS")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3; margin: 10px; padding: 10px; background-color: #E3F2FD; border-radius: 5px;")
        layout.addWidget(title_label)
        
        stats_group = QGroupBox("Основные показатели")
        stats_group.setStyleSheet("QGroupBox {font-weight: bold; font-size: 14px; margin-top: 10px;}")
        stats_layout = QGridLayout()
        
        self.total_players_label = QLabel("0")
        self.total_players_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        
        self.total_answers_label = QLabel("0")
        self.total_answers_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF9800;")
        
        self.correct_answers_label = QLabel("0")
        self.correct_answers_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #4CAF50;")
        
        self.active_players_label = QLabel("0")
        self.active_players_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2196F3;")
        
        self.total_languages_label = QLabel("0")
        self.total_languages_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #9C27B0;")
        
        self.total_levels_label = QLabel("0")
        self.total_levels_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #FF5722;")
        
        stats_layout.addWidget(QLabel("Всего игроков:"), 0, 0)
        stats_layout.addWidget(self.total_players_label, 0, 1)
        stats_layout.addWidget(QLabel("Всего ответов:"), 0, 2)
        stats_layout.addWidget(self.total_answers_label, 0, 3)
        
        stats_layout.addWidget(QLabel("Правильных ответов:"), 1, 0)
        stats_layout.addWidget(self.correct_answers_label, 1, 1)
        stats_layout.addWidget(QLabel("Активных игроков:"), 1, 2)
        stats_layout.addWidget(self.active_players_label, 1, 3)
        
        stats_layout.addWidget(QLabel("Языков программирования:"), 2, 0)
        stats_layout.addWidget(self.total_languages_label, 2, 1)
        stats_layout.addWidget(QLabel("Уровней сложности:"), 2, 2)
        stats_layout.addWidget(self.total_levels_label, 2, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        recent_group = QGroupBox("Последние ответы")
        recent_group.setStyleSheet("QGroupBox {font-weight: bold; font-size: 14px; margin-top: 10px;}")
        recent_layout = QVBoxLayout()
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(4)
        self.recent_table.setHorizontalHeaderLabels(["Игрок", "Вопрос", "Результат", "Время"])
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.recent_table.setAlternatingRowColors(True)
        
        recent_layout.addWidget(self.recent_table)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        self.btn_refresh = QPushButton("Обновить статистику")
        self.btn_refresh.setStyleSheet("QPushButton {background-color: #4CAF50; color: white; padding: 8px; border-radius: 4px; font-weight: bold;} QPushButton:hover {background-color: #388E3C;}")
        self.btn_refresh.clicked.connect(self.load_statistics)
        layout.addWidget(self.btn_refresh)
        
        layout.addStretch()
        self.setLayout(layout)

    def load_statistics(self):
        if not self.db_manager.connected:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных!")
            return
            
        try:
            # Получаем базовую статистику
            result = self.db_manager.execute_query("SELECT COUNT(*) FROM players", fetch=True)
            self.total_players_label.setText(str(result[0][0] if result else 0))
            
            result = self.db_manager.execute_query("SELECT COUNT(*) FROM player_answers", fetch=True)
            self.total_answers_label.setText(str(result[0][0] if result else 0))
            
            result = self.db_manager.execute_query("SELECT COUNT(*) FROM player_answers WHERE is_correct = TRUE", fetch=True)
            self.correct_answers_label.setText(str(result[0][0] if result else 0))
            
            result = self.db_manager.execute_query("SELECT COUNT(*) FROM languages", fetch=True)
            self.total_languages_label.setText(str(result[0][0] if result else 0))
            
            result = self.db_manager.execute_query("SELECT COUNT(*) FROM levels", fetch=True)
            self.total_levels_label.setText(str(result[0][0] if result else 0))
            
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            result = self.db_manager.execute_query(
                "SELECT COUNT(DISTINCT player_id) FROM player_answers WHERE answered_at > %s", 
                (week_ago,), fetch=True
            )
            self.active_players_label.setText(str(result[0][0] if result else 0))
            
            # Последние ответы
            recent_answers = self.db_manager.get_all_answers()[:10]
            self.recent_table.setRowCount(len(recent_answers))
            
            for row_idx, answer in enumerate(recent_answers):
                if len(answer) >= 6:
                    _, username, question_text, option_text, is_correct, answered_at = answer
                    
                    self.recent_table.setItem(row_idx, 0, QTableWidgetItem(str(username)))
                    
                    question_display = question_text[:100] + "..." if question_text and len(question_text) > 100 else (question_text or "")
                    self.recent_table.setItem(row_idx, 1, QTableWidgetItem(question_display))
                    
                    result_text = "✓ Правильно" if is_correct else "✗ Неправильно"
                    result_item = QTableWidgetItem(result_text)
                    if is_correct:
                        result_item.setBackground(QColor(200, 255, 200))
                    else:
                        result_item.setBackground(QColor(255, 200, 200))
                    self.recent_table.setItem(row_idx, 2, result_item)
                    
                    if answered_at:
                        try:
                            if isinstance(answered_at, datetime):
                                time_str = answered_at.strftime("%d.%m.%Y %H:%M")
                            else:
                                try:
                                    dt = datetime.strptime(str(answered_at), "%Y-%m-%d %H:%M:%S")
                                    time_str = dt.strftime("%d.%m.%Y %H:%M")
                                except:
                                    time_str = str(answered_at)
                        except:
                            time_str = str(answered_at)
                    else:
                        time_str = ""
                    self.recent_table.setItem(row_idx, 3, QTableWidgetItem(time_str))
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить статистику: " + str(e))

class PlayersView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_player_id = None
        self.setup_ui()
        self.load_players()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        
        # Левая панель - список игроков
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        title_label = QLabel("Список игроков")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        left_layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск игрока...")
        self.search_input.textChanged.connect(self.load_players)
        
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        self.players_table = QTableWidget()
        self.players_table.setColumnCount(3)
        self.players_table.setHorizontalHeaderLabels(["ID", "Имя", "Дата регистрации"])
        self.players_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.players_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.players_table.setAlternatingRowColors(True)
        self.players_table.cellClicked.connect(self.show_player_details)
        
        left_layout.addWidget(self.players_table)
        
        # Правая панель - детали игрока
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.player_details_label = QLabel("Выберите игрока")
        self.player_details_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        right_layout.addWidget(self.player_details_label)
        
        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout()
        
        self.player_username = QLabel("-")
        self.player_fullname = QLabel("-")
        self.player_email = QLabel("-")
        self.player_birthdate = QLabel("-")
        self.player_interface_lang = QLabel("-")
        self.player_sound = QLabel("-")
        self.player_music = QLabel("-")
        self.player_created = QLabel("-")
        self.player_last_login = QLabel("-")
        
        info_layout.addRow("Логин:", self.player_username)
        info_layout.addRow("Полное имя:", self.player_fullname)
        info_layout.addRow("Email:", self.player_email)
        info_layout.addRow("Дата рождения:", self.player_birthdate)
        info_layout.addRow("Язык интерфейса:", self.player_interface_lang)
        info_layout.addRow("Звук включен:", self.player_sound)
        info_layout.addRow("Музыка включена:", self.player_music)
        info_layout.addRow("Дата регистрации:", self.player_created)
        info_layout.addRow("Последний вход:", self.player_last_login)
        
        info_group.setLayout(info_layout)
        right_layout.addWidget(info_group)
        
        # Статистика по языкам
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(8)
        self.stats_table.setHorizontalHeaderLabels(["Язык", "Персонаж", "Уровень", "Очки", "Монеты", "Опыт", "Игр", "Точность %"])
        self.stats_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        right_layout.addWidget(self.stats_table)
        
        # Таблица с ответами игрока
        answers_label = QLabel("Ответы игрока:")
        answers_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(answers_label)
        
        self.answers_table = QTableWidget()
        self.answers_table.setColumnCount(5)
        self.answers_table.setHorizontalHeaderLabels(["Вопрос", "Ответ", "Правильный", "Время", "Дата"])
        self.answers_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.answers_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.answers_table)
        
        buttons_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.load_players)
        self.btn_delete = QPushButton("Удалить игрока")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete.clicked.connect(self.delete_player)
        
        buttons_layout.addWidget(self.btn_refresh)
        buttons_layout.addWidget(self.btn_delete)
        buttons_layout.addStretch()
        
        right_layout.addLayout(buttons_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)

    def load_players(self):
        if not self.db_manager.connected:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных!")
            return
            
        try:
            players = self.db_manager.get_all_players()
            print(f"Загружено игроков: {len(players) if players else 0}")
            if not players:
                self.players_table.setRowCount(0)
                print("Список игроков пуст")
                return
            
            search_text = self.search_input.text().lower().strip()
            
            filtered_players = []
            for player in players:
                if not player or len(player) < 2:
                    continue
                
                # Если поиск пустой, показываем всех
                if not search_text:
                    filtered_players.append(player)
                else:
                    # Фильтруем по поисковому запросу
                    username = str(player[1]).lower() if player[1] else ""
                    full_name = str(player[2]).lower() if player[2] else ""
                    player_id_str = str(player[0]).lower() if len(player) > 0 else ""
                    
                    if (search_text in username or 
                        search_text in full_name or 
                        search_text in player_id_str):
                        filtered_players.append(player)
            
            # Устанавливаем количество строк
            self.players_table.setRowCount(len(filtered_players))
            
            # Заполняем таблицу
            for row_idx, player in enumerate(filtered_players):
                if not player:
                    continue
                
                # Безопасный доступ к элементам (данные: id, username, full_name, email, interface_language, sound_enabled, music_enabled, created_at, last_login)
                player_id = player[0] if len(player) > 0 else None
                username = player[1] if len(player) > 1 else None
                full_name = player[2] if len(player) > 2 else None
                created_at = player[7] if len(player) > 7 else None
                
                # ID
                if player_id is not None:
                    self.players_table.setItem(row_idx, 0, QTableWidgetItem(str(player_id)))
                else:
                    self.players_table.setItem(row_idx, 0, QTableWidgetItem(""))
                
                # Имя пользователя
                username_str = str(username) if username is not None else ""
                self.players_table.setItem(row_idx, 1, QTableWidgetItem(username_str))
                
                # Дата регистрации
                if created_at:
                    try:
                        if isinstance(created_at, datetime):
                            date_str = created_at.strftime("%d.%m.%Y")
                        elif isinstance(created_at, str):
                            # Попытка парсинга строки
                            date_str = created_at[:10] if len(created_at) >= 10 else created_at
                        else:
                            date_str = str(created_at)[:10]
                        self.players_table.setItem(row_idx, 2, QTableWidgetItem(date_str))
                    except Exception as e:
                        self.players_table.setItem(row_idx, 2, QTableWidgetItem(str(created_at)[:10] if created_at else ""))
                else:
                    self.players_table.setItem(row_idx, 2, QTableWidgetItem(""))
                    
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить игроков: " + str(e))
            import traceback
            traceback.print_exc()

    def show_player_details(self, row, column):
        try:
            player_id = int(self.players_table.item(row, 0).text())
            self.current_player_id = player_id
            
            player_data = self.db_manager.get_player_details(player_id)
            if player_data:
                # Основная информация
                self.player_username.setText(player_data[1])
                self.player_fullname.setText(player_data[2] or "-")
                self.player_email.setText(player_data[3] or "-")
                self.player_birthdate.setText(str(player_data[4]) if player_data[4] else "-")
                self.player_interface_lang.setText(player_data[5] or "ru")
                self.player_sound.setText("Да" if player_data[6] else "Нет")
                self.player_music.setText("Да" if player_data[7] else "Нет")
                
                if player_data[8]:  # created_at
                    if isinstance(player_data[8], datetime):
                        self.player_created.setText(player_data[8].strftime("%d.%m.%Y %H:%M"))
                    else:
                        self.player_created.setText(str(player_data[8]))
                
                if player_data[9]:  # last_login
                    if isinstance(player_data[9], datetime):
                        self.player_last_login.setText(player_data[9].strftime("%d.%m.%Y %H:%M"))
                    else:
                        self.player_last_login.setText(str(player_data[9]))
                
                self.player_details_label.setText(f"Игрок: {player_data[1]}")
                
                # Статистика
                stats = self.db_manager.get_player_statistics(player_id)
                self.stats_table.setRowCount(len(stats))
                
                for i, stat in enumerate(stats):
                    if len(stat) >= 12:
                        self.stats_table.setItem(i, 0, QTableWidgetItem(stat[1]))  # Язык
                        # Получаем имя персонажа
                        char_id = stat[11] if len(stat) > 11 else None
                        if char_id:
                            char_query = "SELECT character_name FROM characters WHERE id = %s"
                            char_result = self.db_manager.execute_query(char_query, (char_id,), fetch=True)
                            char_name = char_result[0][0] if char_result and len(char_result) > 0 else "Не выбран"
                        else:
                            char_name = "Не выбран"
                        self.stats_table.setItem(i, 1, QTableWidgetItem(char_name))  # Персонаж
                        self.stats_table.setItem(i, 2, QTableWidgetItem(str(stat[2])))  # Уровень
                        self.stats_table.setItem(i, 3, QTableWidgetItem(str(stat[3])))  # Очки
                        self.stats_table.setItem(i, 4, QTableWidgetItem(str(stat[5])))  # Монеты
                        self.stats_table.setItem(i, 5, QTableWidgetItem(str(stat[6])))  # Опыт
                        self.stats_table.setItem(i, 6, QTableWidgetItem(str(stat[7])))  # Игр
                        accuracy = stat[10] if stat[10] else "0"
                        self.stats_table.setItem(i, 7, QTableWidgetItem(str(accuracy)))  # Точность
                
                # Загружаем ответы игрока
                answers_query = """
                SELECT q.question_text, ao.option_text, pa.is_correct, pa.time_spent, pa.answered_at
                FROM player_answers pa
                JOIN quiz_questions q ON pa.question_id = q.id
                LEFT JOIN answer_options ao ON pa.selected_option_id = ao.id
                WHERE pa.player_id = %s
                ORDER BY pa.answered_at DESC
                LIMIT 100
                """
                answers = self.db_manager.execute_query(answers_query, (player_id,), fetch=True)
                self.answers_table.setRowCount(len(answers))
                
                for i, answer in enumerate(answers):
                    if len(answer) >= 5:
                        question_text = answer[0][:100] + "..." if answer[0] and len(answer[0]) > 100 else (answer[0] or "")
                        option_text = answer[1] or "Не выбран"
                        is_correct = answer[2]
                        time_spent = str(answer[3]) if answer[3] else "0"
                        answered_at = answer[4]
                        
                        self.answers_table.setItem(i, 0, QTableWidgetItem(question_text))
                        self.answers_table.setItem(i, 1, QTableWidgetItem(option_text))
                        
                        result_item = QTableWidgetItem("✓ Правильно" if is_correct else "✗ Неправильно")
                        if is_correct:
                            result_item.setBackground(QColor(200, 255, 200))
                        else:
                            result_item.setBackground(QColor(255, 200, 200))
                        self.answers_table.setItem(i, 2, result_item)
                        
                        self.answers_table.setItem(i, 3, QTableWidgetItem(time_spent + " сек"))
                        
                        if answered_at:
                            if isinstance(answered_at, datetime):
                                time_str = answered_at.strftime("%d.%m.%Y %H:%M")
                            else:
                                time_str = str(answered_at)
                        else:
                            time_str = ""
                        self.answers_table.setItem(i, 4, QTableWidgetItem(time_str))
        except Exception as e:
            print(f"Ошибка при загрузке деталей игрока: {e}")

    def delete_player(self):
        if not self.current_player_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите игрока")
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            f'Вы уверены, что хотите удалить игрока ID {self.current_player_id}?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.db_manager.delete_player(self.current_player_id)
            if result:
                QMessageBox.information(self, "Успех", "Игрок удален")
                self.load_players()
                self.current_player_id = None
                self.clear_player_details()

    def clear_player_details(self):
        self.player_details_label.setText("Выберите игрока")
        self.player_username.setText("-")
        self.player_fullname.setText("-")
        self.player_email.setText("-")
        self.player_birthdate.setText("-")
        self.player_interface_lang.setText("-")
        self.player_sound.setText("-")
        self.player_music.setText("-")
        self.player_created.setText("-")
        self.player_last_login.setText("-")
        self.stats_table.setRowCount(0)

class LanguagesView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_language_id = None
        self.setup_ui()
        self.load_languages()

    def setup_ui(self):
        main_layout = QHBoxLayout()
        
        # Левая панель - список языков
        left_panel = QWidget()
        left_panel.setMaximumWidth(300)
        left_layout = QVBoxLayout(left_panel)
        
        title_label = QLabel("Языки программирования")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        left_layout.addWidget(title_label)
        
        buttons_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить")
        self.btn_add.clicked.connect(self.add_language)
        self.btn_delete = QPushButton("Удалить")
        self.btn_delete.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_delete.clicked.connect(self.delete_language)
        
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_delete)
        left_layout.addLayout(buttons_layout)
        
        self.languages_list = QListWidget()
        self.languages_list.itemClicked.connect(self.show_language_details)
        left_layout.addWidget(self.languages_list)
        
        # Правая панель - уровни и вопросы
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.language_title = QLabel("Выберите язык")
        self.language_title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        right_layout.addWidget(self.language_title)
        
        # Уровни
        self.levels_table = QTableWidget()
        self.levels_table.setColumnCount(5)
        self.levels_table.setHorizontalHeaderLabels(["ID", "Уровень", "Название", "Сложность", "Очки"])
        self.levels_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.levels_table.cellClicked.connect(self.show_questions)
        right_layout.addWidget(self.levels_table)
        
        # Вопросы
        questions_label = QLabel("Вопросы выбранного уровня:")
        questions_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(questions_label)
        
        self.questions_table = QTableWidget()
        self.questions_table.setColumnCount(4)
        self.questions_table.setHorizontalHeaderLabels(["ID", "Вопрос", "Подсказка", "Тип"])
        self.questions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.questions_table.cellClicked.connect(self.show_answer_options)
        right_layout.addWidget(self.questions_table)
        
        # Варианты ответов
        options_label = QLabel("Варианты ответов:")
        options_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        right_layout.addWidget(options_label)
        
        self.options_table = QTableWidget()
        self.options_table.setColumnCount(4)
        self.options_table.setHorizontalHeaderLabels(["ID", "Ответ", "Правильный", "Объяснение"])
        self.options_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        right_layout.addWidget(self.options_table)
        
        # Кнопки управления
        manage_layout = QHBoxLayout()
        self.btn_add_level = QPushButton("Добавить уровень")
        self.btn_add_level.clicked.connect(self.add_level)
        self.btn_add_question = QPushButton("Добавить вопрос")
        self.btn_add_question.clicked.connect(self.add_question)
        self.btn_add_option = QPushButton("Добавить вариант")
        self.btn_add_option.clicked.connect(self.add_answer_option)
        
        manage_layout.addWidget(self.btn_add_level)
        manage_layout.addWidget(self.btn_add_question)
        manage_layout.addWidget(self.btn_add_option)
        right_layout.addLayout(manage_layout)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        self.setLayout(main_layout)

    def load_languages(self):
        if not self.db_manager.connected:
            return
            
        try:
            languages = self.db_manager.get_all_languages()
            self.languages_list.clear()
            
            for lang in languages:
                if lang and len(lang) >= 3:
                    lang_id, name, code = lang[:3]
                    item = QListWidgetItem(f"{name} ({code})")
                    item.setData(getattr(Qt, 'UserRole', 32), lang_id)  # type: ignore
                    self.languages_list.addItem(item)
        except Exception as e:
            print(f"Ошибка при загрузке языков: {e}")

    def show_language_details(self, item):
        try:
            self.current_language_id = item.data(getattr(Qt, 'UserRole', 32))  # type: ignore
            language_text = item.text()
            self.language_title.setText(f"Язык: {language_text}")
            
            # Загружаем уровни
            levels = self.db_manager.get_levels_by_language(self.current_language_id)
            self.levels_table.setRowCount(len(levels))
            
            for i, level in enumerate(levels):
                if len(level) >= 6:
                    self.levels_table.setItem(i, 0, QTableWidgetItem(str(level[0])))  # ID
                    self.levels_table.setItem(i, 1, QTableWidgetItem(str(level[1])))  # Номер
                    self.levels_table.setItem(i, 2, QTableWidgetItem(level[2] or ""))  # Название
                    self.levels_table.setItem(i, 3, QTableWidgetItem(level[3] or ""))  # Сложность
                    self.levels_table.setItem(i, 4, QTableWidgetItem(str(level[4])))  # Очки
            
            # Очищаем таблицы вопросов и ответов
            self.questions_table.setRowCount(0)
            self.options_table.setRowCount(0)
            
        except Exception as e:
            print(f"Ошибка при загрузке уровней: {e}")

    def show_questions(self, row, column):
        try:
            level_id = int(self.levels_table.item(row, 0).text())
            current_level = self.levels_table.item(row, 1).text()
            language_name = self.language_title.text().split(": ")[1]
            self.language_title.setText(f"Язык: {language_name} - Уровень {current_level}")
            
            # Загружаем вопросы
            questions = self.db_manager.get_questions_by_level(level_id)
            self.questions_table.setRowCount(len(questions))
            
            for i, question in enumerate(questions):
                if len(question) >= 5:
                    self.questions_table.setItem(i, 0, QTableWidgetItem(str(question[0])))  # ID
                    self.questions_table.setItem(i, 1, QTableWidgetItem(question[1] or ""))  # Вопрос
                    self.questions_table.setItem(i, 2, QTableWidgetItem(question[2] or ""))  # Подсказка
                    self.questions_table.setItem(i, 3, QTableWidgetItem(question[3] or ""))  # Тип
            
            # Очищаем таблицу ответов
            self.options_table.setRowCount(0)
            
        except Exception as e:
            print(f"Ошибка при загрузке вопросов: {e}")

    def show_answer_options(self, row, column):
        try:
            question_id = int(self.questions_table.item(row, 0).text())
            
            # Загружаем варианты ответов
            options = self.db_manager.get_options_by_question(question_id)
            self.options_table.setRowCount(len(options))
            
            for i, option in enumerate(options):
                if len(option) >= 4:
                    self.options_table.setItem(i, 0, QTableWidgetItem(str(option[0])))  # ID
                    self.options_table.setItem(i, 1, QTableWidgetItem(option[1] or ""))  # Ответ
                    self.options_table.setItem(i, 2, QTableWidgetItem("✓" if option[2] else "✗"))  # Правильный
                    self.options_table.setItem(i, 3, QTableWidgetItem(option[3] or ""))  # Объяснение
        except Exception as e:
            print(f"Ошибка при загрузке вариантов ответов: {e}")

    def add_language(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить язык")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Python")
        code_input = QLineEdit()
        code_input.setPlaceholderText("python")
        
        layout.addRow("Название:", name_input)
        layout.addRow("Код:", code_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            code = code_input.text().strip()
            
            if name and code:
                result = self.db_manager.add_language(name, code)
                if result:
                    QMessageBox.information(self, "Успех", "Язык добавлен")
                    self.load_languages()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить язык")

    def delete_language(self):
        if not self.current_language_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите язык")
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Вы уверены, что хотите удалить этот язык?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            result = self.db_manager.delete_language(self.current_language_id)
            if result:
                QMessageBox.information(self, "Успех", "Язык удален")
                self.current_language_id = None
                self.load_languages()
                self.levels_table.setRowCount(0)
                self.questions_table.setRowCount(0)
                self.options_table.setRowCount(0)
                self.language_title.setText("Выберите язык")

    def add_level(self):
        if not self.current_language_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите язык")
            return
            
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить уровень")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        number_input = QSpinBox()
        number_input.setRange(1, 10)
        name_input = QLineEdit()
        name_input.setPlaceholderText("Начальный уровень")
        difficulty_combo = QComboBox()
        difficulty_combo.addItems(["easy", "medium", "hard"])
        score_input = QSpinBox()
        score_input.setRange(0, 10000)
        score_input.setValue(100)
        
        layout.addRow("Номер уровня:", number_input)
        layout.addRow("Название:", name_input)
        layout.addRow("Сложность:", difficulty_combo)
        layout.addRow("Требуемые очки:", score_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            result = self.db_manager.add_level(
                self.current_language_id,
                number_input.value(),
                name_input.text(),
                difficulty_combo.currentText(),
                score_input.value()
            )
            if result:
                QMessageBox.information(self, "Успех", "Уровень добавлен")
                self.show_language_details(self.languages_list.currentItem())

    def add_question(self):
        if not self.current_language_id:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите язык")
            return
            
        current_row = self.levels_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите уровень")
            return
            
        level_id = int(self.levels_table.item(current_row, 0).text())
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить вопрос")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        question_input = QTextEdit()
        question_input.setPlaceholderText("Введите текст вопроса...")
        question_input.setMaximumHeight(100)
        
        hint_input = QTextEdit()
        hint_input.setPlaceholderText("Введите подсказку...")
        hint_input.setMaximumHeight(100)
        
        layout.addWidget(QLabel("Вопрос:"))
        layout.addWidget(question_input)
        layout.addWidget(QLabel("Подсказка:"))
        layout.addWidget(hint_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            question_text = question_input.toPlainText().strip()
            hint = hint_input.toPlainText().strip()
            
            if question_text:
                question_id = self.db_manager.add_question(
                    self.current_language_id,
                    level_id,
                    question_text,
                    hint
                )
                if question_id:
                    QMessageBox.information(self, "Успех", "Вопрос добавлен. Теперь добавьте варианты ответов.")
                    self.show_questions(current_row, 0)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить вопрос")

    def add_answer_option(self):
        current_row = self.questions_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Предупреждение", "Сначала выберите вопрос")
            return
            
        question_id = int(self.questions_table.item(current_row, 0).text())
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить вариант ответа")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        option_input = QTextEdit()
        option_input.setMaximumHeight(80)
        option_input.setPlaceholderText("Введите вариант ответа...")
        
        is_correct_check = QCheckBox("Правильный ответ")
        order_input = QSpinBox()
        order_input.setRange(0, 10)
        explanation_input = QLineEdit()
        explanation_input.setPlaceholderText("Объяснение (необязательно)")
        
        layout.addRow("Вариант ответа:", option_input)
        layout.addRow("", is_correct_check)
        layout.addRow("Порядок:", order_input)
        layout.addRow("Объяснение:", explanation_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            option_text = option_input.toPlainText().strip()
            if option_text:
                result = self.db_manager.add_answer_option(
                    question_id,
                    option_text,
                    is_correct_check.isChecked(),
                    order_input.value()
                )
                if result:
                    QMessageBox.information(self, "Успех", "Вариант ответа добавлен")
                    self.show_answer_options(current_row, 0)
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить вариант ответа")

class CharactersView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_characters()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Персонажи")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3; margin: 10px; padding: 10px; background-color: #E3F2FD; border-radius: 5px;")
        layout.addWidget(title_label)
        
        buttons_layout = QHBoxLayout()
        self.btn_add = QPushButton("Добавить персонажа")
        self.btn_add.clicked.connect(self.add_character)
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.load_characters)
        
        buttons_layout.addWidget(self.btn_add)
        buttons_layout.addWidget(self.btn_refresh)
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Имя", "Описание", "Здоровье", "Скорость", "Уровень разблокировки"])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.setLayout(layout)

    def load_characters(self):
        if not self.db_manager.connected:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных!")
            return
            
        try:
            characters = self.db_manager.get_all_characters()
            self.table.setRowCount(len(characters))
            
            for row_idx, char in enumerate(characters):
                if len(char) >= 6:
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(char[0])))  # ID
                    self.table.setItem(row_idx, 1, QTableWidgetItem(char[1] or ""))  # Имя
                    self.table.setItem(row_idx, 2, QTableWidgetItem(char[2] or ""))  # Описание
                    self.table.setItem(row_idx, 3, QTableWidgetItem(str(char[3])))  # Здоровье
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(char[4])))  # Скорость
                    self.table.setItem(row_idx, 5, QTableWidgetItem(str(char[5])))  # Уровень
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить персонажей: " + str(e))

    def add_character(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить персонажа")
        dialog.setModal(True)
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        name_input.setPlaceholderText("Новичок")
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(80)
        desc_input.setPlaceholderText("Описание персонажа...")
        health_input = QSpinBox()
        health_input.setRange(1, 500)
        health_input.setValue(100)
        speed_input = QSpinBox()
        speed_input.setRange(1, 20)
        speed_input.setValue(5)
        unlock_input = QSpinBox()
        unlock_input.setRange(1, 50)
        unlock_input.setValue(1)
        
        layout.addRow("Имя:", name_input)
        layout.addRow("Описание:", desc_input)
        layout.addRow("Здоровье:", health_input)
        layout.addRow("Скорость:", speed_input)
        layout.addRow("Уровень разблокировки:", unlock_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            description = desc_input.toPlainText().strip()
            
            if name:
                result = self.db_manager.add_character(
                    name,
                    description,
                    health_input.value(),
                    speed_input.value(),
                    unlock_input.value()
                )
                if result:
                    QMessageBox.information(self, "Успех", "Персонаж добавлен")
                    self.load_characters()
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось добавить персонажа")

class GameProgressView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.load_game_progress()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        title_label = QLabel("Прогресс игры")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #2196F3; margin: 10px; padding: 10px; background-color: #E3F2FD; border-radius: 5px;")
        layout.addWidget(title_label)
        
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по имени игрока...")
        self.search_input.textChanged.connect(self.load_game_progress)
        
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Игрок", "Язык", "Персонаж", "Уровень", "Очки", "Монеты", "Последняя игра"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        
        self.btn_refresh = QPushButton("Обновить")
        self.btn_refresh.clicked.connect(self.load_game_progress)
        layout.addWidget(self.btn_refresh)
        
        self.setLayout(layout)

    def load_game_progress(self):
        if not self.db_manager.connected:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных!")
            return
            
        try:
            progress = self.db_manager.get_all_game_progress()
            search_text = self.search_input.text().lower()
            
            filtered_progress = []
            for item in progress:
                if len(item) >= 2:
                    username = str(item[1]).lower() if item[1] else ""
                    if search_text in username:
                        filtered_progress.append(item)
            
            self.table.setRowCount(len(filtered_progress))
            
            for row_idx, prog in enumerate(filtered_progress):
                if len(prog) >= 8:
                    self.table.setItem(row_idx, 0, QTableWidgetItem(str(prog[0])))  # ID
                    self.table.setItem(row_idx, 1, QTableWidgetItem(prog[1] or ""))  # Игрок
                    self.table.setItem(row_idx, 2, QTableWidgetItem(prog[2] or ""))  # Язык
                    self.table.setItem(row_idx, 3, QTableWidgetItem(prog[3] or ""))  # Персонаж
                    self.table.setItem(row_idx, 4, QTableWidgetItem(str(prog[4])))  # Уровень
                    self.table.setItem(row_idx, 5, QTableWidgetItem(str(prog[5])))  # Очки
                    self.table.setItem(row_idx, 6, QTableWidgetItem(str(prog[6])))  # Монеты
                    
                    if prog[7]:  # last_played
                        if isinstance(prog[7], datetime):
                            time_str = prog[7].strftime("%d.%m.%Y %H:%M")
                        else:
                            time_str = str(prog[7])
                        self.table.setItem(row_idx, 7, QTableWidgetItem(time_str))
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", "Не удалось загрузить прогресс: " + str(e))

class AdminMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db_manager = DBManager()
        self.config = self.load_config()
        
        self.setWindowTitle("OSUDOS - Админ Панель")
        self.setGeometry(100, 100, 1400, 800)
        self.setup_ui()
        self.hide()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return DEFAULT_CONFIG

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except:
            pass

    def initialize_database(self):
        if self.db_manager.connected:
            success, message = self.db_manager.initialize_database()
            if success:
                QMessageBox.information(self, "Успех", message)
                self.load_data()
            else:
                QMessageBox.warning(self, "Предупреждение", message)
                self.load_data()

    def setup_ui(self):
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #f5f5f5;")
        main_layout = QHBoxLayout(central_widget)
        
        # Левая панель навигации
        left_widget = QWidget()
        left_widget.setFixedWidth(250)
        left_widget.setStyleSheet("background-color: #263238; color: white; border-right: 2px solid #37474F;")
        left_layout = QVBoxLayout(left_widget)
        
        title_label = QLabel("OSUDOS")
        title_label.setFixedHeight(80)
        title_label.setAlignment(getattr(Qt, 'AlignCenter', 4 | 32))  # type: ignore
        title_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2196F3; background-color: #37474F; border-radius: 10px; margin: 10px; padding: 10px;")
        left_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Административная панель")
        subtitle_label.setAlignment(getattr(Qt, 'AlignCenter', 4 | 32))  # type: ignore
        subtitle_label.setStyleSheet("color: #B0BEC5; font-size: 12px; margin-bottom: 20px;")
        left_layout.addWidget(subtitle_label)
        
        # Кнопки навигации
        self.btn_statistics = QPushButton("📊 Статистика")
        self.btn_players = QPushButton("👥 Игроки")
        self.btn_languages = QPushButton("💻 Языки")
        self.btn_characters = QPushButton("🎮 Персонажи")
        self.btn_progress = QPushButton("📈 Прогресс")
        
        nav_buttons = [
            self.btn_statistics,
            self.btn_players,
            self.btn_languages,
            self.btn_characters,
            self.btn_progress
        ]
        
        for btn in nav_buttons:
            btn.setFixedHeight(45)
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 14px;
                    color: white;
                    background-color: #37474F;
                    border: none;
                    text-align: left;
                    padding-left: 20px;
                    margin: 2px 10px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #2196F3;
                }
            """)
            left_layout.addWidget(btn)
        
        left_layout.addStretch()
        
        # Статус подключения
        self.connection_status = QLabel("Не подключено")
        self.connection_status.setAlignment(getattr(Qt, 'AlignCenter', 4 | 32))  # type: ignore
        self.connection_status.setStyleSheet("color: #f44336; padding: 10px; background-color: #37474F; border-radius: 5px; margin: 10px;")
        left_layout.addWidget(self.connection_status)
        
        # Кнопка отключения
        self.btn_disconnect = QPushButton("Отключиться")
        self.btn_disconnect.setFixedHeight(40)
        self.btn_disconnect.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                color: white;
                background-color: #f44336;
                border: none;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.btn_disconnect.clicked.connect(self.disconnect)
        left_layout.addWidget(self.btn_disconnect)
        
        # Центральная область с вкладками
        self.stacked_widget = QStackedWidget()
        
        # Создаем все вьюшки
        self.statistics_view = StatisticsView(self.db_manager)
        self.players_view = PlayersView(self.db_manager)
        self.languages_view = LanguagesView(self.db_manager)
        self.characters_view = CharactersView(self.db_manager)
        self.progress_view = GameProgressView(self.db_manager)
        
        # Добавляем в стекированный виджет
        self.stacked_widget.addWidget(self.statistics_view)
        self.stacked_widget.addWidget(self.players_view)
        self.stacked_widget.addWidget(self.languages_view)
        self.stacked_widget.addWidget(self.characters_view)
        self.stacked_widget.addWidget(self.progress_view)
        
        # Подключаем кнопки
        self.btn_statistics.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.btn_players.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.btn_languages.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.btn_characters.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(3))
        self.btn_progress.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(4))
        
        main_layout.addWidget(left_widget)
        main_layout.addWidget(self.stacked_widget)
        
        self.setCentralWidget(central_widget)

    def load_data(self):
        if not self.db_manager.connected:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к базе данных!")
            return
        
        self.connection_status.setText("Подключено")
        self.connection_status.setStyleSheet("color: #4CAF50; padding: 10px; background-color: #37474F; border-radius: 5px; margin: 10px;")
        
        try:
            self.statistics_view.load_statistics()
            self.players_view.load_players()
            self.languages_view.load_languages()
            self.characters_view.load_characters()
            self.progress_view.load_game_progress()
        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", "Некоторые данные не удалось загрузить: " + str(e))

    def disconnect(self):
        message = self.db_manager.disconnect()
        self.connection_status.setText("Не подключено")
        self.connection_status.setStyleSheet("color: #f44336; padding: 10px; background-color: #37474F; border-radius: 5px; margin: 10px;")
        
        self.hide()
        auth_window = AuthWindow(self)
        auth_window.show()

    def closeEvent(self, event):
        self.db_manager.disconnect()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    app.setStyleSheet("""
        QTableWidget {
            alternate-background-color: #f8f9fa;
            selection-background-color: #e3f2fd;
        }
        QHeaderView::section {
            background-color: #2196F3;
            color: white;
            padding: 5px;
            border: 1px solid #1976D2;
        }
        QLineEdit, QTextEdit {
            padding: 5px;
            border: 1px solid #bdbdbd;
            border-radius: 3px;
        }
        QLineEdit:focus, QTextEdit:focus {
            border: 2px solid #2196F3;
        }
    """)
    
    try:
        import psycopg2
    except ImportError:
        QMessageBox.critical(QApplication.activeWindow(), "Ошибка", "Библиотека psycopg2 не установлена! Установите: pip install psycopg2-binary")
        sys.exit(1)
    
    main_window = AdminMainWindow()
    auth_window = AuthWindow(main_window)
    auth_window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()