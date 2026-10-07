"""Circle developer-controlled wallets. Keys stay in the settler process."""

from __future__ import annotations

import hashlib
import json
import ssl
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HELPER = Path(__file__).resolve().parent / "circle_cipher.js"
USDC_ARC = "0x3600000000000000000000000000000000000000"
ARC_TESTNET = "ARC-TESTNET"
ARCSCAN = "https://testnet.arcscan.app/tx/"
ESCROW = "0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD"
VENDING = "0x01ed2f186edab0b28dd796afe0762fac5a5b092d"


def circle_host(env: dict[str, str]) -> str:
    circle_env = (env.get("CIRCLE_ENV") or "sandbox").lower()
    if circle_env == "production":
        return "https://api.circle.com"
    return "https://api-sandbox.circle.com"


def derive_idempotency_key(job_id: str, step_name: str) -> str:
    digest = hashlib.sha256(f"{job_id}:{step_name}".encode("utf-8")).hexdigest()
    return f"{digest[:8]}-{digest[8:12]}-5{digest[13:16]}-a{digest[17:20]}-{digest[20:32]}"


def entity_secret_ciphertext(api_key: str, entity_secret: str, host: str) -> str:
    completed = subprocess.run(
        ["node", str(HELPER), api_key, entity_secret, host],
        check=False,
        capture_output=True,
        text=True,
        cwd=str(ROOT),
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or "circle cipher failed")
    return completed.stdout.strip()


def circle_post(
    env: dict[str, str],
    path: str,
    body: dict[str, Any],
    idempotency_key: str,
) -> dict[str, Any]:
    api_key = env.get("CIRCLE_API_KEY") or ""
    secret = env.get("CIRCLE_ENTITY_SECRET") or ""
    if not api_key or not secret:
        raise RuntimeError("CIRCLE_API_KEY and CIRCLE_ENTITY_SECRET are required")
    host = circle_host(env)
    payload = dict(body)
    payload["entitySecretCiphertext"] = entity_secret_ciphertext(api_key, secret, host)
    payload["idempotencyKey"] = idempotency_key
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        host + path,
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "butler-check/1.0",
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(request, timeout=60, context=ctx) as response:
            parsed = json.loads(response.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8")
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"message": raw}
        raise RuntimeError(parsed.get("message") or f"Circle HTTP {error.code}") from error
    data_obj = parsed.get("data") if isinstance(parsed, dict) else None
    if not isinstance(data_obj, dict):
        data_obj = parsed if isinstance(parsed, dict) else {}
    tx_id = str(data_obj.get("id") or data_obj.get("transactionId") or "")
    if not tx_id:
        raise RuntimeError("Circle returned no transaction id")
    tx_hash = wait_for_tx_hash(env, tx_id)
    return {"transactionId": tx_id, "txHash": tx_hash, "raw": parsed}


def circle_get(env: dict[str, str], path: str) -> dict[str, Any]:
    api_key = env.get("CIRCLE_API_KEY") or ""
    if not api_key:
        raise RuntimeError("CIRCLE_API_KEY and CIRCLE_ENTITY_SECRET are required")
    request = urllib.request.Request(
        circle_host(env) + path,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
            "User-Agent": "butler-check/1.0",
        },
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(request, timeout=30, context=ctx) as response:
        parsed = json.loads(response.read().decode("utf-8") or "{}")
    return parsed if isinstance(parsed, dict) else {}


def wait_for_tx_hash(env: dict[str, str], tx_id: str, timeout_sec: float = 45) -> str:
    deadline = time.time() + timeout_sec
    while True:
        try:
            parsed = circle_get(env, f"/v1/w3s/transactions/{tx_id}")
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError):
            parsed = {}
        data = parsed.get("data") if isinstance(parsed.get("data"), dict) else {}
        tx = data.get("transaction") if isinstance(data.get("transaction"), dict) else data
        digest = str(tx.get("txHash") or "")
        state = str(tx.get("state") or "")
        if digest:
            return digest
        if state in {"FAILED", "CANCELLED", "DENIED"}:
            return ""
        if time.time() >= deadline:
            return ""
        time.sleep(2)


def arc_line(label: str, circle_id: object, tx_hash: object) -> str:
    digest = str(tx_hash or "")
    if digest and not digest.startswith("0x"):
        digest = "0x" + digest
    if digest:
        return f"{label} {circle_id} arc {ARCSCAN}{digest}"
    return f"{label} {circle_id} arc hash pending"


def execute_contract(
    env: dict[str, str],
    wallet_id: str,
    signature: str,
    parameters: list[Any],
    job_id: str,
) -> dict[str, Any]:
    return circle_post(
        env,
        "/v1/w3s/developer/transactions/contractExecution",
        {
            "walletId": wallet_id,
            "contractAddress": ESCROW,
            "abiFunctionSignature": signature,
            "abiParameters": parameters,
            "blockchain": ARC_TESTNET,
            "feeLevel": "MEDIUM",
        },
        derive_idempotency_key(job_id, f"execute:{signature}"),
    )


def transfer_usdc(
    env: dict[str, str],
    wallet_id: str,
    destination: str,
    amount: str,
    job_id: str,
) -> dict[str, Any]:
    return circle_post(
        env,
        "/v1/w3s/developer/transactions/transfer",
        {
            "walletId": wallet_id,
            "destinationAddress": destination,
            "amounts": [amount],
            "tokenAddress": USDC_ARC,
            "blockchain": ARC_TESTNET,
            "feeLevel": "MEDIUM",
        },
        derive_idempotency_key(job_id, "transfer-usdc"),
    )
