import json
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect
from database import engine
from models import Base, GapTestQuestion

print("Creating database tables...")
Base.metadata.create_all(bind=engine)

# Verify if tables exist after creation
inspector = inspect(engine)
tables = inspector.get_table_names()

if tables:
    print("✅ Tables found in database:", tables)
else:
    print("❌ No tables found! Something went wrong.")

# Load questions from JSON files into the database
def load_questions_from_json(json_file):
    """Load questions from a JSON file into the database."""
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    topic = data["topic"]
    questions = data["questions"]

    # Create a session
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    for q in questions:
        # Handle prerequisites differently for programming fundamentals
        if topic.lower() == "programming fundamentals":
            prerequisites = ", ".join(q["prerequisites"]) if isinstance(q["prerequisites"], list) else q["prerequisites"]
        else:
            prerequisites = q.get("prerequisite", "")

        question_entry = GapTestQuestion(
            topic=topic,
            question=q["question"],
            options=q["options"],
            answer=q["answer"],
            difficulty=q["difficulty"],
            prerequisites=prerequisites  # Always stored as a string
        )
        session.add(question_entry)
    
    session.commit()
    session.close()
    print(f"✅ Loaded questions from {json_file}")

# List of JSON files to load
json_files = [
    "gap_questions/programming_fundamentals.json",
    "gap_questions/data_structure_&_algorithms.json",
    "gap_questions/databases.json",
    "gap_questions/computer_networks.json",
    "gap_questions/operating_systems.json",
    "gap_questions/software_engineering.json",
    "gap_questions/cybersecurity.json",
    "gap_questions/object_oriented_programming.json"
]

print("\n📥 Loading questions into the database...")
for file in json_files:
    try:
        load_questions_from_json(file)
    except FileNotFoundError:
        print(f"❌ File not found: {file}")
    except Exception as e:
        print(f"❌ Error loading {file}: {e}")

print("\n✅ Database initialization complete!")
