import pytest
from sqlalchemy.orm import Session
from database import User, Task, get_db
from auth import get_password_hash
import uuid

def test_user_model(client):
    """Test du modèle User"""
    db = next(get_db())
    
    # Email unique pour éviter les conflits
    unique_email = f"test-{uuid.uuid4()}@db.com"
    
    user = User(
        email=unique_email,
        hashed_password=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.email == unique_email
    assert user.is_active is True
    assert len(user.tasks) == 0

def test_task_model(client):
    """Test du modèle Task avec relation"""
    db = next(get_db())
    
    # Email unique pour ce test aussi
    unique_email = f"test-task-{uuid.uuid4()}@db.com"
    
    user = User(
        email=unique_email,
        hashed_password=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Créer une tâche
    task = Task(
        title="Test Task",
        description="Description test",
        status="todo",
        owner_id=user.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.owner_id == user.id
    assert task.owner.email == unique_email
    
    # Vérifier la relation inverse
    db.refresh(user)
    assert len(user.tasks) == 1
    assert user.tasks[0].title == "Test Task"
