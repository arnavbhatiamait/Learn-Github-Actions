import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """Test the home endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to Task Manager API" in response.data

def test_get_tasks(client):
    """Test retrieving all tasks"""
    response = client.get("/tasks")
    assert response.status_code == 200
    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) >= 1

def test_add_task(client):
    """Test adding a new task"""
    new_task = {"title": "Write Unit Tests"}
    response = client.post("/tasks", json=new_task)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["title"] == "Write Unit Tests"
    assert not json_data["done"]

def test_add_task_without_title(client):
    """Test adding a task without a title"""
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    json_data = response.get_json()
    assert "error" in json_data