"""
Database models for the Academic Assignment Helper
This file defines the structure of our database tables
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import os

# Create base class for database models
Base = declarative_base()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://student:secure_password@localhost:5432/academic_helper")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ===== DATABASE MODELS (Tables) =====

class Student(Base):
    """Students table - stores user information"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    student_id = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to assignments
    assignments = relationship("Assignment", back_populates="student")


class Assignment(Base):
    """Assignments table - stores uploaded assignments"""
    __tablename__ = "assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    filename = Column(String, nullable=False)
    original_text = Column(Text)
    topic = Column(String)
    academic_level = Column(String)
    word_count = Column(Integer)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    student = relationship("Student", back_populates="assignments")
    analysis = relationship("AnalysisResult", back_populates="assignment", uselist=False)


class AnalysisResult(Base):
    """Analysis results table - stores AI analysis of assignments"""
    __tablename__ = "analysis_results"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    suggested_sources = Column(JSONB)  # JSON data with source suggestions
    plagiarism_score = Column(Float)
    flagged_sections = Column(JSONB)  # JSON data with plagiarized sections
    research_suggestions = Column(Text)
    citation_recommendations = Column(Text)
    confidence_score = Column(Float)
    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    assignment = relationship("Assignment", back_populates="analysis")


class AcademicSource(Base):
    """Academic sources table - stores papers and materials for RAG"""
    __tablename__ = "academic_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    authors = Column(String)
    publication_year = Column(Integer)
    abstract = Column(Text)
    full_text = Column(Text)
    source_type = Column(String)  # 'paper', 'textbook', 'course_material'
    embedding = Column(Vector(1536))  # OpenAI embeddings are 1536 dimensions


# ===== PYDANTIC MODELS (For API requests/responses) =====

class UserCreate(BaseModel):
    """Model for creating a new user"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    student_id: Optional[str] = None


class UserResponse(BaseModel):
    """Model for user response"""
    id: int
    email: str
    full_name: Optional[str] = None
    student_id: Optional[str] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Model for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class AssignmentCreate(BaseModel):
    """Model for creating an assignment"""
    topic: str
    academic_level: str


class AssignmentResponse(BaseModel):
    """Model for assignment response"""
    id: int
    filename: str
    topic: Optional[str] = None
    academic_level: Optional[str] = None
    word_count: Optional[int] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisResponse(BaseModel):
    """Model for analysis result response"""
    id: int
    assignment_id: int
    plagiarism_score: Optional[float] = None
    research_suggestions: Optional[str] = None
    citation_recommendations: Optional[str] = None
    confidence_score: Optional[float] = None
    analyzed_at: datetime
    
    class Config:
        from_attributes = True


# Function to create all tables
def create_tables():
    """Create all database tables and enable pgvector extension"""
    from sqlalchemy import text
    
    # Enable pgvector extension
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
        print("✅ pgvector extension enabled")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")
