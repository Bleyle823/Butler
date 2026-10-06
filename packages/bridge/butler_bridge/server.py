"""Butler bridge HTTP API.

KeeperHub posts jobs. The robot posts pose. This process never calls peaq or Circle.
Webhook bodies are the only place peaq and Circle ids appear, and they come from
config/wallets.json on this machine.
"""

from __future__ import annotations

import json
import math
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
_LOCAL_CONFIG = ROOT / "config" / "bridge.json"
DEFAULT_CONFIG = _LOCAL_CONFIG if _LOCAL_CONFIG.exists() else ROOT / "config" / "bridge.example.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Ledger:
    def __init__(self, config: dict[str, Any], wallets: dict[str, Any]) -> None:
        self.config = config
        self.wallets = wallets
        self.lock = threading.Lock()
        self.fleet: dict[str, dict[str, Any]] = {}
        self.jobs: dict[str, dict[str, Any]] = {}
        self.goals: dict[str, dict[str, Any] | None] = {}
        self.suspended: set[str] = set()
        self.dwell_since: dict[str, float] = {}
        self.sent: dict[str, set[str]] = {}

    def actor(self, label: str) -> dict[str, Any]:
        for row in self.wallets.get("actors", []):
            if row.get("label") == label:
                return row
        return {}

    def room_pose(self, room: str) -> tuple[float, float] | None:
        rooms = self.config.get("rooms", {})
        row = rooms.get(room)
        if not isinstance(row, dict):
            return None
        return float(row["x"]), float(row["y"])

    def distance(self, robot: str, room: str) -> float | None:
        pose = self.fleet.get(robot, {}).get("pose")
        target = self.room_pose(room)
        if not pose or target is None:
            return None
        return math.hypot(pose[0] - target[0], pose[1] - target[1])


def _post_json(url: str, body: dict[str, Any], secret: str, token: str = "") -> None:
    if not url:
        return
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Butler-Secret": secret,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            response.read()
    except urllib.error.URLError:
        return


