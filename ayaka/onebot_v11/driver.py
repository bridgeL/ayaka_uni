
"""[FastAPI](https://fastapi.tiangolo.com/) 驱动适配
"""

from functools import wraps
from typing import Optional

import uvicorn
from fastapi import FastAPI, status
from starlette.websockets import WebSocket, WebSocketState

from .model import Request, WebSocketServerSetup


def catch_closed(func):
    @wraps(func)
    async def decorator(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except:
            raise

    return decorator


class Driver:
    """FastAPI 驱动框架。"""

    def __init__(self):
        self._server_app = FastAPI()

    @property
    def type(self) -> str:
        """驱动名称: `fastapi`"""
        return "fastapi"

    @property
    def server_app(self) -> FastAPI:
        """`FastAPI APP` 对象"""
        return self._server_app

    def setup_websocket_server(self, setup: WebSocketServerSetup) -> None:
        async def _handle(websocket: WebSocket) -> None:
            await self._handle_ws(websocket, setup)

        self._server_app.add_api_websocket_route(
            setup.path.path,
            _handle,
            name=setup.name,
        )

    def run(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        *,
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
            app or self.server_app,  # type: ignore
            host=host,
            port=port,
            reload=True,
            log_config=LOGGING_CONFIG,
        )

    async def _handle_ws(self, websocket: WebSocket, setup: WebSocketServerSetup):
        request = Request(
            "GET",
            str(websocket.url),
            headers=websocket.headers.items(),
            cookies=websocket.cookies,
            version=websocket.scope.get("http_version", "1.1"),
        )
        ws = FastAPIWebSocket(
            request=request,
            websocket=websocket,
        )

        await setup.handle_func(ws)


class FastAPIWebSocket:
    """FastAPI WebSocket Wrapper"""

    def __init__(self, *, request: Request, websocket: WebSocket):
        self.request = request
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

    @catch_closed
    async def receive(self) -> str:
        return await self.websocket.receive_text()

    @catch_closed
    async def receive_bytes(self) -> bytes:
        return await self.websocket.receive_bytes()

    async def send(self, data: str) -> None:
        await self.websocket.send({"type": "websocket.send", "text": data})

    async def send_bytes(self, data: bytes) -> None:
        await self.websocket.send({"type": "websocket.send", "bytes": data})
