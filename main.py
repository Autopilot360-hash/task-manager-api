import os
from fastapi import FastAPI
from database import engine, Base
from routers import users, tasks

# Créer les tables (Railway le fera automatiquement)
# Base.metadata.create_all(bind=engine)  # Supprimé - fait dans le Dockerfile

# Créer l'application FastAPI
app = FastAPI(
    title="Task Manager API",
    description="Une API simple pour gérer les tâches d'équipe - Déployée avec Railway 🚀",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Inclure les routers
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {
        "message": "🚀 Task Manager API déployée sur Railway !",
        "status": "healthy",
        "environment": os.getenv("ENVIRONMENT", "production"),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if engine else "disconnected"
    }