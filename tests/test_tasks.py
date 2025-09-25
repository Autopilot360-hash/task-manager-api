import pytest

def test_create_task(authenticated_client):
    """Test création d'une tâche"""
    task_data = {
        "title": "Ma première tâche",
        "description": "Description de test",
        "status": "todo"
    }
    
    response = authenticated_client.post("/tasks/", json=task_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == task_data["title"]
    assert data["description"] == task_data["description"]
    assert data["status"] == task_data["status"]
    assert "id" in data
    assert "created_at" in data
    assert "owner_id" in data

def test_create_task_without_auth(client):
    """Test création tâche sans authentification"""
    task_data = {
        "title": "Tâche non autorisée",
        "description": "Ne devrait pas marcher"
    }
    
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == 401

def test_get_tasks_empty(authenticated_client):
    """Test récupération tâches vides"""
    response = authenticated_client.get("/tasks/")
    
    assert response.status_code == 200
    assert response.json() == []

def test_get_tasks_with_data(authenticated_client):
    """Test récupération avec des tâches"""
    # Créer quelques tâches
    tasks_data = [
        {"title": "Tâche 1", "description": "Desc 1"},
        {"title": "Tâche 2", "description": "Desc 2", "status": "in_progress"},
        {"title": "Tâche 3", "description": "Desc 3", "status": "done"}
    ]
    
    created_tasks = []
    for task_data in tasks_data:
        response = authenticated_client.post("/tasks/", json=task_data)
        created_tasks.append(response.json())
    
    # Récupérer toutes les tâches
    response = authenticated_client.get("/tasks/")
    
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 3
    
    # Vérifier que toutes nos tâches sont là
    titles = [task["title"] for task in tasks]
    assert "Tâche 1" in titles
    assert "Tâche 2" in titles
    assert "Tâche 3" in titles

def test_get_single_task(authenticated_client):
    """Test récupération d'une tâche spécifique"""
    # Créer une tâche
    task_data = {"title": "Tâche unique", "description": "Test single"}
    response = authenticated_client.post("/tasks/", json=task_data)
    created_task = response.json()
    
    # Récupérer cette tâche
    response = authenticated_client.get(f"/tasks/{created_task['id']}")
    
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == created_task["id"]
    assert task["title"] == task_data["title"]

def test_get_nonexistent_task(authenticated_client):
    """Test récupération tâche inexistante"""
    response = authenticated_client.get("/tasks/999")
    
    assert response.status_code == 404
    assert "Task not found" in response.json()["detail"]

def test_update_task(authenticated_client):
    """Test mise à jour d'une tâche"""
    # Créer une tâche
    task_data = {"title": "Tâche originale", "status": "todo"}
    response = authenticated_client.post("/tasks/", json=task_data)
    created_task = response.json()
    
    # Mettre à jour
    update_data = {
        "title": "Tâche modifiée",
        "status": "in_progress",
        "description": "Nouvelle description"
    }
    response = authenticated_client.put(
        f"/tasks/{created_task['id']}", 
        json=update_data
    )
    
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["title"] == update_data["title"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["description"] == update_data["description"]
    assert updated_task["id"] == created_task["id"]  # ID inchangé

def test_partial_update_task(authenticated_client):
    """Test mise à jour partielle"""
    # Créer une tâche
    task_data = {
        "title": "Tâche complète", 
        "description": "Description originale",
        "status": "todo"
    }
    response = authenticated_client.post("/tasks/", json=task_data)
    created_task = response.json()
    
    # Mettre à jour seulement le statut
    update_data = {"status": "done"}
    response = authenticated_client.put(
        f"/tasks/{created_task['id']}", 
        json=update_data
    )
    
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == "done"
    # Les autres champs restent inchangés
    assert updated_task["title"] == task_data["title"]
    assert updated_task["description"] == task_data["description"]

def test_delete_task(authenticated_client):
    """Test suppression d'une tâche"""
    # Créer une tâche
    task_data = {"title": "Tâche à supprimer"}
    response = authenticated_client.post("/tasks/", json=task_data)
    created_task = response.json()
    
    # Supprimer
    response = authenticated_client.delete(f"/tasks/{created_task['id']}")
    
    assert response.status_code == 200
    assert "Task deleted successfully" in response.json()["message"]
    
    # Vérifier qu'elle n'existe plus
    response = authenticated_client.get(f"/tasks/{created_task['id']}")
    assert response.status_code == 404

def test_user_isolation(client, test_user):
    """Test que les utilisateurs ne voient que leurs tâches"""
    # Créer deux utilisateurs
    user1_data = {"email": "user1@test.com", "password": "pass123"}
    user2_data = {"email": "user2@test.com", "password": "pass123"}
    
    client.post("/users/register", json=user1_data)
    client.post("/users/register", json=user2_data)
    
    # Connecter user1
    response = client.post("/users/token", data={
        "username": user1_data["email"], 
        "password": user1_data["password"]
    })
    user1_token = response.json()["access_token"]
    
    # Connecter user2
    response = client.post("/users/token", data={
        "username": user2_data["email"], 
        "password": user2_data["password"]
    })
    user2_token = response.json()["access_token"]
    
    # User1 crée une tâche
    client.headers.update({"Authorization": f"Bearer {user1_token}"})
    response = client.post("/tasks/", json={"title": "Tâche de User1"})
    user1_task = response.json()
    
    # User2 ne doit pas voir la tâche de User1
    client.headers.update({"Authorization": f"Bearer {user2_token}"})
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert len(response.json()) == 0
    
    # User2 ne peut pas accéder à la tâche de User1
    response = client.get(f"/tasks/{user1_task['id']}")
    assert response.status_code == 404
