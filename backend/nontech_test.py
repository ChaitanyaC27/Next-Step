from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User  # Ensure the User model is correctly imported
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

# Pydantic model for request data
class NonTechTestRequest(BaseModel):
    username: str
    responses: Dict[int, int]  # {question_id: likert_scale_value}

@router.post("/submit_non_tech_test")
def submit_non_tech_test(data: NonTechTestRequest, db: Session = Depends(get_db)):
    # Verify user exists
    user = db.query(User).filter(User.username == data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Analyze personality type
        personality_type = analyze_personality(data.responses)

        # Store result in the database
        user.non_technical_test = personality_type
        db.commit()

        return {"message": "Test submitted successfully", "personality_type": personality_type}

    except Exception as e:
        db.rollback()  # Rollback if an error occurs
        raise HTTPException(status_code=500, detail=f"Error processing test: {str(e)}")

def analyze_personality(responses: Dict[int, int]) -> str:
    """Analyze MBTI-based coder personality from responses."""
    scores = {"I": 0, "E": 0, "S": 0, "N": 0, "T": 0, "F": 0, "J": 0, "P": 0}

    # Mapping of question IDs to MBTI traits
    question_traits = {
        1: "I", 2: "S", 3: "T", 4: "J", 5: "E", 6: "N", 7: "F", 8: "P",
        9: "I", 10: "S", 11: "T", 12: "J", 13: "E", 14: "N", 15: "F", 16: "P",
        17: "I", 18: "S", 19: "T", 20: "J"
    }

    for q_id, answer in responses.items():
        if q_id not in question_traits:
            raise ValueError(f"Invalid question ID: {q_id}")  # Ensure valid questions

        trait = question_traits[q_id]

        # Normalize Likert scale: 4 (neutral) is the midpoint
        scores[trait] += (answer - 4)  # Positive if agree, negative if disagree

    # Determine MBTI type (e.g., INTJ, ENFP)
    personality = (
        ("I" if scores["I"] > scores["E"] else "E") +
        ("S" if scores["S"] > scores["N"] else "N") +
        ("T" if scores["T"] > scores["F"] else "F") +
        ("J" if scores["J"] > scores["P"] else "P")
    )

    return personality

@router.get("/get_result")
def get_result(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.non_technical_test:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"personality_type": user.non_technical_test}