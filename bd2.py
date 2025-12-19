import psycopg2
import hashlib
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connected = False
        
    def connect(self, dbname='osudos', user='postgres', password='87780455396', host='localhost', port='5432'):
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
            print("Подключено к базе данных")
            return True, "Подключение успешно"
        except Exception as e:
            return False, "Ошибка подключения: " + str(e)
    
    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.connected = False
        print("Отключено от базы данных")
    
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
                try:
                    self.cursor.execute(sql)
                except Exception as e:
                    print(f"Ошибка при создании таблицы: {e}")
        
            if self.conn:
                self.conn.commit()
        
        
            self.migrate_database()
        
            self.add_sample_data()
            return True, "Таблицы созданы"
        
        except Exception as e:
            if self.conn:
                self.conn.rollback()
            return False, "Ошибка: " + str(e)
    
    def migrate_database(self):
       
        if not self.connected or not self.cursor or not self.conn:
            return
        
        try:
            cursor = self.cursor

            
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

           
            add_column_if_not_exists("players", "email", "VARCHAR(100)")
            add_column_if_not_exists("players", "birth_date", "DATE")
            add_column_if_not_exists("players", "interface_language", "VARCHAR(10)")
           
            try:
                cursor.execute("UPDATE players SET interface_language = 'ru' WHERE interface_language IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("players", "sound_enabled", "BOOLEAN")
            try:
                cursor.execute("UPDATE players SET sound_enabled = TRUE WHERE sound_enabled IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("players", "music_enabled", "BOOLEAN")
            try:
                cursor.execute("UPDATE players SET music_enabled = TRUE WHERE music_enabled IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("players", "created_at", "TIMESTAMP")
            try:
                cursor.execute("UPDATE players SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("players", "last_login", "TIMESTAMP")

            add_column_if_not_exists("languages", "language_code", "VARCHAR(10)")
            add_column_if_not_exists("languages", "is_active", "BOOLEAN")
            try:
                cursor.execute("UPDATE languages SET is_active = TRUE WHERE is_active IS NULL")
            except Exception:
                pass

            add_column_if_not_exists("characters", "base_health", "INTEGER")
            try:
                cursor.execute("UPDATE characters SET base_health = 100 WHERE base_health IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("characters", "base_speed", "INTEGER")
            try:
                cursor.execute("UPDATE characters SET base_speed = 5 WHERE base_speed IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("characters", "unlock_level", "INTEGER")
            try:
                cursor.execute("UPDATE characters SET unlock_level = 1 WHERE unlock_level IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("characters", "is_active", "BOOLEAN")
            try:
                cursor.execute("UPDATE characters SET is_active = TRUE WHERE is_active IS NULL")
            except Exception:
                pass

     
            add_column_if_not_exists("levels", "unlock_threshold", "INTEGER")
            try:
                cursor.execute("UPDATE levels SET unlock_threshold = 0 WHERE unlock_threshold IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("levels", "is_active", "BOOLEAN")
            try:
                cursor.execute("UPDATE levels SET is_active = TRUE WHERE is_active IS NULL")
            except Exception:
                pass

            # Миграция таблицы quiz_questions
            add_column_if_not_exists("quiz_questions", "difficulty_score", "INTEGER")
            try:
                cursor.execute("UPDATE quiz_questions SET difficulty_score = 1 WHERE difficulty_score IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("quiz_questions", "is_active", "BOOLEAN")
            try:
                cursor.execute("UPDATE quiz_questions SET is_active = TRUE WHERE is_active IS NULL")
            except Exception:
                pass

            # Миграция таблицы answer_options
            add_column_if_not_exists("answer_options", "explanation", "TEXT")
            add_column_if_not_exists("answer_options", "order_num", "INTEGER")
            try:
                cursor.execute("UPDATE answer_options SET order_num = 0 WHERE order_num IS NULL")
            except Exception:
                pass

            # Миграция таблицы game_progress
            add_column_if_not_exists("game_progress", "lives_left", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET lives_left = 3 WHERE lives_left IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "coins", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET coins = 0 WHERE coins IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "experience", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET experience = 0 WHERE experience IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "games_played", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET games_played = 0 WHERE games_played IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "correct_answers", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET correct_answers = 0 WHERE correct_answers IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "total_answers", "INTEGER")
            try:
                cursor.execute("UPDATE game_progress SET total_answers = 0 WHERE total_answers IS NULL")
            except Exception:
                pass
            add_column_if_not_exists("game_progress", "last_played", "TIMESTAMP")
            try:
                cursor.execute("UPDATE game_progress SET last_played = CURRENT_TIMESTAMP WHERE last_played IS NULL")
            except Exception:
                pass

            # Коммитим все изменения миграции
            if self.conn:
                self.conn.commit()
            
        except Exception as e:
            print(f"Ошибка при миграции базы данных: {e}")
            if self.conn:
                self.conn.rollback()
    
    def add_sample_data(self):
        if not self.connected or not self.cursor or not self.conn:
            return
        try:
            # Сначала проверяем наличие колонки language_code
            self.cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name='languages' AND column_name='language_code'")
            if not self.cursor.fetchone():
                # Если колонки нет, добавляем её
                self.cursor.execute("ALTER TABLE languages ADD COLUMN language_code VARCHAR(10)")
            
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
    
    def register_player(self, username, password, full_name=None, email=None, birth_date=None):
        if not self.connected or not self.cursor or not self.conn:
            return False, "Нет подключения"
            
        try:
            self.cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
            if self.cursor.fetchone():
                return False, "Имя занято"
            
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute("INSERT INTO players (username, password_hash, full_name, email, birth_date, created_at) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id", (username, password_hash, full_name, email, birth_date, datetime.now()))
            result = self.cursor.fetchone()
            if not result:
                return False, "Ошибка при создании игрока"
            player_id = result[0]
            
            self.cursor.execute("SELECT id FROM languages WHERE is_active = TRUE")
            languages = self.cursor.fetchall()
            for lang_id in languages:
                self.cursor.execute("INSERT INTO game_progress (player_id, language_id, character_id) VALUES (%s, %s, 1)", (player_id, lang_id[0]))
            
            self.conn.commit()
            return True, player_id
            
        except Exception as e:
            self.conn.rollback()
            return False, "Ошибка: " + str(e)
    
    def login_player(self, username, password):
        if not self.connected or not self.cursor or not self.conn:
            return False, "Нет подключения"
            
        try:
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            self.cursor.execute("SELECT id, username, full_name FROM players WHERE username = %s AND password_hash = %s", (username, password_hash))
            result = self.cursor.fetchone()
            
            if result:
                player_id, username, full_name = result
                self.cursor.execute("UPDATE players SET last_login = %s WHERE id = %s", (datetime.now(), player_id))
                stats = self.get_player_stats(player_id)
                self.conn.commit()
                return True, {'id': player_id, 'username': username, 'full_name': full_name, 'stats': stats}
            else:
                return False, "Неверные данные"
                
        except Exception as e:
            return False, "Ошибка: " + str(e)
    
    def get_player_stats(self, player_id):
        if not self.connected or not self.cursor or not self.conn:
            return {}
            
        try:
            self.cursor.execute("SELECT COALESCE(SUM(pp.total_score), 0), COALESCE(SUM(pp.games_played), 0), COALESCE(SUM(pp.correct_answers), 0), COALESCE(SUM(pp.total_answers), 0), COALESCE(SUM(pp.coins), 0), COALESCE(SUM(pp.experience), 0) FROM game_progress pp WHERE pp.player_id = %s", (player_id,))
            result = self.cursor.fetchone()
            if result:
                return {'total_score': result[0] or 0, 'games_played': result[1] or 0, 'correct_answers': result[2] or 0, 'total_answers': result[3] or 0, 'coins': result[4] or 0, 'experience': result[5] or 0}
            return {}
        except Exception as e:
            print("Ошибка: " + str(e))
            return {}
    
    def get_questions_for_game(self, language_id, level_number, count=5):
        """
        Возвращает вопросы и варианты ответов для игры.
        Сделано совместимым с твоей текущей схемой БД:
        - без поля is_active
        - без поля order_num в answer_options
        """
        if not self.connected or not self.cursor or not self.conn:
            return []
            
        try:
            # Ищем уровень по language_id и level_number (без is_active)
            self.cursor.execute(
                "SELECT id FROM levels WHERE language_id = %s AND level_number = %s",
                (language_id, level_number),
            )
            result = self.cursor.fetchone()
            if not result:
                print(f"Уровень не найден для language_id={language_id}, level_number={level_number}")
                return []
            
            level_id = result[0]

            # Берём вопросы для этого уровня (без is_active, случайный порядок, ограничение по count)
            self.cursor.execute(
                """SELECT id, question_text, hint
                       FROM quiz_questions
                       WHERE language_id = %s AND level_id = %s
                       ORDER BY RANDOM()
                       LIMIT %s""",
                (language_id, level_id, count),
            )
            
            questions = []
            for row in self.cursor.fetchall():
                question_id, question_text, hint = row

                # Варианты ответов, упорядочиваем по id (так как order_num в твоей схеме нет)
                self.cursor.execute(
                    """SELECT id, option_text, is_correct
                       FROM answer_options
                       WHERE question_id = %s
                       ORDER BY id""",
                    (question_id,),
                )
                
                options = []
                for opt in self.cursor.fetchall():
                    options.append({'id': opt[0], 'text': opt[1], 'is_correct': opt[2]})
                
                questions.append({'id': question_id, 'text': question_text, 'hint': hint, 'options': options})
            
            if not questions:
                print(f"Вопросы не найдены для language_id={language_id}, level_id={level_id}")
            else:
                print(f"Загружено {len(questions)} вопросов для языка {language_id}, уровня {level_number}")
            return questions
            
        except Exception as e:
            print("Ошибка в get_questions_for_game: " + str(e))
            return []
    
    def save_game_result(self, player_id, language_id, correct_answers, total_questions, score):
        if not self.connected or not self.cursor or not self.conn:
            return False
            
        try:
            # Обновляем или создаем game_progress
            self.cursor.execute(
                """INSERT INTO game_progress (player_id, language_id, current_level, total_score, correct_answers, total_answers, games_played, last_played)
                   VALUES (%s, %s, 1, %s, %s, %s, 1, %s)
                   ON CONFLICT (player_id, language_id) 
                   DO UPDATE SET correct_answers = game_progress.correct_answers + %s, 
                                total_answers = game_progress.total_answers + %s, 
                                total_score = game_progress.total_score + %s, 
                                games_played = game_progress.games_played + 1, 
                                last_played = %s""",
                (player_id, language_id, score, correct_answers, total_questions, datetime.now(),
                 correct_answers, total_questions, score, datetime.now())
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print("Ошибка: " + str(e))
            return False
    
    def save_player_answer(self, player_id, question_id, selected_option_id, is_correct):
        """Сохраняет ответ игрока на вопрос"""
        if not self.connected or not self.cursor or not self.conn:
            return False
        
        try:
            self.cursor.execute(
                """INSERT INTO player_answers (player_id, question_id, selected_option_id, is_correct, answered_at)
                   VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                (player_id, question_id, selected_option_id, is_correct)
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Ошибка сохранения ответа: {e}")
            return False
    
    def get_all_players(self):
        if not self.connected or not self.cursor or not self.conn:
            return []
            
        try:
            self.cursor.execute("SELECT id, username, full_name, email, created_at, last_login FROM players ORDER BY created_at DESC")
            return self.cursor.fetchall()
        except Exception as e:
            print("Ошибка: " + str(e))
            return []
    
    def get_game_statistics(self):
        if not self.connected or not self.cursor or not self.conn:
            return {}
            
        try:
            stats = {}
            self.cursor.execute("SELECT COUNT(*) FROM players")
            result = self.cursor.fetchone()
            stats['total_players'] = result[0] if result else 0
            
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            self.cursor.execute("SELECT COUNT(*) FROM players WHERE last_login > %s", (week_ago,))
            result = self.cursor.fetchone()
            stats['active_players'] = result[0] if result else 0
            
            self.cursor.execute("SELECT COUNT(*) FROM player_answers")
            result = self.cursor.fetchone()
            stats['total_answers'] = result[0] if result else 0
            
            self.cursor.execute("SELECT COUNT(*) FROM player_answers WHERE is_correct = TRUE")
            result = self.cursor.fetchone()
            stats['correct_answers'] = result[0] if result else 0
            
            if stats['total_answers'] > 0:
                stats['accuracy'] = round((stats['correct_answers'] / stats['total_answers']) * 100, 2)
            else:
                stats['accuracy'] = 0
            
            self.cursor.execute("SELECT p.username, SUM(pp.total_score) as total_score FROM players p JOIN game_progress pp ON p.id = pp.player_id GROUP BY p.id, p.username ORDER BY total_score DESC LIMIT 5")
            stats['top_players'] = self.cursor.fetchall()
            
            return stats
            
        except Exception as e:
            print("Ошибка: " + str(e))
            return {}
    
    def add_question(self, language_id, level_id, question_text, hint, options):
        if not self.connected or not self.cursor or not self.conn:
            return False, "Нет подключения"
            
        try:
            self.cursor.execute("INSERT INTO quiz_questions (language_id, level_id, question_text, hint) VALUES (%s, %s, %s, %s) RETURNING id", (language_id, level_id, question_text, hint))
            result = self.cursor.fetchone()
            if not result:
                return False, "Ошибка при создании вопроса"
            question_id = result[0]
            
            for i, option in enumerate(options):
                self.cursor.execute("INSERT INTO answer_options (question_id, option_text, is_correct, order_num) VALUES (%s, %s, %s, %s)", (question_id, option['text'], option['is_correct'], i))
            
            self.conn.commit()
            return True, "Вопрос добавлен ID: " + str(question_id)
        except Exception as e:
            self.conn.rollback()
            return False, "Ошибка: " + str(e)
    
    def get_language_id_by_name(self, language_name):
        """Получает ID языка программирования по названию"""
        if not self.connected or not self.cursor:
            return None
        
        try:
            lang_map = {
                "Python": "python",
                "Java": "java",
                "C#": "csharp",
                "SQL": "sql"
            }
            lang_code = lang_map.get(language_name, language_name.lower())
            
            self.cursor.execute(
                "SELECT id FROM languages WHERE language_name = %s OR language_code = %s",
                (language_name, lang_code)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка получения ID языка: {e}")
            return None
    
    def get_character_id_by_name(self, character_name):
        """Получает ID персонажа по имени"""
        if not self.connected or not self.cursor:
            return None
        
        try:
            self.cursor.execute(
                "SELECT id FROM characters WHERE character_name = %s",
                (character_name,)
            )
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Ошибка получения ID персонажа: {e}")
            return None
    
    def create_character_if_not_exists(self, character_name, description="", health=100, speed=5, unlock=1):
        """Создает персонажа если его нет"""
        if not self.connected or not self.cursor or not self.conn:
            return None
        
        try:
            # Проверяем существует ли персонаж
            char_id = self.get_character_id_by_name(character_name)
            if char_id:
                return char_id
            
            # Создаем нового персонажа
            self.cursor.execute(
                """INSERT INTO characters (character_name, description, base_health, base_speed, unlock_level)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (character_name, description or f"Персонаж {character_name}", health, speed, unlock)
            )
            result = self.cursor.fetchone()
            if result:
                self.conn.commit()
                return result[0]
            return None
        except Exception as e:
            print(f"Ошибка создания персонажа: {e}")
            if self.conn:
                self.conn.rollback()
            return None

db = DatabaseManager() 