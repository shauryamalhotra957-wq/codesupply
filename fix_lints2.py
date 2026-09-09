import re

with open("backend/app/api/routes.py", "r", encoding="utf-8") as f:
    routes_code = f.read()

if 'from fastapi import WebSocket, WebSocketDisconnect' not in routes_code:
    routes_code = routes_code.replace('from fastapi import APIRouter', 'from fastapi import APIRouter, WebSocket, WebSocketDisconnect\nfrom app.api.ws import manager')

with open("backend/app/api/routes.py", "w", encoding="utf-8") as f:
    f.write(routes_code)
