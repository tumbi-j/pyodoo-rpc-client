from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


class PublicExportsTests(unittest.TestCase):
    def test_public_exports_importable(self):
        from pyodoo_rpc_client import OdooRpcClient, OdooRpcConfigError, OdooRpcEntity, OdooRpcError, OdooRpcModel

        self.assertIsNotNone(OdooRpcClient)
        self.assertIsNotNone(OdooRpcModel)
        self.assertIsNotNone(OdooRpcEntity)
        self.assertIsNotNone(OdooRpcError)
        self.assertIsNotNone(OdooRpcConfigError)
