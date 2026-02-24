from dataclasses import dataclass
from typing import Optional


@dataclass
class OdooRpcError(Exception):
    message: str
    cause: Optional[Exception] = None

    def __str__(self) -> str:
        return self.message


class OdooRpcConfigError(ValueError):
    pass
