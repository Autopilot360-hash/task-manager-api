import pytest

def test_create_user(client, test_user):
    """Test création d'utilisateur"""
    response = client.post("/users/register", json=test_user)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "id" in data
    assert data["is_active"] is True
    # Le mot de passe ne doit pas être retourné
    assert "password" not in data

def test_create_duplicate_user(client, test_user):
    """Test création utilisateur avec email existant"""
    # Créer le premier utilisateur
    client.post("/users/register", json=test_user)
    
    # Essayer de créer le même utilisateur
    response = client.post("/users/register", json=test_user)
    
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test connexion réussie"""
    # Créer l'utilisateur
    client.post("/users/register", json=test_user)
    
    # Se connecter
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/users/token", data=login_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test connexion avec mauvais mot de passe"""
    # Créer l'utilisateur
    client.post("/users/register", json=test_user)
    
    # Se connecter avec mauvais mot de passe
    login_data = {
        "username": test_user["email"],
        "password": "wrongpassword"
    }
    response = client.post("/users/token", data=login_data)
    
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """Test connexion utilisateur inexistant"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "password"
    }
    response = client.post("/users/token", data=login_data)
    
    assert response.status_code == 401
