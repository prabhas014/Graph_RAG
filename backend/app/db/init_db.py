from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine
# Import all models here so metadata is registered
from app.models.user import User
from app.models.document import Document

def init_db():
    Base.metadata.create_all(bind=engine)
