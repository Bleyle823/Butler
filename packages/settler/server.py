"""HTTP commander for Circle and peaq. The sim never talks to this except via the bridge."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from economy import actor, deposit, machine_id_bytes32, on_delivery, on_pickup
from peaq_client import PeaqMachine

ROOT = Path(__file__).resolve().parents[2]
KITCHEN_ITEMS = ["honey jar", "jam jar 1", "jam jar 2"]


def load_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :]
        name, raw = stripped.split("=", 1)
        values[name.strip()] = raw.strip().strip('"').strip("'")
    return values


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Settler:
    def __init__(self) -> None:
        env_path = ROOT / ".env"
        self.env = load_env(env_path)
        wallets_path = ROOT / "config" / "wallets.json"
        if not wallets_path.exists():
            wallets_path = ROOT / "config" / "wallets.example.json"
        self.wallets = load_json(wallets_path)
        self.bridge_url = self.env.get("BUTLER_BRIDGE_URL") or "http://127.0.0.1:8787"
        self.secret = self.env.get("BUTLER_SECRET") or "change-me"
        self.host = self.env.get("SETTLER_HOST") or "127.0.0.1"
        self.port = int(self.env.get("SETTLER_PORT") or "8788")
        self.peaq = PeaqMachine(self.env)

    def post_bridge_job(self, job_id: str, room: str, items: list[str]) -> dict[str, Any]:
        robot = actor(self.wallets, "servebot-1")
        guest = actor(self.wallets, "guest-bob")
        vending = actor(self.wallets, "vending")
        body = {
            "jobId": job_id,
            "robot": "servebot-1",
            "room": room,
            "items": items,
            "peaqMachineId": robot.get("peaqMachineId") or "",
            "circleWalletId": robot.get("circleWalletId") or "",
            "guestWalletId": guest.get("circleWalletId") or "",
            "vendingWalletId": vending.get("circleWalletId") or "",
        }
        data = json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.bridge_url.rstrip("/") + "/jobs",
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-Butler-Secret": self.secret,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=15) as response:
                return json.loads(response.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as error:
            raw = error.read().decode("utf-8")
            raise RuntimeError(raw or f"bridge HTTP {error.code}") from error

    def order(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        room = str(body.get("room") or "")
        job_id = str(body.get("jobId") or "")
        if room not in {"room-1204", "room-1205", "room-1206"}:
            return 400, {"error": "Unknown room"}
        items = [str(name) for name in (body.get("items") or [])]
        if items != KITCHEN_ITEMS:
            return 400, {"error": "Order is honey jar, jam jar 1, and jam jar 2"}
        if not job_id.startswith("0x") or len(job_id) != 66:
            return 400, {"error": "jobId must be 32 bytes hex"}
        machine_hex = machine_id_bytes32(self.wallets, str(body.get("machineId") or ""))
        try:
            paid = deposit(self.env, self.wallets, job_id, machine_hex)
            posted = self.post_bridge_job(job_id, room, items)
        except Exception as error:
            print(f"[settler] order failed {error}", flush=True)
            return 502, {"error": str(error)}
        return 200, {
            "jobId": job_id,
            "room": room,
            "depositId": paid.get("transactionId"),
            "items": items,
            "goal": posted,
        }

    def pickup(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        try:
            result = on_pickup(self.env, self.wallets, body, self.peaq)
        except Exception as error:
            print(f"[settler] pickup failed {error}", flush=True)
            return 502, {"error": str(error)}
        return 200, result

    def delivery(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        try:
            result = on_delivery(self.env, self.wallets, body, self.peaq)
        except Exception as error:
            print(f"[settler] delivery failed {error}", flush=True)
            return 502, {"error": str(error)}
        return 200, result


def make_handler(settler: Settler) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _json(self, code: int, body: dict[str, Any]) -> None:
            raw = json.dumps(body, default=str).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _read(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length") or 0)
            if length == 0:
                return {}
            return json.loads(self.rfile.read(length).decode("utf-8"))

        def do_GET(self) -> None:
            if self.path.split("?", 1)[0] == "/health":
                self._json(200, {"ok": True})
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:
            path = self.path.split("?", 1)[0]
            body = self._read()
            if path == "/order":
                code, result = settler.order(body)
                self._json(code, result)
                return
            if path == "/pickup":
                code, result = settler.pickup(body)
                self._json(code, result)
                return
            if path == "/delivery":
                code, result = settler.delivery(body)
                self._json(code, result)
                return
            self._json(404, {"error": "not found"})

    return Handler


def main() -> None:
    settler = Settler()
    server = ThreadingHTTPServer((settler.host, settler.port), make_handler(settler))
    print(f"butler settler http://{settler.host}:{settler.port}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
