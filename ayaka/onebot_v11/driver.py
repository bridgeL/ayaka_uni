
"""[FastAPI](https://fastapi.tiangolo.com/) 驱动适配
"""

import uvicorn
from typing import Optional
from fastapi import FastAPI, status
from starlette.websockets import WebSocket, WebSocketState

class Driver:
    """FastAPI 驱动框架。"""

    def __init__(self):
        self._server_app = FastAPI()
        self.websocket:Optional[WebSocket] = None

    @property
    def server_app(self) -> FastAPI:
        """`FastAPI APP` 对象"""
        return self._server_app

    def setup(self, name, path, handle):
        async def _handle(websocket: WebSocket) -> None:
            await handle(FastAPIWebSocket(websocket))

        self._server_app.add_api_websocket_route(path, _handle, name)

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        app: Optional[str] = None
    ):
        """使用 `uvicorn` 启动 FastAPI"""
        LOGGING_CONFIG = {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {
                "default": {
                    "class": "ayaka.logger.UvicornLogger",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default"],
                    "level": "INFO"
                },
            },
        }

        uvicorn.run(
            # 当reload为true时，必须使用__main__:app类型的字符串，不能直接传递asgi对象
            app=app,  # type: ignore
            host=host,
            port=port,
            reload=True,
            log_config=LOGGING_CONFIG,
        )

class FastAPIWebSocket:
    """FastAPI WebSocket Wrapper"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    @property
    def closed(self) -> bool:
        return (
            self.websocket.client_state == WebSocketState.DISCONNECTED
            or self.websocket.application_state == WebSocketState.DISCONNECTED
        )

    async def accept(self) -> None:
        await self.websocket.accept()

    async def close(
        self, code: int = status.WS_1000_NORMAL_CLOSURE, reason: str = ""
    ) -> None:
        await self.websocket.close(code)

    async def receive(self) -> str:
        return await self.websocket.receive_text()

    async def receive_bytes(self) -> bytes:
        return await self.websocket.receive_bytes()

    async def send(self, data: str) -> None:
        await self.websocket.send({"type": "websocket.send", "text": data})

    async def send_bytes(self, data: bytes) -> None:
        await self.websocket.send({"type": "websocket.send", "bytes": data})
