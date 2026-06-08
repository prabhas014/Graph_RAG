import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.schemas import DocumentResponse

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

from app.services.extraction_service import extract_text, chunk_text
from app.ai.gemini_client import extract_entities, extract_relationships, embed_text
from app.graph.neo4j_client import neo4j_client
from app.vector.chroma_client import chroma_client

from app.db.session import SessionLocal

def process_document_background(doc_id: int, file_path: str):
    db = SessionLocal()
    try:
        # Mark as processing
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return
        doc.status = DocumentStatus.PROCESSING
        db.commit()

        # Extract text
        text = extract_text(file_path, doc.file_type)
        
        # Phase 2 Entity/Relationship Extraction & Neo4j insertion
        entities = extract_entities(text)
        relationships = extract_relationships(text, entities)
        if entities or relationships:
            neo4j_client.build_graph(entities, relationships)
        
        # Phase 3 Embeddings & ChromaDB insertion
        chunks = chunk_text(text)
        if chunks:
            embeddings = embed_text(chunks)
            if embeddings:
                chroma_client.add_chunks(doc.id, chunks, embeddings)
        
        doc.status = DocumentStatus.COMPLETED
        db.commit()
    except Exception as e:
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.status = DocumentStatus.FAILED
            db.commit()
        print(f"Error processing document {doc_id}: {e}")
    finally:
        db.close()

@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db)
):
    # Mock current user for testing without frontend auth
    current_user_id = 1
    
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, f"{current_user_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    doc = Document(
        filename=file.filename,
        file_path=file_path,
        file_type=ext.replace(".", ""),
        owner_id=current_user_id
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    # Trigger processing
    background_tasks.add_task(process_document_background, doc.id, file_path)
    
    return doc

@router.get("/", response_model=list[DocumentResponse])
def get_documents(
    db: Session = Depends(deps.get_db)
):
    return db.query(Document).all()
