from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db, Task, User
from schemas import TaskCreate, TaskUpdate, Task as TaskSchema
from auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskSchema)
def create_task(
    task: TaskCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_task = Task(**task.dict(), owner_id=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

"""
@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).offset(skip).limit(limit).all()
    return tasks
"""
@router.get("/", response_model=List[TaskSchema])
def read_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of tasks to return"), 
    status: Optional[str] = Query(None, description="Filter by status: todo, in_progress, done"),
    sort_by: str = Query("created_at", description="Sort by: title, created_at, status"),
    order: str = Query("desc", description="Order: asc, desc"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve tasks with filtering, sorting, and search capabilities.
    """
    query = db.query(Task).filter(Task.owner_id == current_user.id)
    
    # Filtrer par statut
    if status:
        valid_statuses = ["todo", "in_progress", "done"]
        if status not in valid_statuses:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        query = query.filter(Task.status == status)
    
    # Recherche textuelle
    if search:
        search_filter = f"%{search.lower()}%"
        query = query.filter(
            (Task.title.ilike(search_filter)) | 
            (Task.description.ilike(search_filter))
        )
    
    # Tri
    valid_sorts = ["title", "created_at", "status"]
    if sort_by not in valid_sorts:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort_by. Must be one of: {valid_sorts}"
        )
    
    sort_column = getattr(Task, sort_by)
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    return query.offset(skip).limit(limit).all()

@router.get("/stats", response_model=dict)
def get_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get task statistics for the current user."""
    stats = {
        "total": db.query(Task).filter(Task.owner_id == current_user.id).count(),
        "todo": db.query(Task).filter(Task.owner_id == current_user.id, Task.status == "todo").count(),
        "in_progress": db.query(Task).filter(Task.owner_id == current_user.id, Task.status == "in_progress").count(),
        "done": db.query(Task).filter(Task.owner_id == current_user.id, Task.status == "done").count(),
    }
    stats["completion_rate"] = round((stats["done"] / stats["total"]) * 100, 1) if stats["total"] > 0 else 0
    return stats

@router.get("/{task_id}", response_model=TaskSchema)
def read_task(
    task_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=TaskSchema)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Mettre à jour seulement les champs fournis
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task = db.query(Task).filter(Task.id == task_id, Task.owner_id == current_user.id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


