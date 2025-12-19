import psycopg2

DB_NAME = "osudos"
DB_USER = "postgres"
DB_PASSWORD = "87780455396"
DB_HOST = "localhost"
DB_PORT = "5432"


def connect_to_db():
    """
    Простое подключение к PostgreSQL.
    Если что‑то пойдет не так – вернем (None, None).
    """
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        cursor = conn.cursor()
        print("✓ Подключились к базе данных PostgreSQL")
        return conn, cursor
    except Exception as e:
        print(f"✗ Ошибка подключения к БД: {e}")
        return None, None


def load_questions_for_language(language_name, max_levels=3):
    """
    Загружает вопросы из БД для выбранного языка для уровней 1..max_levels.
    Возвращает словарь: {1: [q1, q2, ...], 2: [...], 3: [...]}
    Формат вопроса:
      {
        "question": "текст",
        "answers": ["вариант1", ...],
        "correct": 0  # индекс правильного варианта
      }
    """
    conn, cursor = connect_to_db()
    if not conn or not cursor:
        return {}

    try:
        questions_by_level = {lvl: [] for lvl in range(1, max_levels + 1)}

        # 1. Ищем язык
        cursor.execute(
            "SELECT id FROM languages WHERE language_name = %s",
            (language_name,),
        )
        lang_row = cursor.fetchone()
        if not lang_row:
            print(f"✗ Язык '{language_name}' не найден в таблице languages")
            cursor.close()
            conn.close()
            return {}

        language_id = lang_row[0]

        for level_number in range(1, max_levels + 1):
            # 2. Ищем уровень
            cursor.execute(
                "SELECT id FROM levels WHERE language_id = %s AND level_number = %s",
                (language_id, level_number),
            )
            level_row = cursor.fetchone()
            if not level_row:
                print(
                    f"✗ Уровень {level_number} для языка '{language_name}' не найден в levels"
                )
                continue

            level_id = level_row[0]

            # 3. Берем вопросы
            cursor.execute(
                """
                SELECT id, question_text
                FROM quiz_questions
                WHERE language_id = %s AND level_id = %s
                ORDER BY id
                """,
                (language_id, level_id),
            )
            q_rows = cursor.fetchall()

            for q_id, q_text in q_rows:
                # 4. Берем варианты ответов
                cursor.execute(
                    """
                    SELECT option_text, is_correct
                    FROM answer_options
                    WHERE question_id = %s
                    ORDER BY id
                    """,
                    (q_id,),
                )
                opts = cursor.fetchall()
                if len(opts) < 2:
                    # пропускаем "битые" вопросы без нормальных вариантов
                    continue

                answers = []
                correct_index = 0
                for idx, (opt_text, is_correct) in enumerate(opts):
                    answers.append(opt_text)
                    if is_correct:
                        correct_index = idx

                questions_by_level[level_number].append(
                    {
                        "question": q_text,
                        "answers": answers,
                        "correct": correct_index,
                    }
                )

        cursor.close()
        conn.close()

        for lvl in range(1, max_levels + 1):
            print(
                f"✓ Уровень {lvl}: загружено {len(questions_by_level[lvl])} вопросов из БД для языка '{language_name}'"
            )

        return questions_by_level
    except Exception as e:
        print(f"✗ Ошибка при загрузке вопросов из БД: {e}")
        try:
            cursor.close()
            conn.close()
        except Exception:
            pass
        return {}


