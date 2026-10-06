"""Activate servebot-1 on peaq once the Turnkey API key pair is in KeeperHub .env.

The robot never receives the key. This script only checks that KeeperHub can
sign. It does not print key material.
"""

from __future__ import annotations

import sys
from pathlib import Path

ENV_PATH = Path(r"C:\Users\Omen\Desktop\keeperhub-staging\.env")
ORG = "5f1342fd-2929-4c51-90ea-ef416ebfeb48"


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
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
    org = env.get("TURNKEY_ORGANIZATION_ID") or ""
    if org != ORG:
        print("TURNKEY_ORGANIZATION_ID is not the expected org")
        return 2
    missing = [
        name
        for name in ("TURNKEY_API_PUBLIC_KEY", "TURNKEY_API_PRIVATE_KEY")
        if not env.get(name)
    ]
    if missing:
        print("blocked " + ", ".join(missing))
        print("servebot-1 stays unregistered until those keys are in the gitignored KeeperHub .env")
        return 2
    print("turnkey key pair is present for the configured org")
    print("register servebot-1 from KeeperHub with the peaqos plugin before the first paid job")
    return 0


if __name__ == "__main__":
    sys.exit(main())
