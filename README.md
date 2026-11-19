# P24 : Service de notifications instantanees

Service de notifications en temps reel : Redis (Pub/Sub + Streams) + FastAPI + WebSocket.

## Prerequis
- Python 3.10+
- Redis installe dans WSL (Ubuntu) ou sur Linux (sans Docker)

## Installation
```bash
sudo apt update && sudo apt install -y redis-server
sudo service redis-server start
redis-cli ping   # PONG
```
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Fichier `.env` (optionnel, non versionne) :
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS-PASSWORD=
## Lancement
```powershell
uvicorn main:app --reload
```
- Client web : http://127.0.0.1:8000/client
- Documentation Swagger : http://127.0.0.1:8000/docs

## Endpoints
| Methode | URL | Role |
|---|---|---|
| POST | /notifications | Publie (PUBLISH) et stocke (XADD) une notification |
| GET | /history/{user} | Historique recent (XREVRANGE) |
| WS | /ws/{user} | Reception en temps reel (SUBSCRIBE) |
| GET | /health | Etat de Redis |

## Modele de cles Redis
| Cle | Type | Role |
|---|---|---|
| notifications:<user> | Canal Pub/Sub | Diffusion instantanee |
| history:<user> | Stream (MAXLEN ~ 50) | Historique recent |

## Simulation (3 producteurs, 30 notifications)
Ouvrir 3 onglets de /client (user42), puis :
```powershell
python simulation.py
```
