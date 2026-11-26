# Declaration d'utilisation de l'IA (P24)

## Journal des utilisations

| Date | Outil IA | Objectif du prompt | Validation et modifications |
|---|---|---|---|
| 2026-11-10 | Claude | Structure initiale de l'API FastAPI + WebSocket + Redis Pub/Sub et Streams | Code relu, adapte, execute et teste sur redis-cli et pytest |
| 2026-11-19 | Gemini | Validation du user (regex), endpoint /history/{user}/stats (XLEN), nettoyage WebSocket | Relu, teste, explique |

## Ce qui a ete verifie manuellement
- Commandes Redis executees directement dans redis-cli (PING, PUBLISH, SUBSCRIBE, PSUBSCRIBE, XADD, XREVRANGE, XRANGE, XLEN).
- Securite des secrets verifiee : aucun mot de passe code en dur (variables d'environnement via .env).
- Validation des entrees et isolation des utilisateurs (user42 vs user4) verifiees sur /client et via les 10 tests pytest.
