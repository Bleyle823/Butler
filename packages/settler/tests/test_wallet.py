"""Local peaq wallet registry. The public listing must not include the key."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from eth_account import Account

from peaq_wallet import PeaqWalletRegistry


class WalletRegistryTest(unittest.TestCase):
    def test_import_lists_address_only(self) -> None:
        account = Account.create()
        with tempfile.TemporaryDirectory() as folder:
            registry = PeaqWalletRegistry(Path(folder) / "peaqos_wallets.json")
            address = registry.import_key(account.key.hex(), "servebot-1")
            public = registry.list_public()
            self.assertEqual(public[0]["address"], address)
            self.assertNotIn("private_key", public[0])
            stored = registry.get_private_key(address)
            self.assertTrue(stored.startswith("0x"))
            self.assertEqual(Account.from_key(stored).address, address)


if __name__ == "__main__":
    unittest.main()
