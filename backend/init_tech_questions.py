import json
import sqlite3

DB_PATH = "nextstep.db"
JSON_FILE = "tech_questions.json"

def create_table():
    """Creates the technical_questions table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS technical_questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        problem_statement TEXT NOT NULL,
        input_example TEXT NOT NULL,
        expected_output TEXT NOT NULL,
        constraints TEXT NOT NULL,
        min_lines INTEGER NOT NULL,
        max_lines INTEGER NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def load_questions():
    """Loads questions from tech_questions.json into the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        questions = json.load(file)

    for q in questions:
        # Check if the question already exists (to avoid duplicates)
        cursor.execute("SELECT id FROM technical_questions WHERE id = ?", (q["id"],))
        existing = cursor.fetchone()

        if not existing:
            cursor.execute("""
            INSERT INTO technical_questions (id, title, problem_statement, input_example, expected_output, constraints, min_lines, max_lines)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (q["id"], q["title"], q["problem_statement"], q["input_example"],
                  q["expected_output"], q["constraints"], q["min_lines"], q["max_lines"]))

    conn.commit()
    conn.close()
    print("Technical questions loaded successfully!")

if __name__ == "__main__":
    create_table()
    load_questions()
