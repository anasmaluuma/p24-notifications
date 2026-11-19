import json
import os
from typing import Literal

import redis
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from redis.exceptions import RedisError

load_dotenv()

app = FastAPI(title="P24 Notifications")
r = redis.Redis(
    host=os.getenv("REDIS_HOST", "127.0.0.1"),
    port=int(os.getenv("REDIS_PORT", "6379")),
    password=os.getenv("REDIS_PASSWORD") or None,
    decode_responses=True,
    socket_connect_timeout=2,
)


class Notification(BaseModel):
    user: str = Field(min_length=1)
    type: Literal["message", "evenement", "statut"]
    msg: str = Field(min_length=1, max_length=200)
    source: str = "app"


@app.get("/")
def accueil():
    return {"message": "P24 API"}


@app.get("/health")
def health():
    try:
        return {"redis": r.ping(), "service": "p24"}
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
