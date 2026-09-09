with open("backend/app/api/routes.py", "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'from fastapi import APIRouter, WebSocket, WebSocketDisconnect\nfrom fastapi.responses import StreamingResponse\nfrom sqlalchemy import func, select\nfrom sqlalchemy.ext.asyncio import AsyncSession\n\nfrom app.api.ws import BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, manager',
    'from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect\nfrom fastapi.responses import StreamingResponse\nfrom sqlalchemy import func, select\nfrom sqlalchemy.ext.asyncio import AsyncSession\n\nfrom app.api.ws import manager'
)

with open("backend/app/api/routes.py", "w", encoding="utf-8") as f:
    f.write(code)
