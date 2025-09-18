from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
import json

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/gap_analysis/{username}")
def get_gap_analysis_result(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.gap_analysis:
        raise HTTPException(status_code=404, detail="Gap analysis result not found")
    
    # Parse the stored JSON string
    gap_analysis_data = json.loads(user.gap_analysis)

    # Extract topic ratings and average elo
    topic_ratings = gap_analysis_data.get("topic_ratings", {})
    average_elo = gap_analysis_data.get("average_elo", 0)

    return {"topic_ratings": topic_ratings, "average_elo": average_elo}

@router.get("/technical_test/{username}")
def get_technical_test_result(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not user.technical_test:
        raise HTTPException(status_code=404, detail="Technical test result not found")

    # Parse the stored JSON string
    tech_test_data = json.loads(user.technical_test)

    # Extract solved count and milestone (default to 0 if missing)
    solved = tech_test_data.get("solved", 0)
    milestone = tech_test_data.get("milestone", "0")  # Default to "0" if blank

    return {"solved": solved, "milestone": milestone}