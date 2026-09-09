import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger("codesupply.ws")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, scan_id: str):
        await websocket.accept()
        if scan_id not in self.active_connections:
            self.active_connections[scan_id] = []
        self.active_connections[scan_id].append(websocket)
        logger.info(f"WebSocket connected for scan {scan_id}. Total clients: {len(self.active_connections[scan_id])}")

    def disconnect(self, websocket: WebSocket, scan_id: str):
        if scan_id in self.active_connections:
            if websocket in self.active_connections[scan_id]:
                self.active_connections[scan_id].remove(websocket)
            if not self.active_connections[scan_id]:
                del self.active_connections[scan_id]
        logger.info(f"WebSocket disconnected for scan {scan_id}")

    async def broadcast_scan_update(self, scan_id: str, scan_data: dict):
        if scan_id in self.active_connections:
            connections = self.active_connections[scan_id]
            stale_connections = []
            for connection in connections:
                try:
                    await connection.send_json(scan_data)
                except Exception as e:
                    logger.warning(f"Failed to send to websocket: {e}")
                    stale_connections.append(connection)
            
            for stale in stale_connections:
                self.disconnect(stale, scan_id)

manager = ConnectionManager()