class Bridge:
    def __init__(self, config: dict[str, Any], wallets: dict[str, Any]) -> None:
        self.ledger = Ledger(config, wallets)
        self.secret = str(config.get("secret") or "")
        keeperhub = config.get("keeperhub") or {}
        self.pickup_url = str(keeperhub.get("pickup_webhook") or "")
        self.delivery_url = str(keeperhub.get("delivery_webhook") or "")
        self.webhook_token = str(keeperhub.get("webhook_token") or "")
        self.dwell_sec = float(config.get("dwell_sec") or 8)
        self.radius = float(config.get("arrive_radius") or 0.8)
        self.pickup = config.get("pickup_pose") or {"x": 8.70, "y": -4.62}

    def fleet_view(self) -> dict[str, Any]:
        robots = []
        with self.ledger.lock:
            names = set(self.ledger.fleet) | set(self.ledger.suspended)
            for name in sorted(names):
                row = dict(self.ledger.fleet.get(name) or {})
                row["name"] = name
                row["suspended"] = name in self.ledger.suspended
                row["busy"] = any(
                    job.get("robot") == name and job.get("status") in {"assigned", "pickup", "delivering"}
                    for job in self.ledger.jobs.values()
                )
                robots.append(row)
        return {"robots": robots}

    def create_job(self, body: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        room = str(body.get("room") or "")
        robot = str(body.get("robot") or "servebot-1")
        job_id = str(body.get("jobId") or "")
        if self.ledger.room_pose(room) is None:
            return 409, {"error": "unknown room"}
        if not job_id:
            return 400, {"error": "jobId is required"}
        with self.ledger.lock:
            if robot in self.ledger.suspended:
                return 409, {"error": "robot suspended"}
            self.ledger.jobs[job_id] = {
                "jobId": job_id,
                "robot": robot,
                "room": room,
                "status": "assigned",
                "peaqMachineId": body.get("peaqMachineId") or self.ledger.actor(robot).get("peaqMachineId"),
                "circleWalletId": body.get("circleWalletId") or self.ledger.actor(robot).get("circleWalletId"),
                "guestWalletId": body.get("guestWalletId") or self.ledger.actor("guest-bob").get("circleWalletId"),
                "vendingWalletId": body.get("vendingWalletId") or self.ledger.actor("vending").get("circleWalletId"),
            }
            self.ledger.goals[robot] = {"jobId": job_id, "room": room}
            self.ledger.sent[job_id] = set()
        return 201, {"jobId": job_id, "robot": robot, "room": room}

    def cancel(self, job_id: str) -> tuple[int, dict[str, Any]]:
        with self.ledger.lock:
            job = self.ledger.jobs.get(job_id)
            if job is None:
                return 404, {"error": "unknown job"}
            job["status"] = "cancelled"
            robot = job["robot"]
            if self.ledger.goals.get(robot, {}) and self.ledger.goals[robot].get("jobId") == job_id:
                self.ledger.goals[robot] = None
        return 200, {"jobId": job_id, "status": "cancelled"}

    def set_suspended(self, robot: str, suspended: bool) -> dict[str, Any]:
        with self.ledger.lock:
            if suspended:
                self.ledger.suspended.add(robot)
                self.ledger.goals[robot] = None
            else:
                self.ledger.suspended.discard(robot)
        return {"robot": robot, "suspended": suspended}

    def goal_for(self, robot: str) -> dict[str, Any]:
        with self.ledger.lock:
            goal = self.ledger.goals.get(robot)
        if not goal:
            return {}
        return {"jobId": goal["jobId"], "room": goal["room"]}

    def telemetry(self, body: dict[str, Any]) -> None:
        name = str(body.get("name") or "")
        if not name:
            return
        pose = body.get("pose") or [0, 0, 0, 0]
        event = str(body.get("event") or "")
        with self.ledger.lock:
            self.ledger.fleet[name] = {
                "pose": pose,
                "battery": body.get("battery", 0),
                "event": event,
                "carried": body.get("carried") or [],
            }
            job = self._active_job(name)
            if job is None:
                return
            self._maybe_pickup(job, pose, event)
            self._maybe_delivery(job, pose, event)

    def _active_job(self, robot: str) -> dict[str, Any] | None:
        for job in self.ledger.jobs.values():
            if job.get("robot") == robot and job.get("status") in {"assigned", "pickup", "delivering"}:
                return job
        return None

    def _near(self, pose: list[float], x: float, y: float) -> bool:
        return math.hypot(float(pose[0]) - x, float(pose[1]) - y) <= self.radius

    def _maybe_pickup(self, job: dict[str, Any], pose: list[float], event: str) -> None:
        job_id = job["jobId"]
        if "pickup" in self.ledger.sent.get(job_id, set()):
            return
        at_counter = self._near(pose, float(self.pickup["x"]), float(self.pickup["y"]))
        if event != "pickup" and not at_counter:
            return
        if event != "pickup":
            return
        job["status"] = "delivering"
        self.ledger.sent.setdefault(job_id, set()).add("pickup")
        robot = job["robot"]
        payload = {
            "jobId": job_id,
            "robot": robot,
            "event": "pickup",
            "peaqMachineId": job.get("peaqMachineId") or "",
            "circleWalletId": job.get("circleWalletId") or "",
            "vendingWalletId": job.get("vendingWalletId") or "",
            "guestWalletId": job.get("guestWalletId") or "",
        }
        threading.Thread(
            target=_post_json,
            args=(self.pickup_url, payload, self.secret, self.webhook_token),
            daemon=True,
        ).start()

    def _maybe_delivery(self, job: dict[str, Any], pose: list[float], event: str) -> None:
        job_id = job["jobId"]
        if "delivery" in self.ledger.sent.get(job_id, set()):
            return
        target = self.ledger.room_pose(job["room"])
        if target is None:
            return
        at_room = self._near(pose, target[0], target[1]) or event == "delivery"
        now = time.monotonic()
        if not at_room:
            self.ledger.dwell_since.pop(job_id, None)
            return
        started = self.ledger.dwell_since.get(job_id)
        if started is None:
            self.ledger.dwell_since[job_id] = now
            return
        dwell = now - started
        if dwell < self.dwell_sec and event != "delivery":
            return
        if event == "delivery" and dwell < self.dwell_sec:
            return
        job["status"] = "delivered"
        self.ledger.sent.setdefault(job_id, set()).add("delivery")
        payload = {
            "jobId": job_id,
            "robot": job["robot"],
            "event": "delivery",
            "dwellSec": round(dwell, 3),
            "pose": pose,
            "failure": False,
            "peaqMachineId": job.get("peaqMachineId") or "",
            "circleWalletId": job.get("circleWalletId") or "",
            "guestWalletId": job.get("guestWalletId") or "",
        }
        threading.Thread(
            target=_post_json,
            args=(self.delivery_url, payload, self.secret, self.webhook_token),
            daemon=True,
        ).start()


def make_handler(bridge: Bridge) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:
            return

        def _json(self, code: int, body: dict[str, Any]) -> None:
            raw = json.dumps(body).encode("utf-8")
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

        def _authed(self) -> bool:
            return self.headers.get("X-Butler-Secret") == bridge.secret

        def _localhost(self) -> bool:
            host = self.client_address[0]
            return host in {"127.0.0.1", "::1"}

        def do_GET(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/fleet":
                if not self._authed():
                    self._json(401, {"error": "unauthorized"})
                    return
                self._json(200, bridge.fleet_view())
                return
            if path.startswith("/robots/") and path.endswith("/goal"):
                if not self._localhost():
                    self._json(403, {"error": "localhost only"})
                    return
                robot = path.split("/")[2]
                self._json(200, bridge.goal_for(robot))
                return
            self._json(404, {"error": "not found"})

        def do_POST(self) -> None:
            path = self.path.split("?", 1)[0]
            if path == "/telemetry":
                if not self._localhost():
                    self._json(403, {"error": "localhost only"})
                    return
                bridge.telemetry(self._read())
                self._json(204, {})
                return
            if not self._authed():
                self._json(401, {"error": "unauthorized"})
                return
            if path == "/jobs":
                code, body = bridge.create_job(self._read())
                self._json(code, body)
                return
            parts = [part for part in path.split("/") if part]
            if len(parts) == 3 and parts[0] == "jobs" and parts[2] == "cancel":
                code, body = bridge.cancel(parts[1])
                self._json(code, body)
                return
            if len(parts) == 3 and parts[0] == "fleet" and parts[2] in {"suspend", "resume"}:
                body = bridge.set_suspended(parts[1], parts[2] == "suspend")
                self._json(200, body)
                return
            self._json(404, {"error": "not found"})

    return Handler


def load_runtime(config_path: Path | None = None) -> Bridge:
    path = config_path or DEFAULT_CONFIG
    config = load_json(path)
    wallets_path = ROOT / str(config.get("wallets_path") or "config/wallets.example.json")
    if not wallets_path.exists():
        wallets_path = ROOT / "config" / "wallets.example.json"
    wallets = load_json(wallets_path)
    return Bridge(config, wallets)


def serve(host: str, port: int, bridge: Bridge) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), make_handler(bridge))
    return server


def main() -> None:
    bridge = load_runtime()
    host = str(bridge.ledger.config.get("host") or "127.0.0.1")
    port = int(bridge.ledger.config.get("port") or 8787)
    server = serve(host, port, bridge)
    print(f"butler bridge http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
