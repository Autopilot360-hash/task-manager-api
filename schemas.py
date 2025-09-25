from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Schémas pour les utilisateurs
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    
    class Config:  # Gardons l'ancienne syntaxe
        from_attributes = True

# Schémas pour les tâches
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Task(TaskBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: User
    
    class Config:  # Gardons l'ancienne syntaxe
        from_attributes = True

# Schéma pour l'authentification
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None