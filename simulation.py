import json
import time
import urllib.request

URL = "http://127.0.0.1:8000/notifications"
PRODUCTEURS = [
    ("shop", "statut", "Commande {} expediee"),
    ("chat", "message", "Nouveau message n{}"),
    ("agenda", "evenement", "Reunion n{} a 14h"),
]

ok = 0
for i in range(1, 31):
    source, type_, modele = PRODUCTEURS[i % 3]
    corps = {"user": "user42", "type": type_, "msg": modele.format(i), "source": source}
    req = urllib.request.Request(
        URL,
        data=json.dumps(corps).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as rep:
            data = json.loads(rep.read())
            ok += 1
            print(f"{i:02d} OK  id={data['id']} abonnes={data['abonnes']}")
    except Exception as e:
        print(f"{i:02d} ERREUR : {e}")
    time.sleep(0.5)

print(f"Termine : {ok}/30 notifications envoyees")
