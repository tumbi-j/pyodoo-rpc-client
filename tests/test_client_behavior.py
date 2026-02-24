from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pyodoo_rpc_client import OdooRpcClient
from pyodoo_rpc_client.entity import OdooRpcEntity
from pyodoo_rpc_client.exceptions import OdooRpcError


class DummyCommonProxy:
    def __init__(self, uid=1):
        self.uid = uid
        self.calls = []

    def authenticate(self, db, username, password, context):
        self.calls.append({"db": db, "username": username, "password": password, "context": context})
        return self.uid


class DummyModelsProxy:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def execute_kw(self, db, uid, password, model_name, method, args, kwargs):
        self.calls.append(
            {
                "db": db,
                "uid": uid,
                "password": password,
                "model_name": model_name,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            }
        )
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class OdooRpcClientBehaviorTests(unittest.TestCase):
    def test_model_search_read_merges_context(self):
        common_proxy = DummyCommonProxy(uid=42)
        models_proxy = DummyModelsProxy(responses=[[{"id": 7, "name": "Acme"}]])

        with patch("xmlrpc.client.ServerProxy", side_effect=[common_proxy, models_proxy]):
            client = OdooRpcClient(
                url="https://example.com",
                db="testdb",
                username="api@example.com",
                password="secret",
            )

        model = client.model("res.partner").with_context({"lang": "en_US"})
        result = model.search_read([["is_company", "=", True]], context={"tz": "UTC"})

        self.assertEqual(len(result), 1)
        self.assertIsInstance(result[0], OdooRpcEntity)
        self.assertEqual(result[0].id, 7)

        call = models_proxy.calls[0]
        self.assertEqual(call["method"], "search_read")
        self.assertEqual(call["args"][0], ["is_company", "=", True])
        self.assertEqual(call["kwargs"]["context"]["lang"], "en_US")
        self.assertEqual(call["kwargs"]["context"]["tz"], "UTC")

    def test_execute_kw_returns_default_when_debug_false_on_rpc_error(self):
        common_proxy = DummyCommonProxy(uid=1)
        models_proxy = DummyModelsProxy(responses=[RuntimeError("boom")])

        with patch("xmlrpc.client.ServerProxy", side_effect=[common_proxy, models_proxy]):
            client = OdooRpcClient(
                url="https://example.com",
                db="testdb",
                username="api@example.com",
                password="secret",
                debug=False,
            )

        default_value = []
        result = client.execute_kw("res.partner", "search_read", args=[[]], kwargs={}, default=default_value)

        self.assertEqual(result, default_value)
        self.assertIsInstance(client.error, OdooRpcError)
