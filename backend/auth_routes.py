from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database import get_db
from models import User
from auth import hash_password, verify_password, create_access_token, verify_access_token
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Request Model for Signup
class SignupRequest(BaseModel):
    fullname: str
    username: str
    email: str
    password: str

# Request Model for Login
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/signup")
def signup(user_data: SignupRequest, db: Session = Depends(get_db)):
    """Registers a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check if email is already in use
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already in use")

    # Hash the password
    hashed_password = hash_password(user_data.password)

    # Create new user
    new_user = User(
        fullname=user_data.fullname,
        username=user_data.username,
        email=user_data.email,
        password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}

@router.post("/login")
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token({"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "fullname": user.fullname,
            "username": user.username,
            "email": user.email
        }
    }

@router.get("/verify-token")
def verify_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Validates the provided JWT token."""
    try:
        payload = verify_access_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Optional: Check if user still exists
        username = payload.get("sub")
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User no longer exists")

        return {"message": "Token is valid", "username": username}

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")
