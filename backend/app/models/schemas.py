from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.document import DocumentStatus

# Token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None

# User
class UserBase(BaseModel):
    email: EmailStr
    is_active: Optional[bool] = True
    is_admin: Optional[bool] = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True

# Document
class DocumentBase(BaseModel):
    filename: str
    file_type: str

class DocumentCreate(DocumentBase):
    file_path: str

class DocumentResponse(DocumentBase):
    id: int
    status: DocumentStatus
    uploaded_at: datetime
    owner_id: int

    class Config:
        from_attributes = True
