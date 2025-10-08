"""
Main FastAPI Application
Simple API for Academic Assignment Helper
"""

import os
import shutil
import json
from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import requests

from models import (
    Student, Assignment, AnalysisResult, AcademicSource,
    UserCreate, UserResponse, Token, AssignmentResponse, AnalysisResponse,
    get_db, create_tables, SessionLocal
)
from auth import hash_password, authenticate_user, create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from rag_service import RAGService

# Create FastAPI app
app = FastAPI(
    title="Academic Assignment Helper API",
    description="Simple API for assignment analysis and plagiarism detection",
    version="1.0.0"
)

# Enable CORS (allows frontend to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    populate_database_sources()
    print("✅ Server started successfully!")


# ===== AUTHENTICATION ENDPOINTS =====

@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new student account"""
    
    # Check if email already exists
    existing_user = db.query(Student).filter(Student.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new student
    new_student = Student(
        email=user.email,
        password_hash=hash_password(user.password),
        full_name=user.full_name,
        student_id=user.student_id
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_student


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login and get access token"""
    
    # Authenticate user
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


# ===== ASSIGNMENT ENDPOINTS =====

@app.post("/upload", response_model=AssignmentResponse)
async def upload_assignment(
    file: UploadFile = File(...),
    topic: str = Form(...),
    academic_level: str = Form(...),
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an assignment file"""
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    
    # Save file
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Read file content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        content = "[Could not read file content]"
    
    # Create assignment record
    assignment = Assignment(
        student_id=current_user.id,
        filename=file.filename,
        original_text=content,
        topic=topic,
        academic_level=academic_level,
        word_count=len(content.split())
    )
    
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # Trigger n8n webhook (optional)
    try:
        n8n_url = os.getenv("N8N_WEBHOOK_URL")
        if n8n_url:
            requests.post(n8n_url, json={
                "assignment_id": assignment.id,
                "student_id": current_user.id,
                "file_path": file_path,
                "topic": topic
            }, timeout=5)
    except:
        pass  # Continue even if n8n fails
    
    return assignment


@app.get("/assignments", response_model=List[AssignmentResponse])
async def get_assignments(
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assignments for current user"""
    assignments = db.query(Assignment).filter(
        Assignment.student_id == current_user.id
    ).all()
    
    return assignments


# ===== ANALYSIS ENDPOINTS =====

@app.get("/analysis/{assignment_id}", response_model=AnalysisResponse)
async def get_analysis(
    assignment_id: int,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis results for an assignment"""
    
    # Get assignment
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.student_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    # Check if analysis exists
    if assignment.analysis:
        return assignment.analysis
    
    # Create new analysis
    rag_service = RAGService(db)
    
    # Run plagiarism detection
    plagiarism_results = rag_service.detect_plagiarism(assignment.original_text)
    
    # Get source suggestions
    sources = rag_service.search_similar_documents(
        query=assignment.original_text,
        top_k=5
    )
    
    # Create analysis record
    analysis = AnalysisResult(
        assignment_id=assignment.id,
        suggested_sources=sources,
        plagiarism_score=plagiarism_results["plagiarism_score"],
        flagged_sections={"matches": plagiarism_results["matches"]},
        research_suggestions="Based on your assignment, consider exploring related academic papers.",
        citation_recommendations="Use APA format for citations. Include author, year, and title.",
        confidence_score=0.85
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return analysis


# ===== SOURCE SEARCH ENDPOINT =====

@app.get("/sources")
async def search_sources(
    query: str,
    limit: int = 10,
    current_user: Student = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Search academic sources"""
    rag_service = RAGService(db)
    results = rag_service.search_similar_documents(query, top_k=limit)
    return results


# ===== HEALTH CHECK =====

@app.get("/health")
async def health_check():
    """Check if API is running"""
    return {"status": "ok", "message": "API is running"}


# ===== DATABASE POPULATION FUNCTION =====

def populate_database_sources():
    """
    Populate the database with academic sources from sample data file.
    This function reads data/sample_academic_sources.json, generates embeddings,
    and inserts records into the academic_sources table.
    """
    print("📚 Checking academic sources database...")
    
    db = SessionLocal()
    try:
        # Check if sources already exist
        existing_count = db.query(AcademicSource).count()
        
        if existing_count > 0:
            print(f"✅ Database already contains {existing_count} academic sources")
            return
        
        # Path to sample data file (mounted from host)
        data_file = os.path.join('/app', 'data', 'sample_academic_sources.json')
        
        # Check if file exists
        if not os.path.exists(data_file):
            print(f"⚠️  Warning: Sample data file not found at {data_file}")
            print("   Skipping database population.")
            return
        
        # Load sample data
        print(f"📖 Loading academic sources from {data_file}...")
        with open(data_file, 'r', encoding='utf-8') as f:
            sources_data = json.load(f)
        
        print(f"   Found {len(sources_data)} sources to process")
        
        # Check if OpenAI API key is configured
        openai_key = os.getenv('OPENAI_API_KEY', '')
        has_openai = openai_key and openai_key != 'your-openai-api-key-here'
        
        if not has_openai:
            print("⚠️  Warning: OPENAI_API_KEY not configured")
            print("   Academic sources will be added WITHOUT embeddings")
            print("   Plagiarism detection will not work until embeddings are added")
        
        # Initialize RAG service for embeddings
        rag_service = RAGService(db) if has_openai else None
        
        # Process each source
        added_count = 0
        for idx, source_data in enumerate(sources_data, 1):
            try:
                print(f"   [{idx}/{len(sources_data)}] Processing: {source_data['title']}")
                
                # Generate embedding if OpenAI is available
                embedding = None
                if rag_service:
                    # Use abstract for embedding (faster than full text)
                    text_to_embed = source_data.get('abstract', '') or source_data.get('full_text', '')
                    if text_to_embed:
                        try:
                            embedding = rag_service.get_embedding(text_to_embed)
                            if embedding and len(embedding) > 0:
                                print(f"      ✓ Generated embedding ({len(embedding)} dimensions)")
                            else:
                                print(f"      ⚠️  Warning: Empty embedding returned, skipping embedding")
                                embedding = None
                        except Exception as e:
                            print(f"      ⚠️  Warning: Failed to generate embedding: {str(e)}")
                            embedding = None
                
                # Only add source if we have a valid embedding OR if OpenAI is not configured
                # Skip sources with empty embeddings when OpenAI is configured
                if embedding is None and has_openai:
                    print(f"      ⚠️  Skipping source (no valid embedding)")
                    continue
                
                # Create academic source record
                source = AcademicSource(
                    title=source_data['title'],
                    authors=source_data.get('authors', ''),
                    publication_year=source_data.get('publication_year'),
                    abstract=source_data.get('abstract', ''),
                    full_text=source_data.get('full_text', ''),
                    source_type=source_data.get('source_type', 'paper'),
                    embedding=embedding
                )
                
                db.add(source)
                added_count += 1
                print(f"      ✓ Added to database")
                
            except Exception as e:
                print(f"      ❌ Error processing source: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        print(f"✅ Successfully added {added_count} academic sources to database")
        
        if not has_openai:
            print("\n💡 Tip: Set OPENAI_API_KEY environment variable to enable embeddings")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
