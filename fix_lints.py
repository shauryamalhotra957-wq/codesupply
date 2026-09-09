import re

# Fix app/api/routes.py imports
with open("backend/app/api/routes.py", "r", encoding="utf-8") as f:
    routes_code = f.read()

# Remove the trailing imports we appended earlier
routes_code = re.sub(r'from fastapi import WebSocket, WebSocketDisconnect\n\nfrom app\.api\.ws import manager\n*', '', routes_code)
# Add them to the top
routes_code = routes_code.replace('from fastapi import FastAPI, HTTPException', 'from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect\nfrom app.api.ws import manager\n')

with open("backend/app/api/routes.py", "w", encoding="utf-8") as f:
    f.write(routes_code)


# Fix app/workers/runner.py imports
with open("backend/app/workers/runner.py", "r", encoding="utf-8") as f:
    runner_code = f.read()

# Make sure we add the missing imports
if 'from app.api.ws import manager' not in runner_code:
    runner_code = runner_code.replace('from app.models.models import', 'from app.api.ws import manager\nfrom app.api.routes import _scan_to_response, _get_stages\nfrom app.models.models import')

with open("backend/app/workers/runner.py", "w", encoding="utf-8") as f:
    f.write(runner_code)
