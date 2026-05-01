# pyodoo-rpc-client (Odoo RPC)

Python client for the Odoo legacy RPC API (XML-RPC object/common services), intended for Odoo v19 and below.

For the Odoo JSON 2 API (v19+ compliant), use `pyodoo-client`.

## Features

- XML-RPC `common` + `object` service support.
- ORM-like model accessor (`client.model("res.partner")`).
- `with_context` support on model instances.
- `OdooRpcEntity` convenience wrapper with `save`, `delete`, `refresh`.
- Runtime debug behavior — `debug=False` suppresses errors and returns safe fallbacks; `debug=True` raises.

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
    password="secret",   # or use key= for an API key
    debug=True,
)

partners = odoo.model("res.partner").search_read(
    [["is_company", "=", True]],
    fields=["name", "email"],
)

for p in partners:
    print(p.id, p.name)
```

## Authentication

```python
# Username + password
odoo = OdooRpcClient(url=..., db=..., username=..., password="secret")

# Username + API key
odoo = OdooRpcClient(url=..., db=..., username=..., key="your-api-key")
```

After construction, `odoo.logged_in` is `True` when authentication succeeded.

## OdooRpcClient

```python
OdooRpcClient(
    url,           # Odoo base URL, e.g. "http://localhost:8069"
    db,            # database name
    username,      # login username
    password=None, # password (use password or key, not both)
    key=None,      # API key (takes priority over password)
    debug=False,   # True → raises OdooRpcError on failure
    allow_none=True,
)
```

### Attributes

| Attribute   | Description                            |
| ----------- | -------------------------------------- |
| `logged_in` | `True` when authenticated successfully |
| `uid`       | Authenticated user ID                  |
| `error`     | Last error, or `None`                  |
| `debug`     | Current debug flag                     |

### Methods

| Method                                    | Description                                        |
| ----------------------------------------- | -------------------------------------------------- |
| `model(model_name)`                       | Returns an `OdooRpcModel` for the given Odoo model |
| `set_debug(bool)`                         | Toggle debug mode                                  |
| `execute_kw(model, method, args, kwargs)` | Raw XML-RPC call                                   |

## OdooRpcModel

Obtained via `odoo.model("res.partner")`.

### Common methods

All domain arguments are standard Odoo domain lists, e.g. `[["field", "operator", value]]`.
Additional Odoo keyword arguments (`fields`, `limit`, `offset`, `order`, `context`) are passed as keyword arguments.

```python
model = odoo.model("res.partner")

# Search — returns list of IDs
ids = model.search([["is_company", "=", True]], limit=10)

# Read — returns list of dicts
records = model.read([1, 2, 3], fields=["name", "email"])

# Search + read in one call — returns list of OdooRpcEntity
partners = model.search_read(
    [["is_company", "=", True]],
    fields=["name", "email"],
    limit=50,
    order="name asc",
)

# Create — returns new record ID
new_id = model.create({"name": "ACME", "is_company": True})

# Write — returns True on success
model.write([new_id], {"name": "ACME Corp"})

# Unlink (delete) — returns True on success
model.unlink([new_id])

# Fields metadata
meta = model.fields_get([], attributes=["string", "type", "required"])
```

### Context

```python
# Attach context to all calls made on this model instance
model_fr = odoo.model("res.partner").with_context({"lang": "fr_FR"})
partners = model_fr.search_read([["is_company", "=", True]], fields=["name"])

# Or pass context per-call
partners = odoo.model("res.partner").search_read(
    [["is_company", "=", True]],
    fields=["name"],
    context={"lang": "fr_FR"},
)
```

### Arbitrary methods

Any Odoo model method can be called directly:

```python
result = odoo.model("account.move").action_post(ids=[42])
```

## OdooRpcEntity

`search_read` returns a list of `OdooRpcEntity` objects. Field values are accessible as attributes.

```python
partners = odoo.model("res.partner").search_read(
    [["is_company", "=", True]],
    fields=["name", "email"],
)

for p in partners:
    print(p.id, p.name, p.email)

# Load a single entity by ID
partner = odoo.model("res.partner").get(1)

# Refresh from the server
partner.refresh()

# Modify and save
partner.name = "Updated Name"
partner.save()  # calls write() for existing records, create() for new ones

# Delete
partner.delete()

# Check if entity has an ID
partner.exists()  # True / False

# Get field data as a dict
data = partner.get_data(["name", "email"])
changed = partner.get_changed_data()  # only fields changed since load
```

## Error Handling

```python
# debug=False (default): safe fallback returned, error stored on client/model
odoo = OdooRpcClient(..., debug=False)
result = odoo.model("res.partner").search_read([["id", "=", -1]])
# result → []
# odoo.model(...).error or odoo.error holds the exception

# debug=True: raises OdooRpcError immediately
from pyodoo_rpc_client.exceptions import OdooRpcError

odoo = OdooRpcClient(..., debug=True)
try:
    result = odoo.model("res.partner").search_read([["bad_field", "=", 1]])
except OdooRpcError as e:
    print(e)
```

## Compatibility Notes

- Targets the Odoo XML-RPC API (`/xmlrpc/2/common`, `/xmlrpc/2/object`), available in Odoo v8–v19.
- For the Odoo JSON 2 API (v19+), use `pyodoo-client` instead.

## Contributing

- Open Issues for bugs and concrete feature requests.
- Open Pull Requests for code/docs improvements.
- For open-ended questions and ideas, use GitHub Discussions.
- See `CONTRIBUTING.md` for workflow and expectations.

## Development

```bash
# Install locally in editable mode (changes take effect immediately)
pip install -e .

# Build a distribution
pip install build twine
python -m build
python -m twine check dist/*
```
