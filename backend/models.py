from sqlalchemy import Column, Text, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    fullname = Column(Text, nullable=False)
    username = Column(Text, primary_key=True)
    email = Column(Text, unique=True, nullable=False)
    password = Column(Text, nullable=False)
    gap_analysis = Column(JSON, nullable=True)  # ✅ Changed from Text to JSON
    technical_test = Column(Text, nullable=True)
    non_technical_test = Column(Text, nullable=True)
    final_result = Column(Text, nullable=True)

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash the password before storing it."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against the stored hash."""
        return pwd_context.verify(plain_password, hashed_password)


class GapTestQuestion(Base):
    __tablename__ = "gap_test_questions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    topic = Column(String, nullable=False)
    question = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)  # Store options as JSON
    answer = Column(Text, nullable=False)
    difficulty = Column(String, nullable=False)
    prerequisites = Column(JSON, nullable=True)  # Store prerequisites as JSON
