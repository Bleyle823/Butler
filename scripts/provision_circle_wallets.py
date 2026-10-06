"""Create the eight Circle wallets once CIRCLE_ENTITY_SECRET is set.

Does not print the API key or the entity secret. Wallet ids are written to
config/wallets.json, which is gitignored.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    script = ROOT / "scripts" / "provision_circle_wallets.js"
    completed = subprocess.run(["node", str(script)], check=False)
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
