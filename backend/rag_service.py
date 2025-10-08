"""
RAG Service - Handles document search and plagiarism detection
Simple implementation for beginners
"""

import os
from typing import List, Dict, Optional
from openai import OpenAI
from sqlalchemy.orm import Session
from models import AcademicSource
import tiktoken

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
EMBEDDING_MODEL = "text-embedding-ada-002"


class RAGService:
    """Service for RAG operations and plagiarism detection"""
    
    def __init__(self, db: Session):
        self.db = db
        self.encoder = tiktoken.get_encoding("cl100k_base")
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding vector for text using OpenAI"""
        try:
            response = client.embeddings.create(
                input=text,
                model=EMBEDDING_MODEL
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return []
    
    def search_similar_documents(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict]:
        """Search for similar academic documents using pgvector"""
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        if not query_embedding:
            return []
        
        # Use pgvector's cosine distance operator for efficient similarity search
        # The <=> operator calculates cosine distance (1 - cosine similarity)
        sources = self.db.query(
            AcademicSource
        ).filter(
            AcademicSource.embedding.isnot(None)
        ).order_by(
            AcademicSource.embedding.cosine_distance(query_embedding)
        ).limit(top_k).all()
        
        # Format results
        results = []
        for source in sources:
            if source.embedding:
                # Calculate similarity (1 - distance)
                similarity = 1 - float(source.embedding.cosine_distance(query_embedding))
                
                results.append({
                    "id": source.id,
                    "title": source.title,
                    "authors": source.authors,
                    "publication_year": source.publication_year,
                    "abstract": source.abstract,
                    "source_type": source.source_type,
                    "similarity": similarity
                })
        
        return results
    
    def detect_plagiarism(self, text: str, threshold: float = 0.85) -> Dict:
        """Check text for potential plagiarism"""
        
        # Split text into paragraphs
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        results = {
            "total_chunks": len(paragraphs),
            "plagiarized_chunks": 0,
            "plagiarism_score": 0.0,
            "matches": []
        }
        
        # Check each paragraph
        for paragraph in paragraphs:
            if len(paragraph) < 50:  # Skip very short paragraphs
                continue
            
            # Search for similar documents
            similar_docs = self.search_similar_documents(paragraph, top_k=1)
            
            if similar_docs and similar_docs[0]["similarity"] >= threshold:
                results["plagiarized_chunks"] += 1
                results["matches"].append({
                    "text": paragraph[:200] + "..." if len(paragraph) > 200 else paragraph,
                    "similarity": similar_docs[0]["similarity"],
                    "source": {
                        "title": similar_docs[0]["title"],
                        "authors": similar_docs[0]["authors"]
                    }
                })
        
        # Calculate overall plagiarism score
        if results["total_chunks"] > 0:
            results["plagiarism_score"] = results["plagiarized_chunks"] / results["total_chunks"]
        
        return results
