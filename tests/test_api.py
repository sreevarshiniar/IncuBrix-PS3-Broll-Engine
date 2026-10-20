from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health_and_ready():
    assert client.get('/health').status_code==200
    assert 'ready' in client.get('/ready').json()

def test_missing_input_is_rejected():
    r=client.post('/api/v1/broll/jobs',json={})
    assert r.status_code==422

def test_job_creation_and_idempotency(monkeypatch):
    import app.main as main
    monkeypatch.setattr(main.executor,'submit',lambda *args,**kwargs: None)
    payload={"script":"Saving money starts with a plan.","aspect_ratios":["16:9"]}
    a=client.post('/api/v1/broll/jobs',json=payload,headers={'Idempotency-Key':'test-key-1'})
    b=client.post('/api/v1/broll/jobs',json=payload,headers={'Idempotency-Key':'test-key-1'})
    assert a.status_code==202 and b.status_code==202
    assert a.json()['job_id']==b.json()['job_id']
