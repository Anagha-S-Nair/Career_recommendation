"""
Database Initialization and Seeding Script for MySQL Server.
Re-creates the database from scratch and executes database/setup.sql directly into MySQL Server.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import mysql.connector

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
load_dotenv(BASE_DIR / '.env')


def split_sql_statements(sql_text):
    """Splits a multi-statement SQL script into individual executable statements."""
    statements = []
    current_stmt = []
    in_single_quote = False
    in_double_quote = False
    in_backtick = False

    lines = sql_text.splitlines()
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('--') or (stripped.startswith('/*') and stripped.endswith('*/')):
            continue

        i = 0
        while i < len(line):
            char = line[i]
            if char == "'" and not in_double_quote and not in_backtick:
                if i == 0 or line[i - 1] != '\\':
                    in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote and not in_backtick:
                if i == 0 or line[i - 1] != '\\':
                    in_double_quote = not in_double_quote
            elif char == '`' and not in_single_quote and not in_double_quote:
                in_backtick = not in_backtick
            elif char == ';' and not in_single_quote and not in_double_quote and not in_backtick:
                current_stmt.append(line[:i])
                stmt_str = "\n".join(current_stmt).strip()
                if stmt_str:
                    statements.append(stmt_str)
                current_stmt = []
                line = line[i + 1:]
                i = -1
            i += 1

        if line:
            current_stmt.append(line)

    final_stmt = "\n".join(current_stmt).strip()
    if final_stmt:
        statements.append(final_stmt)

    return statements


def execute_sql_file(cursor, file_path):
    """Reads and executes all SQL statements from a file."""
    print(f"Executing {file_path.name}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    stmts = split_sql_statements(sql_content)
    total = len(stmts)
    print(f"Executing {total} SQL statements...")
    for idx, stmt in enumerate(stmts, 1):
        if stmt:
            cursor.execute(stmt)
            if idx % 500 == 0:
                print(f"Progress: {idx}/{total} statements executed...")


def seed_mysql_database():
    """Main MySQL seeder function."""
    user = os.getenv('DB_USER', 'root')
    password = os.getenv('DB_PASSWORD', 'abc123')
    host = os.getenv('DB_HOST', 'localhost')
    port = int(os.getenv('DB_PORT', 3306))
    db_name = os.getenv('DB_NAME', 'career_recommendation_db')

    print(f"Connecting to MySQL Server on {host}:{port}...")
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        port=port,
        autocommit=True
    )
    cursor = conn.cursor()

    # Step 1: Re-create Database cleanly
    cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`;")
    cursor.execute(f"CREATE DATABASE `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
    cursor.execute(f"USE `{db_name}`;")

    # Step 2: Execute all-in-one setup.sql
    setup_file = BASE_DIR / 'database' / 'setup.sql'
    execute_sql_file(cursor, setup_file)

    cursor.close()
    conn.close()
    print("SUCCESS: MySQL Database initialized and fully seeded with setup.sql!")


if __name__ == '__main__':
    seed_mysql_database()
