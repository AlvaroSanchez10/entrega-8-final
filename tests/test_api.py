import asyncio
import json
import os
from uuid import UUID

os.environ.setdefault('OPENAI_API_KEY', 'sk-test-placeholder')

from fastapi.testclient import TestClient
from app import api


class FakeRedis:
    def __init__(self):
        self.data = {}

    async def get(self, key):
        return self.data.get(key)

    async def set(self, key, value):
        self.data[key] = value


def prepare(monkeypatch):
    redis = FakeRedis()
    monkeypatch.setattr(api.app.state, 'redis', redis, raising=False)
    return redis, TestClient(api.app)


def test_tarea_inexistente_devuelve_404(monkeypatch):
    _, client = prepare(monkeypatch)
    response = client.get('/tasks/no-existe')
    assert response.status_code == 404


def test_crear_tarea_pending(monkeypatch):
    redis, client = prepare(monkeypatch)
    launched = []
    def fake_launch(coroutine):
        launched.append(coroutine)
        coroutine.close()
    monkeypatch.setattr(api, 'launch_background_task', fake_launch)
    response = client.post('/tasks', json={'prompt': 'Consultar Redis'})
    assert response.status_code == 200
    data = response.json()
    UUID(data['job_id'])
    assert data['status'] == 'PENDING'
    assert len(launched) == 1
    assert json.loads(redis.data[f"task:{data['job_id']}"])['status'] == 'PENDING'


def test_rechaza_prompt_vacio(monkeypatch):
    _, client = prepare(monkeypatch)
    assert client.post('/tasks', json={'prompt': ''}).status_code == 422


def test_no_aprueba_pending(monkeypatch):
    redis, client = prepare(monkeypatch)
    redis.data['task:abc'] = json.dumps({'status': 'PENDING'})
    response = client.post('/tasks/abc/approve', json={'approved': True})
    assert response.status_code == 409


def test_aprobacion_valida(monkeypatch):
    redis, client = prepare(monkeypatch)
    redis.data['task:abc'] = json.dumps({'status': 'WAITING_APPROVAL'})
    class FakeGraph:
        async def aget_state(self, config):
            assert config['configurable']['thread_id'] == 'abc'
            return type('Snapshot', (), {'next': ('human_review',)})()
    monkeypatch.setattr(api.app.state, 'graph', FakeGraph(), raising=False)
    launched = []
    def fake_launch(coroutine):
        launched.append(coroutine)
        coroutine.close()
    monkeypatch.setattr(api, 'launch_background_task', fake_launch)
    response = client.post('/tasks/abc/approve', json={'approved': True})
    assert response.status_code == 200
    assert response.json()['approved'] is True
    assert json.loads(redis.data['task:abc'])['status'] == 'RUNNING'
    assert len(launched) == 1


def test_rechazo_guarda_rejected(monkeypatch):
    redis, _ = prepare(monkeypatch)
    class FakeGraph:
        async def ainvoke(self, graph_input, config):
            return {'review_decision': 'rejected', 'messages': []}
        async def aget_state(self, config):
            return type('Snapshot', (), {'next': ()})()
    monkeypatch.setattr(api.app.state, 'graph', FakeGraph(), raising=False)
    asyncio.run(api.execute_task('rechazado', {'messages': []}))
    assert json.loads(redis.data['task:rechazado'])['status'] == 'REJECTED'


def test_validacion_fallida_no_completa(monkeypatch):
    redis, _ = prepare(monkeypatch)
    class FakeGraph:
        async def ainvoke(self, graph_input, config):
            return {'validation_passed': False, 'messages': []}
        async def aget_state(self, config):
            return type('Snapshot', (), {'next': ()})()
    monkeypatch.setattr(api.app.state, 'graph', FakeGraph(), raising=False)
    asyncio.run(api.execute_task('invalidado', {'messages': []}))
    assert json.loads(redis.data['task:invalidado'])['status'] == 'FAILED'


def test_aprobacion_guarda_completed(monkeypatch):
    redis, _ = prepare(monkeypatch)
    class FakeGraph:
        async def ainvoke(self, graph_input, config):
            return {'review_decision': 'approved', 'validation_passed': True,
                    'messages': [type('Message', (), {'content': 'OK'})()]}
        async def aget_state(self, config):
            return type('Snapshot', (), {'next': ()})()
    monkeypatch.setattr(api.app.state, 'graph', FakeGraph(), raising=False)
    asyncio.run(api.execute_task('aprobado', {'messages': []}))
    state = json.loads(redis.data['task:aprobado'])
    assert state['status'] == 'COMPLETED' and state['result'] == 'OK'
