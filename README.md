# pyodoo-rpc-client (Odoo RPC)

Python client for Odoo XML-RPC object/common services for older Odoo versions and legacy integrations.

## Features

- XML-RPC `common` + `object` service support.
- ORM-like model accessor (`client.model("res.partner")`).
- `with_context` support in model calls.
- `OdooRpcEntity` convenience API (`save`, `delete`, `refresh`).
- Runtime debug behavior (`debug=False` suppresses/records, `debug=True` raises).

## Installation

```bash
pip install pyodoo-rpc-client
```

## Quick Start

```python
from pyodoo_rpc_client import OdooRpcClient

odoo = OdooRpcClient(
    url="https://mycompany.example.com",
    db="mycompany",
    username="api-user@example.com",
    password="...",
    debug=False,
)

partners = odoo.model("res.partner").search_read(
    [["is_company", "=", True]],
    fields=["name", "email"],
)
```

## API Overview

### OdooRpcClient

- `OdooRpcClient(url, db, username, password=None, key=None, debug=False, allow_none=True)`
- `model(model_name)`
- `set_debug(bool)`
- `execute_kw(model_name, method, args=None, kwargs=None, debug=None, default=None)`

### OdooRpcModel

- `set_debug(bool)`
- `with_context(dict)`
- common methods: `search`, `read`, `search_read`, `create`, `write`, `unlink`, `fields_get`

### OdooRpcEntity

- `id`, `exists()`, `refresh()`
- `save()`, `delete()`, `get_data(...)`

## Error Handling

- `debug=False` (default): method-safe fallback values are returned and latest error is stored.
- `debug=True`: raises `OdooRpcError`.

## Compatibility Notes

- Intended for pre-JSON-2 Odoo integrations.
- Odoo 20 deprecates legacy RPC endpoints; for Odoo 19+ prefer `pyodoo-client`.

## Contributing

- Open Issues for bugs and concrete feature requests.
- Open Pull Requests for code/docs improvements.
- For open-ended questions and ideas, use GitHub Discussions (enable in repo settings).
- See `CONTRIBUTING.md` for workflow and expectations.

## Development

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine check dist/*
```
