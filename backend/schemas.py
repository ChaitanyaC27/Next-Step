from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    fullname: str
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenData(BaseModel):
    sub: str  # This represents the username in the JWT token

# ✅ Schema for fetching the next question
class QuestionResponse(BaseModel):
    id: int
    question: str
    options: List[str]

# ✅ Schema for submitting an answer
class GapTestResponse(BaseModel):
    question_id: int  # 🔄 Changed from str → int for consistency
    answer: str  # Selected answer (e.g., "A", "B", "C", "D")

# ✅ Schema for evaluating response
class AnswerEvaluation(BaseModel):
    correct: bool
    new_elo: int
