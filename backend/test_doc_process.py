import traceback
import os
from app.db.session import SessionLocal
from app.models.document import Document
from app.api.routes.documents import process_document_background

db = SessionLocal()
file_path = "uploads/1_R-Unit-2 (1).pdf"

# Create a dummy doc
doc = Document(filename="test.pdf", file_path=file_path, file_type="pdf", owner_id=1)
db.add(doc)
db.commit()
db.refresh(doc)

try:
    print(f"Testing process_document_background with doc_id {doc.id}")
    process_document_background(doc.id, file_path)
    
    doc_after = db.query(Document).filter(Document.id == doc.id).first()
    print("Final status:", doc_after.status)
except Exception as e:
    traceback.print_exc()
finally:
    db.close()
