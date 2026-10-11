"""
Comprehensive Student Question Bank Builder & Exporter.
Defines, validates, and seeds 317+ high-quality adaptive assessment questions for Class 7-12
across all 19 standardized assessment sections with multi-dimensional ML feature mappings.
Generates database/questions_seed.json and database/questions_seed.sql.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / '.env')


# ------------------------------------------------------------
# Standardized Options Builders
# ------------------------------------------------------------

def make_rating_options(low_label="Not Interested", high_label="Very Interested"):
    return [
        {"option_text": f"1 - {low_label}", "option_value": "1", "score": 20.0, "is_correct": False, "display_order": 1},
        {"option_text": "2 - Slight", "option_value": "2", "score": 40.0, "is_correct": False, "display_order": 2},
        {"option_text": "3 - Moderate / Neutral", "option_value": "3", "score": 60.0, "is_correct": False, "display_order": 3},
        {"option_text": "4 - High", "option_value": "4", "score": 80.0, "is_correct": False, "display_order": 4},
        {"option_text": f"5 - {high_label}", "option_value": "5", "score": 100.0, "is_correct": False, "display_order": 5}
    ]


def make_frequency_options():
    return [
        {"option_text": "1 - Never", "option_value": "1", "score": 20.0, "is_correct": False, "display_order": 1},
        {"option_text": "2 - Rarely", "option_value": "2", "score": 40.0, "is_correct": False, "display_order": 2},
        {"option_text": "3 - Sometimes", "option_value": "3", "score": 60.0, "is_correct": False, "display_order": 3},
        {"option_text": "4 - Often", "option_value": "4", "score": 80.0, "is_correct": False, "display_order": 4},
        {"option_text": "5 - Very Often", "option_value": "5", "score": 100.0, "is_correct": False, "display_order": 5}
    ]


def make_mcq(options_data, correct_idx):
    opts = []
    for i, (text, val) in enumerate(options_data):
        is_corr = (i == correct_idx)
        opts.append({
            "option_text": text,
            "option_value": str(val),
            "score": 100.0 if is_corr else 0.0,
            "is_correct": is_corr,
            "display_order": i + 1
        })
    return opts


# Self-contained master questions generator (317 Questions)
from database.master_question_definitions import get_all_master_questions

MASTER_QUESTIONS = get_all_master_questions()


def export_questions_to_json(output_path: str = "database/questions_seed.json"):
    out_file = BASE_DIR / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(MASTER_QUESTIONS, f, indent=2, ensure_ascii=False)
    print(f"[OK] Exported {len(MASTER_QUESTIONS)} questions to JSON: {out_file}")


def export_questions_to_sql(output_path: str = "database/questions_seed.sql"):
    out_file = BASE_DIR / output_path
    out_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "-- Master Questions Seed SQL",
        f"-- Total Questions: {len(MASTER_QUESTIONS)}",
        "SET FOREIGN_KEY_CHECKS = 0;",
        "TRUNCATE TABLE question_options;",
        "TRUNCATE TABLE questions;",
        "SET FOREIGN_KEY_CHECKS = 1;",
        ""
    ]

    for q in MASTER_QUESTIONS:
        code = q['question_code'].replace("'", "''")
        text = q['question_text'].replace("'", "''")
        sec_id = q['section_id']
        q_type = q['question_type']
        c_min = q['class_min']
        c_max = q['class_max']
        diff = q['difficulty']
        skill = q['skill_category']
        stream = q.get('stream_specific', 'All')
        req = 1 if q.get('is_required', True) else 0
        order = q.get('display_order', 1)
        expl = (q.get('explanation') or '').replace("'", "''")

        q_sql = (
            f"INSERT INTO questions (question_code, question_text, section_id, question_type, "
            f"class_min, class_max, difficulty, skill_category, stream_specific, is_required, "
            f"display_order, explanation, is_active) VALUES "
            f"('{code}', '{text}', {sec_id}, '{q_type}', {c_min}, {c_max}, '{diff}', '{skill}', "
            f"'{stream}', {req}, {order}, '{expl}', TRUE);"
        )
        lines.append(q_sql)

        for opt in q.get('options', []):
            opt_text = opt['option_text'].replace("'", "''")
            opt_val = str(opt['option_value']).replace("'", "''")
            score = float(opt.get('score', 0.0))
            is_corr = 1 if opt.get('is_correct', False) else 0
            opt_order = int(opt.get('display_order', 1))

            opt_sql = (
                f"INSERT INTO question_options (question_id, option_text, option_value, score, is_correct, display_order) "
                f"SELECT id, '{opt_text}', '{opt_val}', {score}, {is_corr}, {opt_order} "
                f"FROM questions WHERE question_code = '{code}';"
            )
            lines.append(opt_sql)

    with open(out_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"[OK] Exported {len(MASTER_QUESTIONS)} questions to SQL: {out_file}")


def seed_questions_into_mysql():
    host = os.getenv('DB_HOST') or os.getenv('MYSQL_HOST', 'localhost')
    user = os.getenv('DB_USER') or os.getenv('MYSQL_USER', 'root')
    password = os.getenv('DB_PASSWORD') or os.getenv('MYSQL_PASSWORD', 'abc123')
    database = os.getenv('DB_NAME') or os.getenv('MYSQL_DATABASE', 'career_recommendation_db')
    port = int(os.getenv('DB_PORT') or os.getenv('MYSQL_PORT', 3306))

    print(f"Connecting to MySQL Server at {host}:{port}/{database}...")
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        cursor = conn.cursor()
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("DELETE FROM question_options;")
        cursor.execute("DELETE FROM questions;")

        q_count = 0
        opt_count = 0

        for q in MASTER_QUESTIONS:
            cursor.execute(
                """
                INSERT INTO questions (
                    question_code, question_text, section_id, question_type,
                    class_min, class_max, difficulty, skill_category, stream_specific,
                    is_required, display_order, explanation, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE);
                """,
                (
                    q['question_code'], q['question_text'], q['section_id'], q['question_type'],
                    q['class_min'], q['class_max'], q['difficulty'], q['skill_category'],
                    q.get('stream_specific', 'All'), q['is_required'], q['display_order'],
                    q.get('explanation')
                )
            )
            q_id = cursor.lastrowid
            q_count += 1

            for opt in q.get('options', []):
                cursor.execute(
                    """
                    INSERT INTO question_options (
                        question_id, option_text, option_value, score, is_correct, display_order
                    ) VALUES (%s, %s, %s, %s, %s, %s);
                    """,
                    (
                        q_id, opt['option_text'], str(opt['option_value']),
                        float(opt.get('score', 0.0)), bool(opt.get('is_correct', False)),
                        int(opt['display_order'])
                    )
                )
                opt_count += 1

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print(f"[OK] Successfully seeded {q_count} questions and {opt_count} options into MySQL Server!")

    except Exception as e:
        if 'conn' in locals() and conn.is_connected():
            conn.rollback()
        print(f"[NOTE] MySQL seeding skipped/failed (using SQLite or offline runner): {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn and conn.is_connected():
            conn.close()


if __name__ == '__main__':
    export_questions_to_json()
    export_questions_to_sql()
    seed_questions_into_mysql()
