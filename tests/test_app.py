import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    rv = client.get('/')
    assert rv.status_code == 200
    assert b"Welcome to the Todo API" in rv.data

def test_create_and_get_task(client):
    rv = client.post('/tasks', json={'title': 'Test task', 'description': 'Details'})
    assert rv.status_code == 201
    task_id = rv.json['id']
    
    rv = client.get(f'/tasks/{task_id}')
    assert rv.status_code == 200
    assert rv.json['title'] == 'Test task'

def test_update_task(client):
    rv = client.post('/tasks', json={'title': 'Old'})
    task_id = rv.json['id']
    rv = client.put(f'/tasks/{task_id}', json={'completed': True})
    assert rv.status_code == 200
    assert rv.json['completed'] is True

def test_delete_task(client):
    rv = client.post('/tasks', json={'title': 'To delete'})
    task_id = rv.json['id']
    rv = client.delete(f'/tasks/{task_id}')
    assert rv.status_code == 200
    rv = client.get(f'/tasks/{task_id}')
    assert rv.status_code == 404

def test_ping_secure(client):
    rv = client.get('/ping?target=127.0.0.1')
    assert rv.status_code == 200
    assert 'PING' in rv.json['result']  # ping output snippet (Windows) or 'PING' (Linux) - Updated for Linux CI


def test_health(client):
    rv = client.get('/health')
    assert rv.status_code == 200
    assert rv.json['status'] == 'healthy'

def test_ping_invalid_target(client):
    rv = client.get('/ping?target=;evilcommand')
    assert rv.status_code == 400
    assert 'Invalid target format' in rv.json['error']