from sqlalchemy.orm import declarative_base, sessionmaker, relationship  # Changement ici

# ... reste identique

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Configuration SQLite (simple pour débuter)
SQLALCHEMY_DATABASE_URL = "sqlite:///./tasks.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modèles de base de données
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    tasks = relationship("Task", back_populates="owner")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, default="todo")  # todo, in_progress, done
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="tasks")

# Fonction pour obtenir la session DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
