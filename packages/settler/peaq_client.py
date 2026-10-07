"""peaqOS writes through peaq-os-sdk. The signer is an address, not a key on the wire."""

from __future__ import annotations

import sys
import time
import types
from pathlib import Path
from typing import Any

import yaml

from peaq_wallet import PeaqWalletRegistry


def _allow_sdk_import() -> None:
    """peaq-os-sdk 0.10 imports Unix pwd while loading. Butler only submits events."""
    if sys.platform != "win32" or "pwd" in sys.modules:
        return
    stub = types.ModuleType("pwd")

    def _missing(*_args: object, **_kwargs: object) -> None:
        raise OSError("pwd is not available on Windows")

    stub.getpwnam = _missing  # type: ignore[attr-defined]
    stub.getpwuid = _missing  # type: ignore[attr-defined]
    sys.modules["pwd"] = stub

ROOT = Path(__file__).resolve().parents[2]


def load_peaq_config(path: Path | None = None) -> dict[str, Any]:
    target = path or ROOT / "config" / "peaq.yaml"
    if not target.exists():
        target = ROOT / "config" / "peaq.example.yaml"
    data = yaml.safe_load(target.read_text(encoding="utf-8")) or {}
    peaq_os = data.get("peaq_os") or {}
    if not isinstance(peaq_os, dict):
        raise RuntimeError("peaq_os config is missing")
    return peaq_os


class PeaqMachine:
    def __init__(self, env: dict[str, str], config: dict[str, Any] | None = None) -> None:
        self.config = config or load_peaq_config()
        registry_path = Path(str((self.config.get("wallet_registry") or {}).get("path") or "config/peaqos_wallets.json"))
        if not registry_path.is_absolute():
            registry_path = ROOT / registry_path
        self.wallets = PeaqWalletRegistry(registry_path)
        self.signer = str((self.config.get("defaults") or {}).get("machine_address") or "").strip()
        seeded = env.get("PEAQ_CONTROLLER_PRIVATE_KEY") or ""
        if seeded:
            imported = self.wallets.import_key(seeded, "servebot-1")
            if not self.signer:
                self.signer = imported
        if not self.signer:
            public = self.wallets.list_public()
            if len(public) == 1:
                self.signer = public[0]["address"]

    def submit_revenue(
        self,
        machine_id: str,
        value: str,
        raw_data: str,
        source_tx_hash: str = "",
    ) -> dict[str, str]:
        if not self.signer:
            raise RuntimeError(
                "No peaq signer address. Set defaults.machine_address or PEAQ_CONTROLLER_PRIVATE_KEY once so the local registry can store it."
            )
        if not machine_id:
            raise RuntimeError("peaq machine id is required")
        _allow_sdk_import()
        from peaq_os_sdk import OperationalLimits, PeaqosClient
        from peaq_os_sdk.constants import EVENT_TYPE_REVENUE
        from peaq_os_sdk.types.events import SubmitEventParams

        contracts = self.config.get("contracts") or {}
        limits_cfg = self.config.get("operational_limits") or {}
        private_key = self.wallets.get_private_key(self.signer)
        client = PeaqosClient(
            rpc_url=str(self.config.get("rpc_url") or "https://quicknode1.peaq.xyz"),
            private_key=private_key,
            identity_registry=str(contracts.get("identity_registry") or ""),
            identity_staking=str(contracts.get("identity_staking") or ""),
            event_registry=str(contracts.get("event_registry") or ""),
            machine_nft=str(contracts.get("machine_nft") or ""),
            did_registry=str(contracts.get("did_registry") or ""),
            batch_precompile=str(contracts.get("batch_precompile") or ""),
            machine_account_factory=str(contracts.get("machine_account_factory") or "") or None,
            machine_nft_adapter=str(contracts.get("machine_nft_adapter") or "") or None,
            api_url=str(self.config.get("api_url") or "https://mcr.peaq.xyz"),
            operational_limits=OperationalLimits(
                max_value_per_tx=int(limits_cfg.get("max_value_per_tx") or 0),
                rate_limit_max_events=int(limits_cfg.get("rate_limit_max_events") or 0),
                rate_limit_window_seconds=int(limits_cfg.get("rate_limit_window_seconds") or 0),
            ),
        )
        note = (raw_data or "arc").encode("utf-8")
        source_text = (source_tx_hash or "").strip()
        source = source_text if source_text.startswith("0x") and len(source_text) == 66 else None
        params = SubmitEventParams(
            machine_id=int(machine_id),
            event_type=EVENT_TYPE_REVENUE,
            value=int(value),
            timestamp=int(time.time()) - 30,
            raw_data=note,
            trust_level=0,
            source_chain_id=0,
            source_tx_hash=source,
            metadata=b"",
            currency="USD",
        )
        tx_hash, data_hash = client.submit_event(
            machine_id=params.machine_id,
            event_type=params.event_type,
            value=params.value,
            timestamp=params.timestamp,
            raw_data=params.raw_data,
            trust_level=params.trust_level,
            source_chain_id=params.source_chain_id,
            source_tx_hash=params.source_tx_hash,
            metadata=params.metadata,
            currency="USD",
        )
        digest = data_hash.hex() if isinstance(data_hash, (bytes, bytearray)) else str(data_hash)
        if not digest.startswith("0x"):
            digest = "0x" + digest
        return {"transactionHash": str(tx_hash), "dataHash": digest, "signer": self.signer}
