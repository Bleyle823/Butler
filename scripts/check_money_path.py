"""Report which money-path secrets are present. Never prints secret values."""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV_PATH = Path(r"C:\Users\Omen\Desktop\keeperhub-staging\.env")
USDC = 6_000_000


def read_env(path: Path) -> dict[str, str]:
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
        values[name.strip()] = raw.strip().strip('"')
    return values


def main() -> int:
    env = read_env(ENV_PATH)
    needed = [
        "CIRCLE_API_KEY",
        "CIRCLE_ENTITY_SECRET",
        "CIRCLE_ENV",
        "TURNKEY_ORGANIZATION_ID",
        "TURNKEY_API_PUBLIC_KEY",
        "TURNKEY_API_PRIVATE_KEY",
    ]
    missing = [name for name in needed if not env.get(name)]
    print("split operator", USDC * 80 // 100)
    print("split manufacturer", USDC * 10 // 100)
    print("split reserve", USDC - (USDC * 80 // 100) - (USDC * 10 // 100))
    for name in needed:
        print(f"{name} {'set' if env.get(name) else 'missing'}")

    api_key = env.get("CIRCLE_API_KEY") or ""
    circle_env = (env.get("CIRCLE_ENV") or env.get("CIRCLE_ENVIRONMENT") or "sandbox").lower()
    host = "https://api.circle.com" if circle_env == "production" else "https://api-sandbox.circle.com"
    if api_key:
        request = urllib.request.Request(
            host + "/v1/w3s/wallets",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "butler-check/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                payload = json.loads(response.read().decode("utf-8"))
            count = len((payload.get("data") or {}).get("wallets") or [])
            print(f"circle wallets list {response.status} count {count}")
        except urllib.error.HTTPError as error:
            print(f"circle wallets list HTTP {error.code}")
        except urllib.error.URLError as error:
            print(f"circle wallets list unreachable {error.reason}")
    else:
        print("circle wallets list skipped")

    if missing:
        print("blocked " + ", ".join(missing))
        print("deposit, release, and peaq record-revenue stay blocked until those are set")
        return 2
    print("ready for provision and activate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
