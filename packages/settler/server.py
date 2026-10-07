"""HTTP commander for Circle and peaq. The robot calls this the way peaq ROS calls peaqos_node."""

from __future__ import annotations

import json
import os
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from circle_client import arc_line
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


def new_job_id() -> str:
    return "0x" + os.urandom(32).hex()


def as_tx(value: object) -> str:
    text = str(value or "")
    if text and not text.startswith("0x"):
        return "0x" + text
    return text


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
        self.lock = threading.Lock()
        self.jobs: dict[str, dict[str, Any]] = {}

    def record(self, job_id: str, line: str) -> None:
        if not job_id:
            print(f"[settler] {line}", flush=True)
            return
        with self.lock:
            row = self.jobs.setdefault(job_id, {"jobId": job_id, "lines": []})
            row["lines"].append(line)
        print(f"[settler] {line}", flush=True)

    def job_snapshot(self, job_id: str) -> dict[str, Any]:
        with self.lock:
            row = self.jobs.get(job_id)
            if row is None:
                return {"jobId": job_id, "lines": []}
            return {"jobId": row["jobId"], "lines": list(row["lines"])}

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
        if not job_id:
            job_id = new_job_id()
        if not job_id.startswith("0x") or len(job_id) != 66:
            return 400, {"error": "jobId must be 32 bytes hex"}
        machine_hex = machine_id_bytes32(self.wallets, str(body.get("machineId") or ""))
        try:
            self.record(job_id, f"locking 6.00 USDC for {room}")
            paid = deposit(self.env, self.wallets, job_id, machine_hex)
            self.record(job_id, arc_line("Circle deposit", paid.get("transactionId"), paid.get("txHash")))
            posted = self.post_bridge_job(job_id, room, items)
            self.record(job_id, "paid goal is on the bridge")
        except Exception as error:
            self.record(job_id, f"order failed {error}")
            return 502, {"error": str(error)}
        return 200, {
            "jobId": job_id,
            "room": room,
            "depositId": paid.get("transactionId"),
            "items": items,
            "goal": posted,
        }

    def pickup(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        job_id = str(body.get("jobId") or "")
        try:
            result = on_pickup(self.env, self.wallets, body, self.peaq)
        except Exception as error:
            self.record(job_id, f"pickup failed {error}")
            return 502, {"error": str(error)}
        circle = result.get("circle") or {}
        peaq_tx = as_tx((result.get("peaq") or {}).get("transactionHash"))
        self.record(job_id, arc_line("Circle vending 2.00", circle.get("transactionId"), circle.get("txHash")))
        self.record(job_id, f"peaq pickup revenue {peaq_tx}")
        return 200, result

    def delivery(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        job_id = str(body.get("jobId") or "")
        try:
            result = on_delivery(self.env, self.wallets, body, self.peaq)
        except Exception as error:
            self.record(job_id, f"delivery failed {error}")
            return 502, {"error": str(error)}
        circle = result.get("circle") or {}
        peaq_tx = as_tx((result.get("peaq") or {}).get("transactionHash"))
        self.record(job_id, arc_line("Circle release", circle.get("transactionId"), circle.get("txHash")))
        self.record(job_id, f"peaq delivery revenue {peaq_tx}")
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
            path = self.path.split("?", 1)[0]
            if path == "/health":
                self._json(200, {"ok": True})
                return
            if path.startswith("/jobs/"):
                job_id = path[len("/jobs/") :]
                self._json(200, settler.job_snapshot(job_id))
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
