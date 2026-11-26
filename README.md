# P24 : Service de notifications instantanees

Service de notifications en temps reel : Redis (Pub/Sub + Streams) + FastAPI + WebSocket.

## Prerequis
- Python 3.10+
- Redis installe sur Ubuntu / Linux (sans Docker)

## Installation
```bash
sudo apt update && sudo apt install -y redis-server
sudo service redis-server start
redis-cli ping   # PONG
```
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Fichier `.env` (optionnel, non versionne) :
```env
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_PASSWORD=
```

## Lancement
```bash
uvicorn main:app --reload
```
- Client web : http://127.0.0.1:8000/client
- Documentation Swagger : http://127.0.0.1:8000/docs

## Endpoints
| Methode | URL | Role |
|---|---|---|
| POST | /notifications | Publie (PUBLISH) et stocke (XADD) une notification |
| GET | /history/{user} | Historique recent (XREVRANGE) |
| GET | /history/{user}/stats | Statistiques du Stream (XLEN) |
| WS | /ws/{user} | Reception en temps reel (SUBSCRIBE) |
| GET | /health | Etat de Redis |
| GET | /client | Page client WebSocket |

## Modele de cles Redis
| Cle | Type | Role |
|---|---|---|
| notifications:<user> | Canal Pub/Sub | Diffusion instantanee |
| history:<user> | Stream (MAXLEN ~ 50) | Historique recent |

## Tests automatises
```bash
python -m pytest -v
```

## Simulation (3 producteurs, 30 notifications)
Ouvrir Un ou plusieurs onglets de /client (ex. user42), puis :
```bash
python simulation.py
```
