import requests
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3
import json

router = APIRouter()

DB_PATH = "nextstep.db"
PISTON_API_URL = "https://emkc.org/api/v2/piston/execute"  # Piston API endpoint
TOTAL_QUESTIONS = 15  # Total number of questions

### 📌 SCHEMAS ###
class AnswerRequest(BaseModel):
    username: str
    question_id: int
    user_code: str
    language: str  # User-selected language

class TechResultResponse(BaseModel):
    solved: int
    milestone: str

class EndTestRequest(BaseModel):
    username: str

class StartTestRequest(BaseModel):
    username: str

### 📌 HELPER FUNCTIONS ###
def get_question_by_id(question_id):
    """Fetch a technical question by its ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Removed language column since it's not stored in our JSON DB.
    cursor.execute("""
        SELECT id, title, problem_statement, input_example, expected_output, 
               constraints, min_lines, max_lines 
        FROM technical_questions 
        WHERE id = ?
    """, (question_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row[0],
            "title": row[1],
            "problem_statement": row[2],
            "input_example": row[3],
            "expected_output": row[4],
            "constraints": row[5],
            "min_lines": row[6],
            "max_lines": row[7]
        }
    return None

def get_user_progress(username):
    """Fetch user progress from the User table."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT technical_test FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and row[0]:
        return json.loads(row[0])
    return {"solved": 0, "milestone": "Not Started"}

def update_user_progress(username, solved_count):
    """Update the user's progress in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if solved_count >= 15:
        milestone = "Completed 15 Questions"
    elif solved_count >= 10:
        milestone = "10 Questions Solved"
    elif solved_count >= 5:
        milestone = "5 Questions Solved"
    else:
        milestone = f"{solved_count} Questions Solved"

    test_result = {"solved": solved_count, "milestone": milestone}
    test_result_json = json.dumps(test_result)

    cursor.execute("UPDATE users SET technical_test = ? WHERE username = ?", (test_result_json, username))
    conn.commit()
    conn.close()

def count_lines_of_code(code):
    """Count the number of non-empty lines in the user's code."""
    return len([line for line in code.split("\n") if line.strip()])

def execute_code(language, user_code, input_example):
    """Execute user code using PistonAPI with the user-selected language."""
    payload = {
        "language": language,
        "version": "*",  # Latest version
        "files": [{"name": "main", "content": user_code}],
        "stdin": input_example
    }
    response = requests.post(PISTON_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("run", {}).get("output", "").strip()
    return None

### 📌 API ENDPOINTS ###

@router.post("/technical_test/start")
def start_test(data: StartTestRequest):
    """
    Resets the user's progress to zero when starting the test and returns question 1.
    """
    # Reset progress
    update_user_progress(data.username, 0)
    question = get_question_by_id(1)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.get("/technical_test/question/{question_id}")
def get_technical_question(question_id: int):
    """Fetch a specific technical test question."""
    question = get_question_by_id(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.post("/technical_test/submit_answer")
def submit_technical_answer(data: AnswerRequest):
    """Submits user code, executes it, and evaluates correctness."""
    question = get_question_by_id(data.question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    # Check line count
    lines_of_code = count_lines_of_code(data.user_code)
    if not (question["min_lines"] <= lines_of_code <= question["max_lines"]):
        raise HTTPException(
            status_code=400,
            detail=f"Code must be between {question['min_lines']} and {question['max_lines']} lines. Your code has {lines_of_code} lines."
        )

    # Execute the user's code using the selected language from the request
    output = execute_code(data.language, data.user_code, question["input_example"])
    expected_output = question["expected_output"].strip()

    if output != expected_output:
        raise HTTPException(status_code=400, detail=f"Incorrect output. Expected: {expected_output}, Got: {output}")

    # Update user progress
    user_progress = get_user_progress(data.username)
    solved_count = user_progress.get("solved", 0) + 1
    if solved_count >= 15:
        milestone = "Completed 15 Questions"
    elif solved_count >= 10:
        milestone = "10 Questions Solved"
    elif solved_count >= 5:
        milestone = "5 Questions Solved"
    else:
        milestone = f"{solved_count} Questions Solved"
    new_progress = {"solved": solved_count, "milestone": milestone}
    update_user_progress(data.username, solved_count)

    return {"message": "Correct answer!", "solved": solved_count, "milestone": milestone}

@router.post("/technical_test/end_test")
def end_test(data: EndTestRequest):
    """
    Ends the test prematurely. All unsolved questions are marked as incorrect.
    Final result is saved to the database.
    """
    user_progress = get_user_progress(data.username)
    solved = user_progress.get("solved", 0)
    unsolved = TOTAL_QUESTIONS - solved
    final_milestone = f"Test Ended: {solved} solved, {unsolved} unsolved."
    final_result = {"solved": solved, "milestone": final_milestone}
    update_user_progress(data.username, solved)
    return final_result

@router.get("/technical_test/result/{username}", response_model=TechResultResponse)
def get_technical_test_result(username: str):
    """Fetch a user's technical test result."""
    progress = get_user_progress(username)
    return TechResultResponse(solved=progress.get("solved", 0), milestone=progress.get("milestone", "Not Started"))
