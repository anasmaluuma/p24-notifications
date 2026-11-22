import re
import asyncio
import json
import os
from typing import Literal

import redis
import redis.asyncio as aredis
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

load_dotenv()

CONFIG = dict(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True,
)
USER_PATTERN = re.compile(r"^[a-zA-Z0-9_-]{1,40}$")
app = FastAPI(title="P24 Notifications")
r = redis.Redis(**CONFIG, socket_connect_timeout=2)
ar = aredis.Redis(**CONFIG)


class Notification(BaseModel):
    user: str = Field(min_length=1, max_length=40, pattern=r"^[a-zA-Z0-9_-]{1,40}$")
    type: Literal["message", "evenement", "statut"]
    msg: str = Field(min_length=1, max_length=200)
    source: str = "app"

def verifier_user(user: str) -> str:
    if not USER_PATTERN.match(user):
        raise HTTPException(status_code=400, detail="Identifiant utilisateur invalide")
    return user


@app.get("/")
def accueil():
    return {"message": "P24 API"}


@app.get("/health")
def health():
    try:
        return {"redis": bool(r.ping()), "service": "p24"}
    except RedisError:
        return {"redis": False, "service": "p24"}


@app.post("/notifications", status_code=201)
def publier(n: Notification):
    champs = {"type": n.type, "msg": n.msg, "source": n.source}
    try:
        abonnes = r.publish(f"notifications:{n.user}", json.dumps(champs))
        id_stream = r.xadd(f"history:{n.user}", champs, maxlen=50, approximate=True)
    except RedisError:
        raise HTTPException(status_code=503, detail="Redis indisponible")
    return {"id": id_stream, "abonnes": abonnes}


@app.get("/history/{user}")
def historique(user: str, count: int = 10):
    user = verifier_user(user)
    try:
        entrees = r.xrevrange(f"history:{user}", count=min(max(count, 1), 50))
    except RedisError:
        raise HTTPException(status_code=503, detail="Redis indisponible")
    return [{"id": i, **champs} for i, champs in entrees]

@app.get("/history/{user}/stats")
def stats_historique(user: str):
    user = verifier_user(user)
    try:
        longueur = r.xlen(f"history:{user}")  # [AJOUT] Opération NoSQL XLEN
    except RedisError:
        raise HTTPException(status_code=503, detail="Redis indisponible")
    return {"user": user, "stream_key": f"history:{user}", "xlen": longueur}

@app.websocket("/ws/{user}")
async def ws_notifications(ws: WebSocket, user: str):
    if not USER_PATTERN.match(user):
        await ws.close(code=1008)
        return

    await ws.accept()
    pubsub = ar.pubsub()
    await pubsub.subscribe(f"notifications:{user}")

    async def envoyer():
        async for m in pubsub.listen():
            if m["type"] == "message":
                await ws.send_text(m["data"])

    tache = asyncio.create_task(envoyer())
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        tache.cancel()
        try:
            await tache
        except asyncio.CancelledError:
            pass
        await pubsub.unsubscribe(f"notifications:{user}")
        await pubsub.aclose()


@app.get("/client")
def client():
    return FileResponse(os.path.join(os.path.dirname(__file__), "client.html"))
