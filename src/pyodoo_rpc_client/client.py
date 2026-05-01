from __future__ import annotations

import xmlrpc.client
from typing import Any, Dict, Optional

from .exceptions import OdooRpcConfigError, OdooRpcError


class OdooRpcClient:
    def __init__(
        self,
        url: str,
        db: str,
        username: str,
        password: Optional[str] = None,
        key: Optional[str] = None,
        debug: bool = False,
        allow_none: bool = True,
    ):
        if not url:
            raise OdooRpcConfigError("url is required")
        if not db:
            raise OdooRpcConfigError("db is required")
        if not username:
            raise OdooRpcConfigError("username is required")

        self.url = str(url).rstrip("/")
        self.db = db
        self.username = username
        self.password = key or password
        self.debug = bool(debug)
        self.allow_none = allow_none

        self.uid = None
        self.logged_in = False
        self.error = None

        self.common = None
        self.models = None

        self._connect()

    def _connect(self):
        if not self.password:
            self.error = OdooRpcConfigError("password/key is required")
            self.logged_in = False
            return
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=self.allow_none)
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})
            self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=self.allow_none)
            self.logged_in = bool(self.uid)
            self.error = None
        except Exception as exc:
            raise exc
            self.error = OdooRpcError("Failed to initialize RPC client", cause=exc)
            self.logged_in = False
            if self.debug:
                raise self.error

    def set_debug(self, debug: bool):
        self.debug = bool(debug)
        return self

    def model(self, model_name: str):
        from .model import OdooRpcModel

        return OdooRpcModel(client=self, model_name=model_name)

    def execute_kw(
        self,
        model_name: str,
        method: str,
        args: Optional[list] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        debug: Optional[bool] = None,
        default: Any = None,
    ):
        if not self.logged_in or self.uid is None:
            exc = OdooRpcError("Client is not authenticated")
            self.error = exc
            if self.debug if debug is None else bool(debug):
                raise exc
            return default

        try:
            result = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                model_name,
                method,
                args or [],
                kwargs or {},
            )
            self.error = None
            return result
        except Exception as exc:
            raise exc
            wrapped = OdooRpcError(f"RPC call failed for {model_name}.{method}", cause=exc)
            self.error = wrapped
            should_raise = self.debug if debug is None else bool(debug)
            if should_raise:
                raise wrapped
            return default
