from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timezone
from app.db.base import Base

class DocumentStatus(enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User")
