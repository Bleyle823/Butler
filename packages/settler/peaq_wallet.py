"""Address-keyed EVM wallet file. Callers never receive the private key."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

PEAQ_CHAIN_ID = "eip155:3338"
PEAQ_NETWORK = "peaq"


def _tools():
    from eth_account import Account
    from eth_utils import is_address, to_checksum_address

    return Account, is_address, to_checksum_address


class PeaqWalletRegistry:
    def __init__(self, path: Path) -> None:
        self.path = path

    def import_key(self, private_key: str, label: str) -> str:
        Account, _, to_checksum_address = _tools()
        key = private_key.strip()
        if not key.startswith("0x"):
            key = "0x" + key
        address = str(to_checksum_address(Account.from_key(key).address))
        registry = self._read()
        wallets = registry.setdefault("wallets", {})
        wallets[address] = {
            "label": label or "servebot-1",
            "address": address,
            "account_id": f"{PEAQ_CHAIN_ID}:{address}",
            "chain_id": PEAQ_CHAIN_ID,
            "network": PEAQ_NETWORK,
            "private_key": key,
            "created_at": int(time.time()),
        }
        self._write(registry)
        return address

    def list_public(self) -> list[dict[str, str]]:
        rows = []
        for entry in self._wallets().values():
            if not isinstance(entry, dict):
                continue
            address = str(entry.get("address") or "")
            if not address:
                continue
            rows.append(
                {
                    "address": address,
                    "label": str(entry.get("label") or "machine_wallet"),
                    "account_id": f"{PEAQ_CHAIN_ID}:{address}",
                    "chain_id": PEAQ_CHAIN_ID,
                    "network": PEAQ_NETWORK,
                }
            )
        return rows

    def get_private_key(self, address: str) -> str:
        checksum = self.normalize(address)
        entry = self._wallets().get(checksum)
        if not isinstance(entry, dict):
            raise KeyError(f"unknown local peaq wallet {checksum}")
        key = str(entry.get("private_key") or "").strip()
        if not key:
            raise RuntimeError(f"missing private key for {checksum}")
        return key

    def normalize(self, address: str) -> str:
        _, is_address, to_checksum_address = _tools()
        value = (address or "").strip()
        if not value or not is_address(value):
            raise ValueError("address must be a valid 0x-prefixed EVM address")
        return str(to_checksum_address(value))

    def _wallets(self) -> dict[str, Any]:
        wallets = self._read().get("wallets")
        if not isinstance(wallets, dict):
            return {}
        return wallets

    def _read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"version": 1, "wallets": {}}
        data = json.loads(self.path.read_text(encoding="utf-8") or "{}")
        if not isinstance(data, dict):
            raise RuntimeError("wallet registry must be a JSON object")
        data.setdefault("version", 1)
        data.setdefault("wallets", {})
        return data

    def _write(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)
        except OSError:
            pass
        tmp.replace(self.path)
