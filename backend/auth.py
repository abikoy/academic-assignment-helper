"""
Authentication module - Handles user login and security
Simple JWT authentication for beginners
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os

from models import Student, get_db

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 setup for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def hash_password(password: str) -> str:
    """Convert plain password to hashed password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if password matches the hashed version"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT token for authenticated users"""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    
    # Create the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, email: str, password: str):
    """Check if user credentials are correct"""
    # Find user by email
    user = db.query(Student).filter(Student.email == email).first()
    
    if not user:
        return False
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return False
    
    return user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get the logged-in user from their token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Get user from database
    user = db.query(Student).filter(Student.email == email).first()
    
    if user is None:
        raise credentials_exception
    
    return user
