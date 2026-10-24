from starlette.datastructures import (
    Headers,
    MutableHeaders,
)
from starlette.types import (
    ASGIApp,
    Receive,
    Scope,
    Send,
)

DEFAULT_PORTS = {("http", "80"), ("https", "443")}


def _last(value: str | None) -> str | None:
    return value.split(",")[-1].strip() or None if value else None


class ProxyFixMiddleware:
    """ASGI counterpart of werkzeug's ProxyFix: trusts X-Forwarded-{For,Proto,Host,Port,Prefix} from one proxy."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            scope = dict(scope)
            headers = Headers(scope=scope)
            if client := _last(headers.get("x-forwarded-for")):
                scope["client"] = (client, 0)
            if proto := _last(headers.get("x-forwarded-proto")):
                scope["scheme"] = proto
            fwd_host = _last(headers.get("x-forwarded-host"))
            fwd_port = _last(headers.get("x-forwarded-port"))
            if fwd_host or fwd_port:
                scope["headers"] = list(scope["headers"])
                mutable_headers = MutableHeaders(scope=scope)
                host = fwd_host or mutable_headers.get("host", "")
                if fwd_port:
                    host = host.split(":", 1)[0]
                    if (scope["scheme"], fwd_port) not in DEFAULT_PORTS:
                        host = f"{host}:{fwd_port}"
                mutable_headers["host"] = host
            if prefix := _last(headers.get("x-forwarded-prefix")):
                prefix = prefix.rstrip("/")
                scope["root_path"] = prefix
                scope["path"] = prefix + scope["path"]
        await self.app(scope, receive, send)
