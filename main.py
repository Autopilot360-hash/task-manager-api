from fastapi import FastAPI
from database import engine, Base
from routers import users, tasks

# Créer les tables
Base.metadata.create_all(bind=engine)

# Créer l'application FastAPI
app = FastAPI(
    title="Task Manager API",
    description="Une API simple pour gérer les tâches d'équipe",
    version="1.0.0"
)

# Inclure les routers
app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
def read_root():
    return {
        "message": "Bienvenue sur l'API Task Manager !",
        "docs": "/docs",
        "redoc": "/redoc"
    }
