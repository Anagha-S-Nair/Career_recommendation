"""
Script to generate a completely clean database/setup.sql from the live MySQL database,
reflecting the streamlined 5-table architecture (users, questions, assessment_sessions, careers, career_recommendations).
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

def escape_sql_val(val):
    if val is None:
        return "NULL"
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "1" if val else "0"
    if isinstance(val, (dict, list)):
        s = json.dumps(val, ensure_ascii=False)
        return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"
    s = str(val)
    return "'" + s.replace("\\", "\\\\").replace("'", "''") + "'"

def generate_setup_sql():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', 'abc123'),
        database=os.getenv('DB_NAME', 'career_recommendation_db'),
        port=int(os.getenv('DB_PORT', 3306))
    )
    cur = conn.cursor(dictionary=True)

    lines = []
    lines.append("-- ============================================================")
    lines.append("-- STREAMLINED 5-TABLE DATABASE INITIALIZATION SCRIPT")
    lines.append("-- Project: Personalized Career Recommendation System Using ML")
    lines.append("-- Database Server: MySQL 8.x / MariaDB Compatible")
    lines.append("-- Target Database: career_recommendation_db")
    lines.append("-- Strictly 5 Modern Physical Tables:")
    lines.append("--   1. users (Merged Authentication & Student Demographics)")
    lines.append("--   2. questions (with options JSON)")
    lines.append("--   3. assessment_sessions (with answers & scores JSON)")
    lines.append("--   4. careers (with required_skills & recommended_subjects JSON)")
    lines.append("--   5. career_recommendations (with match_breakdown JSON & ML confidence)")
    lines.append("-- (All roadmaps and redundant fields completely removed)")
    lines.append("-- ============================================================\n")

    lines.append("CREATE DATABASE IF NOT EXISTS `career_recommendation_db`")
    lines.append("CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;\n")
    lines.append("USE `career_recommendation_db`;\n")
    lines.append("SET NAMES utf8mb4;")
    lines.append("SET FOREIGN_KEY_CHECKS = 0;\n")

    lines.append("-- Drop existing tables (both 5 clean tables and any obsolete legacy tables)")
    drop_tables = [
        "career_recommendations", "assessment_sessions", "careers", "questions",
        "students", "users", "career_pathways", "career_education", "career_subjects",
        "career_skills", "career_clusters", "career_subdomains", "career_domains",
        "assessment_scores", "student_answers", "question_options", "question_sections",
        "academic_scores", "learning_resources", "resources", "recommendation_feedback",
        "temp_recommendations"
    ]
    for t in drop_tables:
        lines.append(f"DROP TABLE IF EXISTS `{t}`;")
    lines.append("\nSET FOREIGN_KEY_CHECKS = 1;\n")

    lines.append("-- ============================================================")
    lines.append("-- 1. DDL SCHEMAS (STRICTLY 5 TABLES)")
    lines.append("-- ============================================================\n")

    # 1.1 users (Unified Auth & Student Profile)
    lines.append("-- 1.1 Table: users (Unified Authentication & Student Demographics)")
    lines.append("""CREATE TABLE `users` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(100) NOT NULL UNIQUE,
    `email` VARCHAR(255) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `role` ENUM('student', 'admin') NOT NULL DEFAULT 'student',
    `student_code` VARCHAR(50) NULL UNIQUE,
    `first_name` VARCHAR(100) NULL,
    `last_name` VARCHAR(100) NULL,
    `age` TINYINT UNSIGNED NULL,
    `gender` VARCHAR(30) NULL,
    `class_level` TINYINT UNSIGNED NULL,
    `board` VARCHAR(100) NULL DEFAULT 'CBSE',
    `medium` VARCHAR(50) NULL DEFAULT 'English',
    `stream` VARCHAR(100) NULL DEFAULT 'General',
    `academic_scores` JSON NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_users_role` (`role`),
    INDEX `idx_users_email` (`email`),
    INDEX `idx_users_username` (`username`),
    INDEX `idx_users_class` (`class_level`),
    INDEX `idx_users_stream` (`stream`),
    INDEX `idx_users_code` (`student_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    # 1.2 questions (CLEAN: no question_code, created_at)
    lines.append("-- 1.2 Table: questions (Cleaned: no question_code, created_at)")
    lines.append("""CREATE TABLE `questions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `question_text` TEXT NOT NULL,
    `section` VARCHAR(100) NOT NULL DEFAULT 'General',
    `question_type` VARCHAR(50) NOT NULL DEFAULT 'MCQ',
    `class_min` SMALLINT NOT NULL DEFAULT 7,
    `class_max` SMALLINT NOT NULL DEFAULT 12,
    `difficulty` VARCHAR(20) DEFAULT 'Medium',
    `skill_category` VARCHAR(100) NULL,
    `stream_specific` VARCHAR(50) NULL DEFAULT 'All',
    `display_order` INT DEFAULT 0,
    `options` JSON NOT NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    INDEX `idx_questions_section` (`section`),
    INDEX `idx_questions_skill` (`skill_category`),
    INDEX `idx_questions_class` (`class_min`, `class_max`),
    INDEX `idx_questions_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    # 1.3 assessment_sessions (CLEAN: no created_at)
    lines.append("-- 1.3 Table: assessment_sessions (Foreign key links directly to users.id)")
    lines.append("""CREATE TABLE `assessment_sessions` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `student_id` BIGINT UNSIGNED NOT NULL,
    `status` ENUM('not_started', 'in_progress', 'completed', 'abandoned') NOT NULL DEFAULT 'not_started',
    `started_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `completed_at` TIMESTAMP NULL,
    `current_question` INT DEFAULT 0,
    `completion_percentage` FLOAT DEFAULT 0.0,
    `selected_question_ids` TEXT NULL,
    `answers` JSON NULL,
    `scores` JSON NULL,
    CONSTRAINT `fk_sessions_user` FOREIGN KEY (`student_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    INDEX `idx_sessions_student` (`student_id`),
    INDEX `idx_sessions_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    # 1.4 careers (CLEAN: no market_demand, growth_rate, salaries, created_at, updated_at)
    lines.append("-- 1.4 Table: careers (Cleaned: no market_demand, growth_rate, salaries, created_at, updated_at)")
    lines.append("""CREATE TABLE `careers` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `career_code` VARCHAR(50) NULL,
    `career_name` VARCHAR(200) NOT NULL,
    `domain` VARCHAR(150) NOT NULL DEFAULT 'General',
    `subdomain` VARCHAR(150) NULL,
    `cluster` VARCHAR(150) NULL,
    `description` TEXT NULL,
    `minimum_education` VARCHAR(150) NULL,
    `typical_education` VARCHAR(150) NULL,
    `required_skills` JSON NULL,
    `recommended_subjects` JSON NULL,
    `is_active` BOOLEAN DEFAULT TRUE,
    INDEX `idx_careers_code` (`career_code`),
    INDEX `idx_careers_name` (`career_name`),
    INDEX `idx_careers_domain` (`domain`),
    INDEX `idx_careers_active` (`is_active`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    # 1.5 career_recommendations (CLEAN: no created_at)
    lines.append("-- 1.5 Table: career_recommendations (ML confidence & match breakdown, no created_at)")
    lines.append("""CREATE TABLE `career_recommendations` (
    `id` BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    `assessment_id` BIGINT UNSIGNED NOT NULL,
    `career_id` BIGINT UNSIGNED NOT NULL,
    `rank_position` INT NOT NULL DEFAULT 1,
    `score` FLOAT NULL,
    `is_decisive` TINYINT(1) DEFAULT 0,
    `probability` FLOAT NULL,
    `recommendation_reason` TEXT NULL,
    `strengths` TEXT NULL,
    `skill_gaps` TEXT NULL,
    `match_breakdown` JSON NULL,
    CONSTRAINT `fk_recs_assessment` FOREIGN KEY (`assessment_id`) REFERENCES `assessment_sessions` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_recs_career` FOREIGN KEY (`career_id`) REFERENCES `careers` (`id`) ON DELETE CASCADE,
    INDEX `idx_recs_assessment` (`assessment_id`),
    INDEX `idx_recs_career` (`career_id`),
    INDEX `idx_recs_rank` (`assessment_id`, `rank_position`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;\n""")

    lines.append("-- ============================================================")
    lines.append("-- 2. SEED DATA (USERS, QUESTIONS, CAREERS)")
    lines.append("-- ============================================================")

    # 2.1 Seed Users (including student demographic fields)
    lines.append("\n-- 2.1 Seed Users (Admin and Demo Student)")
    u_cols = ['id', 'username', 'email', 'password_hash', 'role', 'student_code', 'first_name', 'last_name', 'age', 'gender', 'class_level', 'board', 'medium', 'stream', 'academic_scores']
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in u_cols)} FROM `users` WHERE `id` IN (1, 2) ORDER BY `id`")
    u_rows = cur.fetchall()
    lines.append(f"INSERT INTO `users` ({', '.join(f'`{c}`' for c in u_cols)}) VALUES")
    u_val_lines = []
    for r in u_rows:
        vals = [escape_sql_val(r[c]) for c in u_cols]
        u_val_lines.append(f"({', '.join(vals)})")
    lines.append(",\n".join(u_val_lines) + ";\n")

    # 2.2 Seed Questions
    lines.append("-- 2.2 Seed Questions (413 Master Assessment Questions - Cleaned)")
    q_cols = ['id', 'question_text', 'section', 'question_type', 'class_min', 'class_max', 'difficulty', 'skill_category', 'stream_specific', 'display_order', 'options', 'is_active']
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in q_cols)} FROM `questions` ORDER BY `id`")
    q_rows = cur.fetchall()

    lines.append(f"INSERT INTO `questions` ({', '.join(f'`{c}`' for c in q_cols)}) VALUES")
    q_val_lines = []
    for r in q_rows:
        vals = [escape_sql_val(r[c]) for c in q_cols]
        q_val_lines.append(f"({', '.join(vals)})")
    lines.append(",\n".join(q_val_lines) + ";\n")

    # 2.3 Seed Careers
    lines.append("-- 2.3 Seed Careers (158 Curated Careers - Cleaned, No Market/Salary Fields)")
    c_cols = ['id', 'career_code', 'career_name', 'domain', 'subdomain', 'cluster', 'description', 'minimum_education', 'typical_education', 'required_skills', 'recommended_subjects', 'is_active']
    cur.execute(f"SELECT {', '.join(f'`{c}`' for c in c_cols)} FROM `careers` ORDER BY `id`")
    c_rows = cur.fetchall()

    chunk_size = 200
    for i in range(0, len(c_rows), chunk_size):
        chunk = c_rows[i:i + chunk_size]
        lines.append(f"INSERT INTO `careers` ({', '.join(f'`{c}`' for c in c_cols)}) VALUES")
        c_val_lines = []
        for r in chunk:
            vals = [escape_sql_val(r[c]) for c in c_cols]
            c_val_lines.append(f"({', '.join(vals)})")
        lines.append(",\n".join(c_val_lines) + ";\n")

    conn.close()

    output_path = BASE_DIR / 'database' / 'setup.sql'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"Successfully generated {output_path} with 5 tables, {len(q_rows)} questions, and {len(c_rows)} careers!")

if __name__ == '__main__':
    generate_setup_sql()
