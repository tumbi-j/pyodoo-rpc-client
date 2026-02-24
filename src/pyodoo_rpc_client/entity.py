from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .model import OdooRpcModel


class OdooRpcEntity:
    def __init__(self, model: "OdooRpcModel", data: Any = None):
        self.__model = model
        self.__init_data: Dict[str, Any] = {}
        self.__fields: Dict[str, Dict[str, Any]] = {}
        self.__id = None

        fields = model.fields()
        if fields:
            fields = dict(fields)
            fields.pop("id", None)
            self.__fields = fields

        if data is None:
            return

        if isinstance(data, dict):
            self.__init_data = dict(data)
            if data.get("id") is not None:
                self.__id = data["id"]
            self.set_data(data)
        else:
            self.load(data)

    @property
    def id(self):
        return self.__id

    def exists(self) -> bool:
        return bool(self.__id)

    def __iter__(self):
        if self.__id is not None:
            yield "id", self.__id
        for key in self.__fields.keys():
            if hasattr(self, key):
                yield key, getattr(self, key)

    def load(self, record_id: Any):
        result = self.__model.read([int(record_id)])
        data = dict(result[0]) if result else {}
        self.__init_data = data
        if data.get("id") is not None:
            self.__id = data["id"]
        self.set_data(data)

    def refresh(self):
        if self.__id is not None:
            self.load(self.__id)

    def set_data(self, data: Dict[str, Any]):
        if not data:
            return
        item_data = dict(data)
        item_data.pop("id", None)
        for key, value in item_data.items():
            setattr(self, key, value)

    def get_data(self, fields: Optional[Iterable[str]] = None):
        data = dict(self)
        if fields:
            return {key: data[key] for key in fields if key in data or key == "id"}
        return data

    def get_changed_data(self):
        current_data = dict(self)
        return {key: val for key, val in current_data.items() if val != self.__init_data.get(key, None)}

    def save(self):
        if self.__id is not None:
            data = self.get_changed_data()
            if data:
                self.__model.write([self.__id], data)
        else:
            create_result = self.__model.create(dict(self))
            if create_result:
                self.__id = create_result
                self.refresh()
        return self.__id

    def delete(self):
        if self.__id is not None:
            return self.__model.unlink([self.__id])
        return False
