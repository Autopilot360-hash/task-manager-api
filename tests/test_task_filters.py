def test_filter_by_status(authenticated_client):
    """Test filtering tasks by status"""
    # Créer des tâches avec différents statuts
    tasks_data = [
        {"title": "Todo Task", "status": "todo"},
        {"title": "In Progress Task", "status": "in_progress"}, 
        {"title": "Done Task", "status": "done"},
    ]
    
    for task_data in tasks_data:
        authenticated_client.post("/tasks/", json=task_data)
    
    # Tester le filtre todo
    response = authenticated_client.get("/tasks/?status=todo")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"

def test_search_tasks(authenticated_client):
    """Test searching tasks"""
    # Créer des tâches
    authenticated_client.post("/tasks/", json={"title": "Buy groceries", "description": "Milk and bread"})
    authenticated_client.post("/tasks/", json={"title": "Code review", "description": "FastAPI project"})
    
    # Rechercher par titre
    response = authenticated_client.get("/tasks/?search=groceries")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert "groceries" in tasks[0]["title"].lower()

def test_task_stats(authenticated_client):
    """Test task statistics endpoint"""
    # Créer des tâches
    authenticated_client.post("/tasks/", json={"title": "Task 1", "status": "todo"})
    authenticated_client.post("/tasks/", json={"title": "Task 2", "status": "done"})
    
    response = authenticated_client.get("/tasks/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total"] == 2
    assert stats["todo"] == 1
    assert stats["done"] == 1
    assert stats["completion_rate"] == 50.0
