import json
import logging
from typing import List

from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)


class Notifier:
    def __init__(self):
        self.connections: List[WebSocket] = []
        self.generator = self.get_notification_generator()

    async def get_notification_generator(self):
        while True:
            payload = yield
            await self._notify(payload)

    async def push(self, notification: dict):
        await self.generator.asend(notification)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def remove(self, websocket: WebSocket):
        self.connections.remove(websocket)

    async def _notify(self, notification: dict):
        living_connections = []
        while len(self.connections) > 0:
            # Looping like this is necessary in case a disconnection is handled
            # during await websocket.send_text()
            websocket = self.connections.pop()
            message = json.dumps(notification, indent=None)
            await websocket.send_text(message)
            living_connections.append(websocket)
        self.connections = living_connections


notifier = Notifier()
