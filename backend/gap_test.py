from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import random
import json
import logging

from database import get_db
from models import GapTestQuestion, User
from schemas import QuestionResponse, GapTestResponse
from auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

# Constants
TOPICS = [
    "Programming Fundamentals", "Data Structures & Algorithms", "Databases",
    "Operating Systems", "Computer Networks", "Object-Oriented Programming (OOP)",
    "Software Engineering", "Cybersecurity"
]
DIFFICULTY_RATINGS = {"easy": 800, "medium": 1200, "hard": 1600}
INITIAL_TOPIC_RATING = 1200  # Starting rating for each topic
K_FACTOR = 64
ROTATION_LIMIT = 3
HISTORY_LIMIT = 10

@router.post("/reset_gap_test")
def reset_gap_test(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Resets the user's gap test data.
    Clears previous results, detailed topic ratings, average rating, and history.
    """
    try:
        # Re-fetch the user from the database for an attached instance.
        user = db.query(User).filter(User.username == user.username).first()
        if not user:
            logger.error("User not found in database.")
            raise HTTPException(status_code=404, detail="User not found")

        logger.debug(f"Before reset: {user.gap_analysis}")
        
        gap_data = {
            "topic_ratings": {topic: INITIAL_TOPIC_RATING for topic in TOPICS},
            "average_elo": INITIAL_TOPIC_RATING,
            "prev_topics": [],
            "answered_questions": []
        }
        user.gap_analysis = json.dumps(gap_data)
        
        db.commit()
        db.refresh(user)
        
        logger.debug(f"After reset: {user.gap_analysis}")
        return {"message": "Gap test progress has been reset.", "debug": user.gap_analysis}
    except Exception as e:
        logger.exception("Error resetting gap test:")
        raise HTTPException(status_code=500, detail="Failed to reset gap test.")

@router.get("/next_gap_question", response_model=QuestionResponse)
def next_gap_question(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Fetches the next question based on the user's performance and history.
    Uses the detailed per-topic rating stored in gap_analysis.
    """
    # Re-fetch the user from the database.
    user = db.query(User).filter(User.username == user.username).first()
    
    try:
        gap_analysis = json.loads(user.gap_analysis) if user.gap_analysis else {}
    except json.JSONDecodeError:
        gap_analysis = {}
    
    # Initialize test-specific variables if not present.
    gap_analysis.setdefault("topic_ratings", {topic: INITIAL_TOPIC_RATING for topic in TOPICS})
    gap_analysis.setdefault("prev_topics", [])
    gap_analysis.setdefault("answered_questions", [])

    prev_topics = gap_analysis["prev_topics"]
    answered_questions = set(gap_analysis["answered_questions"])

    # Ensure rotation: do not repeat topics more than ROTATION_LIMIT times.
    valid_topics = [t for t in TOPICS if prev_topics.count(t) < ROTATION_LIMIT]
    if not valid_topics:
        valid_topics = TOPICS
        gap_analysis["prev_topics"] = []
        prev_topics = []

    selected_topic = random.choice(valid_topics)
    current_rating = gap_analysis["topic_ratings"].get(selected_topic, INITIAL_TOPIC_RATING)

    query = db.query(GapTestQuestion).filter(GapTestQuestion.topic == selected_topic)
    if answered_questions:
        query = query.filter(GapTestQuestion.id.notin_(answered_questions))
    
    topic_questions = query.all()
    if not topic_questions:
        return {"id": 0, "question": "No more questions available for this topic", "options": []}

    categorized_questions = {
        "easy": [q for q in topic_questions if q.difficulty.lower() == "easy"],
        "medium": [q for q in topic_questions if q.difficulty.lower() == "medium"],
        "hard": [q for q in topic_questions if q.difficulty.lower() == "hard"]
    }

    # Select a question based on the current rating.
    if current_rating < 1000 and categorized_questions["easy"]:
        selected_question = random.choice(categorized_questions["easy"])
    elif current_rating < 1400 and categorized_questions["medium"]:
        selected_question = random.choice(categorized_questions["medium"])
    elif categorized_questions["hard"]:
        selected_question = random.choice(categorized_questions["hard"])
    else:
        selected_question = random.choice(topic_questions)

    # Update history.
    prev_topics.append(selected_topic)
    if len(prev_topics) > HISTORY_LIMIT:
        prev_topics.pop(0)
    
    answered_questions.add(selected_question.id)
    gap_analysis["prev_topics"] = prev_topics
    gap_analysis["answered_questions"] = list(answered_questions)

    # Commit the updated gap_analysis (no rating change here).
    user.gap_analysis = json.dumps(gap_analysis)
    db.commit()

    return {
        "id": selected_question.id,
        "question": selected_question.question,
        "options": selected_question.options
    }

@router.post("/evaluate_gap_question")
def evaluate_gap_question(
    response: GapTestResponse,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Evaluates the user's answer and updates the topic rating using the Elo formula.
    """
    user = db.query(User).filter(User.username == user.username).first()
    question = db.query(GapTestQuestion).filter(GapTestQuestion.id == response.question_id).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    topic = question.topic

    if response.answer is None:
        return {"error": "No answer provided"}

    correct = response.answer == question.answer

    try:
        gap_analysis = json.loads(user.gap_analysis) if user.gap_analysis else {}
    except json.JSONDecodeError:
        gap_analysis = {}

    topic_ratings = gap_analysis.get("topic_ratings", {t: INITIAL_TOPIC_RATING for t in TOPICS})
    current_rating = topic_ratings.get(topic, INITIAL_TOPIC_RATING)
    question_difficulty = DIFFICULTY_RATINGS.get(question.difficulty.lower(), INITIAL_TOPIC_RATING)

    # Sharper drops than rises
    if correct:
        if current_rating < 1000:
            K = 64  # Decent rise for lower ratings
        elif current_rating < 1400:
            K = 48  # Moderate rise
        else:
            K = 32  # Slower rise at high ratings
    else:
        if current_rating > 1400:
            K = 100  # Big drop for high-rated users
        elif current_rating > 1000:
            K = 120  # Even bigger drop for mid-rated users
        else:
            K = 140  # Massive drop if already struggling

    expected_score = 1 / (1 + 10 ** ((question_difficulty - current_rating) / 400))
    actual_score = 1 if correct else 0
    new_rating = int(current_rating + K * (actual_score - expected_score))

    # Make drops sharper than rises
    if not correct:
        new_rating = int(current_rating - (K * (1 - expected_score) * 1.2))  # 20% sharper drop

    # Prevent the rating from going above 1600 or below 500
    new_rating = max(500, min(new_rating, 1600))

    topic_ratings[topic] = new_rating
    average_rating = int(sum(topic_ratings.values()) / len(topic_ratings))

    gap_analysis["topic_ratings"] = topic_ratings
    gap_analysis["average_elo"] = average_rating
    user.gap_analysis = json.dumps(gap_analysis)

    db.commit()

    return {"correct": correct, "new_rating": new_rating}
