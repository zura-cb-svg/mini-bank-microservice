from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app, get_db
from database import Base

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_account():
    response = client.post("/accounts/", json={"owner_name": "Zura", "balance": 500})
    
    assert response.status_code == 200
    assert response.json()["owner_name"] == "Zura"
    assert response.json()["balance"] == 500

def test_transfer_not_enough_money():
    client.post("/accounts/", json={"owner_name": "Hacker", "balance": 100})
    client.post("/accounts/", json={"owner_name": "Victim", "balance": 50})
    
    response = client.post(
        "/transfer/",
        json={"from_account_id": 1, "to_account_id": 2, "amount": 10000},
    )
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Not enough money"