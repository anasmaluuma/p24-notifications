from unittest.mock import patch

from fastapi.testclient import TestClient
from redis.exceptions import RedisError

from main import app, r

client = TestClient(app)

NOTIF = {"user": "user42", "type": "message", "msg": "Test", "source": "pytest"}


def test_accueil():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "P24 API"}


def test_health_redis_ok():
    with patch.object(r, "ping", return_value=True):
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"redis": True, "service": "p24"}


def test_notification_valide():
    with patch.object(r, "publish", return_value=1), \
         patch.object(r, "xadd", return_value="123-0"):
        response = client.post("/notifications", json=NOTIF)
    assert response.status_code == 201
    assert response.json() == {"id": "123-0", "abonnes": 1}


def test_notification_type_invalide():
    response = client.post("/notifications", json={**NOTIF, "type": "invalid"})
    assert response.status_code == 422


def test_notification_message_vide():
    response = client.post("/notifications", json={**NOTIF, "msg": ""})
    assert response.status_code == 422


def test_redis_indisponible():
    with patch.object(r, "publish", side_effect=RedisError):
        response = client.post("/notifications", json=NOTIF)
    assert response.status_code == 503
    assert response.json()["detail"] == "Redis indisponible"


def test_historique_ok():
    fake = [("123-0", {"type": "message", "msg": "Bonjour", "source": "pytest"})]
    with patch.object(r, "xrevrange", return_value=fake):
        response = client.get("/history/user42")
    assert response.status_code == 200
    assert response.json()[0]["msg"] == "Bonjour"


def test_historique_user_invalide():
    response = client.get("/history/user@42")
    assert response.status_code == 400
    assert response.json()["detail"] == "Identifiant utilisateur invalide"


def test_stats_ok():
    with patch.object(r, "xlen", return_value=5):
        response = client.get("/history/user42/stats")
    assert response.status_code == 200
    assert response.json()["xlen"] == 5
    assert response.json()["user"] == "user42"


def test_client_page():
    response = client.get("/client")
    assert response.status_code == 200
