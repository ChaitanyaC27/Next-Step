from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from database import SessionLocal
from models import User
from schemas import UserCreate, UserLogin

# Secret key for JWT
SECRET_KEY = "your_secret_key_here"  # Ensure this is the same across your backend
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")  # Extracts token from Authorization header

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    """Hash the password before storing it."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_access_token(token: str = Depends(oauth2_scheme)):
    """Verify and decode a JWT token, ensuring it's valid."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload  # Return decoded token data
    except JWTError:
        raise credentials_exception

# 🟢 NEW FUNCTION: Get the current authenticated user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieve the authenticated user from the JWT token."""
    token_data = verify_access_token(token)
    username: str = token_data.get("sub")

    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token")

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

# 🟢 SIGNUP ROUTE
@router.post("/signup")
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user."""
    existing_user = db.query(User).filter((User.username == user.username) | (User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or Email already taken")

    hashed_password = hash_password(user.password)

    new_user = User(
        fullname=user.fullname,
        username=user.username,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User created successfully"}

# 🔵 LOGIN ROUTE
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Authenticates user and returns JWT token."""
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user or not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    # Generate JWT token
    access_token = create_access_token(data={"sub": existing_user.username})

    return {"access_token": access_token, "token_type": "bearer"}

# 🔒 PROTECTED ROUTE (EXAMPLE)
@router.get("/protected")
def protected_route(token_data: dict = Depends(verify_access_token)):
    """Example protected route."""
    return {"message": "Access granted!", "user": token_data}
