import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from database import get_db, Base
from auth import get_password_hash

# Base de données en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    # Créer les tables pour chaque test
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Nettoyer après chaque test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_user():
    """Utilisateur de test"""
    return {
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def authenticated_client(client, test_user):
    """Client avec utilisateur connecté"""
    # Créer l'utilisateur
    response = client.post("/users/register", json=test_user)
    assert response.status_code == 200
    
    # Se connecter
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/users/token", data=login_data)
    token = response.json()["access_token"]
    
    # Retourner client avec headers d'auth
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
