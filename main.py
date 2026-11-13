from fastapi import FastAPI
import redis

app = FastAPI(title="P24 Notifications")
r = redis.Redis(host="localhost", port=6379, decode_responses=True)

@app.get("/")
def accueil():
    return {"message": "P24 API"}

@app.get("/health")
def health():
    return {"redis": r.ping(), "service": "p24"}