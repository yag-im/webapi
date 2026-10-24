import logging
import typing as t

from fastapi import (
    FastAPI,
    Request,
)
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

ERROR_YAG_OP = (1409, "webapi operational error")
ERROR_ACCOUNTSVC = (1408, "accountsvc error")
ERROR_APPSVC = (1409, "appsvc error")
ERROR_JUKEBOXSVC = (1410, "jukeboxsvc error")
ERROR_UNKNOWN = (1500, "unknown error")

log = logging.getLogger("webapi")


class BizException(Exception):
    def __init__(self, code: t.Optional[int] = None, message: t.Optional[t.Any] = None) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


class YagOpException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_YAG_OP[0]
        message = message or ERROR_YAG_OP[1]
        super().__init__(code, message)


class AccountSvcException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_ACCOUNTSVC[0]
        message = message or ERROR_ACCOUNTSVC[1]
        super().__init__(code, message)


class AppSvcException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_APPSVC[0]
        message = message or ERROR_APPSVC[1]
        super().__init__(code, message)


class JukeboxSvcException(BizException):
    def __init__(self, message: t.Optional[t.Any] = None) -> None:
        code = ERROR_JUKEBOXSVC[0]
        message = message or ERROR_JUKEBOXSVC[1]
        super().__init__(code, message)


def init_app(app: FastAPI) -> None:
    """Inits error handlers. HTTPExceptions keep FastAPI's default handling."""

    @app.exception_handler(Exception)
    async def handle_exception(request: Request, e: Exception) -> JSONResponse:
        log.exception(e)
        return JSONResponse({"code": ERROR_UNKNOWN[0], "message": ERROR_UNKNOWN[1]}, status_code=500)

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def handle_validation_error(request: Request, e: RequestValidationError | ValidationError) -> JSONResponse:
        errors = e.errors() if isinstance(e, RequestValidationError) else e.errors(include_context=False)
        res = {"code": 1400, "message": jsonable_encoder(errors)}
        log.error(res)
        return JSONResponse(res, status_code=400)

    @app.exception_handler(BizException)
    async def handle_biz_exception(request: Request, e: BizException) -> JSONResponse:
        res = {"code": e.code, "message": jsonable_encoder(e.message)}
        log.error(res)
        return JSONResponse(res, status_code=409)
