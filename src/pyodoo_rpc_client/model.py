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

    def _exec(self, method: str, args=None, kwargs=None, default=None):
        kwargs = dict(kwargs or {})
        if self.context:
            ctx = copy.deepcopy(self.context)
            if isinstance(kwargs.get("context"), dict):
                ctx.update(kwargs["context"])
            kwargs["context"] = ctx
        result = self.client.execute_kw(self.model, method, args=args or [], kwargs=kwargs, debug=self._debug, default=default)
        self.error = self.client.error
        return result

    def search(self, domain, **kwargs):
        return self._exec("search", args=[domain], kwargs=kwargs, default=[])

    def read(self, ids, **kwargs):
        return self._exec("read", args=[ids], kwargs=kwargs, default=[])

    def search_read(self, domain, **kwargs):
        records = self._exec("search_read", args=[domain], kwargs=kwargs, default=[])
        if not isinstance(records, list):
            return []
        return [OdooRpcEntity(self, data) for data in records]

    def create(self, vals, **kwargs):
        return self._exec("create", args=[vals], kwargs=kwargs, default=None)

    def write(self, ids, vals, **kwargs):
        return self._exec("write", args=[ids, vals], kwargs=kwargs, default=False)

    def unlink(self, ids, **kwargs):
        return self._exec("unlink", args=[ids], kwargs=kwargs, default=False)

    def get(self, pk):
        return OdooRpcEntity(self, pk)

    def entity(self, data):
        return OdooRpcEntity(self, data)

    def new(self):
        return OdooRpcEntity(self)

    def __getattr__(self, method):
        def function(*_args, **_kwargs):
            return self._exec(method, args=list(_args), kwargs=_kwargs, default=[])

        return function
