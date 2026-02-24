from __future__ import annotations

import copy
from typing import Any, Dict, Optional
from typing import TYPE_CHECKING

from .entity import OdooRpcEntity

if TYPE_CHECKING:
    from .client import OdooRpcClient


class OdooRpcModel:
    def __init__(
        self,
        client: "OdooRpcClient",
        model_name: str,
        context: Optional[Dict[str, Any]] = None,
        debug: Optional[bool] = None,
    ):
        self.client = client
        self.model = model_name
        self.context = copy.deepcopy(context or {})
        self.error = None
        self._fields = None
        self._debug = client.debug if debug is None else bool(debug)

    def set_debug(self, debug: bool):
        self._debug = bool(debug)
        return self

    def with_context(self, context: Optional[Dict[str, Any]] = None):
        merged = copy.deepcopy(self.context)
        if context:
            merged.update(copy.deepcopy(context))
        return self.__class__(
            client=self.client,
            model_name=self.model,
            context=merged,
            debug=self._debug,
        )

    def fields(self):
        if self._fields is None:
            data = self.fields_get([], {"attributes": ["string", "help", "type", "required", "relation"]})
            self._fields = data if isinstance(data, dict) else {}
        return self._fields

    @staticmethod
    def _normalize_ids(ids: Any):
        if ids is None:
            return []
        if isinstance(ids, (int, str)):
            return [int(ids)]
        if isinstance(ids, tuple):
            ids = list(ids)
        if isinstance(ids, list):
            if len(ids) == 1 and isinstance(ids[0], list):
                ids = ids[0]
            parsed = []
            for item in ids:
                try:
                    parsed.append(int(item))
                except Exception:
                    continue
            return parsed
        return ids

    @staticmethod
    def _normalize_domain(domain: Any):
        if isinstance(domain, list) and len(domain) == 1 and isinstance(domain[0], list):
            return domain[0]
        return domain

    @staticmethod
    def _default_method_return(method: str):
        method = method.lower()
        if method in {"search", "search_read", "read"}:
            return []
        if method in {"fields_get"}:
            return {}
        if method in {"write", "unlink"}:
            return False
        if method in {"create"}:
            return None
        return []

    def _build_rpc_call(self, method: str, args: tuple, kwargs: dict):
        call_args = list(args)
        call_kwargs = copy.deepcopy(kwargs)
        lower_method = method.lower()

        if lower_method in {"search", "search_read"}:
            if call_args:
                call_args[0] = self._normalize_domain(call_args[0])
        elif lower_method == "read":
            if call_args:
                call_args[0] = self._normalize_ids(call_args[0])
        elif lower_method == "create":
            if call_args:
                first = call_args[0]
                if isinstance(first, tuple):
                    first = list(first)
                if isinstance(first, list) and len(first) == 1 and isinstance(first[0], dict):
                    first = first[0]
                call_args[0] = first
        elif lower_method == "write":
            ids_arg = call_args[0] if len(call_args) >= 1 else None
            vals_arg = call_args[1] if len(call_args) >= 2 else None

            if len(call_args) == 1 and isinstance(call_args[0], (list, tuple)) and len(call_args[0]) >= 2:
                ids_arg = call_args[0][0]
                vals_arg = call_args[0][1]

            call_args = []
            if ids_arg is not None:
                call_args.append(self._normalize_ids(ids_arg))
            if vals_arg is not None:
                vals = vals_arg
                if isinstance(vals, list) and len(vals) == 1 and isinstance(vals[0], dict):
                    vals = vals[0]
                call_args.append(vals)
        elif lower_method == "unlink":
            if call_args:
                call_args[0] = self._normalize_ids(call_args[0])

        return call_args, call_kwargs

    def _exec(self, method: str, args=None, kwargs=None, default=None):
        kwargs = copy.deepcopy(kwargs or {})
        if self.context:
            ctx = copy.deepcopy(self.context)
            if isinstance(kwargs.get("context"), dict):
                ctx.update(kwargs["context"])
            kwargs["context"] = ctx
        result = self.client.execute_kw(self.model, method, args=args or [], kwargs=kwargs, debug=self._debug, default=default)
        self.error = self.client.error
        return result

    def execute(self, method: str, *args, **kwargs):
        default = self._default_method_return(method)
        try:
            call_args, call_kwargs = self._build_rpc_call(method, args, kwargs)
        except Exception as exc:
            self.error = exc
            if self._debug:
                raise
            return default
        return self._exec(method, args=call_args, kwargs=call_kwargs, default=default)

    def execute_kw(self, method: str, *args, **kwargs):
        return self.execute(method, *args, **kwargs)

    def search(self, domain, **kwargs):
        return self.execute("search", domain, **kwargs)

    def read(self, ids, **kwargs):
        return self.execute("read", ids, **kwargs)

    def search_read(self, domain, **kwargs):
        records = self.execute("search_read", domain, **kwargs)
        if not isinstance(records, list):
            return []
        return [OdooRpcEntity(self, data) for data in records]

    def create(self, vals, **kwargs):
        return self.execute("create", vals, **kwargs)

    def write(self, ids, vals, **kwargs):
        return self.execute("write", ids, vals, **kwargs)

    def unlink(self, ids, **kwargs):
        return self.execute("unlink", ids, **kwargs)

    def get(self, pk):
        return OdooRpcEntity(self, pk)

    def entity(self, data):
        return OdooRpcEntity(self, data)

    def new(self):
        return OdooRpcEntity(self)

    def __getattr__(self, method):
        def function(*_args, **_kwargs):
            return self.execute(method, *_args, **_kwargs)

        return function
