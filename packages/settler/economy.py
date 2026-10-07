"""Local commander: Circle money then peaq record. Never imported by Webots."""

from __future__ import annotations

from typing import Any

from circle_client import ESCROW, VENDING, execute_contract, transfer_usdc
from peaq_client import PeaqMachine


def actor(wallets: dict[str, Any], label: str) -> dict[str, Any]:
    for row in wallets.get("actors") or []:
        if row.get("label") == label:
            return row
    return {}


def machine_id_bytes32(wallets: dict[str, Any], override: str = "") -> str:
    if override and override.startswith("0x") and len(override) == 66:
        return override
    machine = str(actor(wallets, "servebot-1").get("peaqMachineId") or "")
    if machine.startswith("0x") and len(machine) == 66:
        return machine
    if machine.isdigit():
        return "0x" + format(int(machine), "064x")
    return "0x" + ("0" * 64)


def deposit(env: dict[str, str], wallets: dict[str, Any], job_id: str, machine_hex: str) -> dict[str, Any]:
    guest = actor(wallets, "guest-bob")
    result = execute_contract(
        env,
        str(guest.get("circleWalletId") or ""),
        "deposit(bytes32,bytes32,uint256)",
        [job_id, machine_hex, "6000000"],
        job_id,
    )
    print(f"[settler] deposit {result['transactionId']}", flush=True)
    return result


def on_pickup(
    env: dict[str, str],
    wallets: dict[str, Any],
    body: dict[str, Any],
    peaq: PeaqMachine,
) -> dict[str, Any]:
    job_id = str(body.get("jobId") or "")
    robot = actor(wallets, "servebot-1")
    machine = str(body.get("peaqMachineId") or robot.get("peaqMachineId") or "")
    paid = transfer_usdc(
        env,
        str(body.get("circleWalletId") or robot.get("circleWalletId") or ""),
        VENDING,
        "2.00",
        job_id,
    )
    print(f"[settler] pickup transfer {paid['transactionId']}", flush=True)
    recorded = peaq.submit_revenue(machine, "200", f"arc:{paid['transactionId']}", paid["transactionId"])
    print(f"[settler] pickup peaq {recorded.get('transactionHash')}", flush=True)
    return {"circle": paid, "peaq": recorded}


def on_delivery(
    env: dict[str, str],
    wallets: dict[str, Any],
    body: dict[str, Any],
    peaq: PeaqMachine,
) -> dict[str, Any]:
    if body.get("failure") is True:
        raise RuntimeError("delivery failure is not handled by this settler")
    job_id = str(body.get("jobId") or "")
    settler = actor(wallets, "settler")
    robot = actor(wallets, "servebot-1")
    machine = str(body.get("peaqMachineId") or robot.get("peaqMachineId") or "")
    released = execute_contract(
        env,
        str(settler.get("circleWalletId") or ""),
        "release(bytes32)",
        [job_id],
        job_id,
    )
    print(f"[settler] release {released['transactionId']}", flush=True)
    recorded = peaq.submit_revenue(
        machine,
        "600",
        f"arc:{released['transactionId']}",
        released["transactionId"],
    )
    print(f"[settler] delivery peaq {recorded.get('transactionHash')}", flush=True)
    return {"circle": released, "peaq": recorded}


def unused_escrow() -> str:
    return ESCROW
