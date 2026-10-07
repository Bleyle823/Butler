"""Scripted trip: jar pickup, kitchen table delivery, dwell of at least 8 seconds."""

from __future__ import annotations

import json
import threading
import time
import unittest
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from butler_bridge.server import Bridge


WEBHOOKS: list[dict] = []


class _Webhook(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        return

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length).decode("utf-8"))
        body["_path"] = self.path
        WEBHOOKS.append(body)
        raw = b"{}"
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(raw)


class BridgeTripTest(unittest.TestCase):
    def setUp(self) -> None:
        WEBHOOKS.clear()
        self.hooks = ThreadingHTTPServer(("127.0.0.1", 0), _Webhook)
        self.hook_thread = threading.Thread(target=self.hooks.serve_forever, daemon=True)
        self.hook_thread.start()
        port = self.hooks.server_address[1]
        config = {
            "secret": "test-secret",
            "dwell_sec": 8,
            "arrive_radius": 0.8,
            "pickup_pose": {"x": 1.72, "y": 0.69},
            "rooms": {"room-1204": {"x": -5.95, "y": -3.25}},
            "settler": {
                "pickup_url": f"http://127.0.0.1:{port}/pickup",
                "delivery_url": f"http://127.0.0.1:{port}/delivery",
            },
        }
        wallets = {
            "actors": [
                {"label": "servebot-1", "circleWalletId": "w-robot", "peaqMachineId": "m-1"},
                {"label": "vending", "circleWalletId": "w-vend"},
                {"label": "guest-bob", "circleWalletId": "w-guest"},
            ]
        }
        self.bridge = Bridge(config, wallets)
        self.http = ThreadingHTTPServer(("127.0.0.1", 0), __import__(
            "butler_bridge.server", fromlist=["make_handler"]
        ).make_handler(self.bridge))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.http.server_address[1]}"

    def tearDown(self) -> None:
        self.http.shutdown()
        self.hooks.shutdown()

    def _req(self, method: str, path: str, body: dict | None = None, secret: str | None = "test-secret"):
        data = None if body is None else json.dumps(body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if secret is not None:
            headers["X-Butler-Secret"] = secret
        request = urllib.request.Request(self.base + path, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=2) as response:
                raw = response.read()
                return response.status, json.loads(raw.decode("utf-8") or "{}")
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read().decode("utf-8") or "{}")

    def test_unknown_room_and_auth(self) -> None:
        code, _ = self._req("GET", "/fleet", secret="nope")
        self.assertEqual(code, 401)
        code, body = self._req("POST", "/jobs", {"jobId": "j", "room": "room-9999"})
        self.assertEqual(code, 409)
        self.assertEqual(body["error"], "unknown room")

    def test_scripted_trip_dwells_eight_seconds(self) -> None:
        code, _ = self._req(
            "POST",
            "/jobs",
            {"jobId": "job-1204", "robot": "servebot-1", "room": "room-1204"},
        )
        self.assertEqual(code, 201)
        code, goal = self._req("GET", "/robots/servebot-1/goal", secret=None)
        self.assertEqual(goal["room"], "room-1204")
        self.assertNotIn("peaqMachineId", goal)

        self.bridge.telemetry(
            {"name": "servebot-1", "pose": [1.72, 0.69, 0.1, 0], "battery": 0.9, "event": "pickup", "carried": ["honey jar"]}
        )
        time.sleep(0.3)
        self.assertEqual(WEBHOOKS[0]["_path"], "/pickup")
        self.assertEqual(WEBHOOKS[0]["peaqMachineId"], "m-1")

        self.bridge.telemetry(
            {"name": "servebot-1", "pose": [-0.38, -0.68, 0.1, 0], "battery": 0.8, "event": "", "carried": ["honey jar"]}
        )
        time.sleep(0.2)
        self.assertEqual(len(WEBHOOKS), 1)
        self.bridge.telemetry(
            {"name": "servebot-1", "pose": [-5.95, -3.25, 0.1, 0], "battery": 0.8, "event": "", "carried": []}
        )
        time.sleep(0.2)
        self.assertEqual(len(WEBHOOKS), 1)
        self.bridge.telemetry(
            {"name": "servebot-1", "pose": [-0.38, -0.68, 0.1, 0], "battery": 0.8, "event": "delivery", "carried": ["honey jar"]}
        )
        time.sleep(0.2)
        self.assertEqual(len(WEBHOOKS), 1)
        time.sleep(8.1)
        self.bridge.telemetry(
            {"name": "servebot-1", "pose": [-0.38, -0.68, 0.1, 0], "battery": 0.8, "event": "delivery", "carried": ["honey jar"]}
        )
        time.sleep(0.3)
        delivery = [row for row in WEBHOOKS if row["_path"] == "/delivery"]
        self.assertEqual(len(delivery), 1)
        self.assertGreaterEqual(delivery[0]["dwellSec"], 8)
        self.assertFalse(delivery[0]["failure"])

    def test_delivery_waits_until_pickup(self) -> None:
        code, _ = self._req(
            "POST",
            "/jobs",
            {"jobId": "job-order", "robot": "servebot-1", "room": "room-1204"},
        )
        self.assertEqual(code, 201)
        placed = {
            "name": "servebot-1",
            "pose": [-0.38, -0.68, 0.1, 0],
            "battery": 1.0,
            "event": "delivery",
            "carried": ["honey jar"],
        }
        self.bridge.telemetry(placed)
        time.sleep(8.2)
        self.bridge.telemetry(placed)
        time.sleep(0.3)
        self.assertEqual(WEBHOOKS, [])

        self.bridge.telemetry(
            {
                "name": "servebot-1",
                "pose": [1.72, 0.69, 0.1, 0],
                "battery": 1.0,
                "event": "pickup",
                "carried": ["honey jar"],
            }
        )
        time.sleep(0.3)
        self.assertEqual([row["_path"] for row in WEBHOOKS], ["/pickup"])
        self.bridge.telemetry(placed)
        time.sleep(8.2)
        self.bridge.telemetry(placed)
        time.sleep(0.3)
        self.assertEqual([row["_path"] for row in WEBHOOKS], ["/pickup", "/delivery"])

    def test_cancel_and_suspend(self) -> None:
        self._req("POST", "/jobs", {"jobId": "job-2", "robot": "servebot-1", "room": "room-1204"})
        code, body = self._req("POST", "/jobs/job-2/cancel")
        self.assertEqual(body["status"], "cancelled")
        self._req("POST", "/fleet/servebot-1/suspend")
        code, body = self._req("POST", "/jobs", {"jobId": "job-3", "robot": "servebot-1", "room": "room-1204"})
        self.assertEqual(code, 409)
        self._req("POST", "/fleet/servebot-1/resume")
        code, _ = self._req("POST", "/jobs", {"jobId": "job-4", "robot": "servebot-1", "room": "room-1204"})
        self.assertEqual(code, 201)


if __name__ == "__main__":
    unittest.main()
