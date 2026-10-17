# Butler — Manual run guide

Use this guide to run a full demo: guest order → robot delivery in Webots → USDC on Arc testnet → public record for **servebot-1** on peaq.

**Rules**

- Run **one paid order at a time**. Wait until the Webots console shows the job is **done** before starting another.
- Start the **payment service** and **coordinator** before pressing Play in Webots.
- Secret files (API keys, wallets) never go in git. Do not paste them in chat.

**Related docs**

- Deep checklist with curl tests: [`RUN.md`](RUN.md)
- First-time install (Webots download, clone): [`README.md`](../README.md#step-by-step-run-butler-locally)

---

## What you will run

| What | Where | What it does |
|------|--------|----------------|
| **Settler** | http://127.0.0.1:8788 | Holds payment keys; locks and releases USDC; writes peaq records |
| **Bridge** | http://127.0.0.1:8787 | Remembers the paid order; connects robot “proof” to the settler |
| **hotel-ui** (optional) | http://localhost:3001 | Guest order page |
| **landing** (optional) | http://localhost:3002 | Marketing site |
| **Webots** | `worlds/kitchen.wbt` | Hotel kitchen + **servebot-1** |

**Demo order:** heineken beer, beverage can, water bottle · **6.00 USDC** · room **1204**, **1205**, or **1206** (who ordered; the robot does not enter guest rooms).

---

## Part A — One-time setup

### A1. Install software

1. **Webots R2025a** — [cyberbotics.com/download](https://cyberbotics.com/#download)
2. **Node.js** 20+ and **pnpm** — for hotel-ui / landing
3. **uv** and **Python 3.12** — for the settler only (Webots uses its own older Python)
4. **Circle** developer account — API key and entity secret (for real test payments)
5. **Arc testnet USDC** — [faucet.circle.com](https://faucet.circle.com) for guest and robot wallets

### A2. Clone the project

```bash
git clone https://github.com/Bleyle823/Butler.git
cd Butler
```

(Use your fork URL if different.)

### A3. Create local config files

Copy examples and fill in your values. All paths are from the **Butler** folder (repo root).

| File | Copy from |
|------|-----------|
| `.env` | `.env.example` |
| `config/wallets.json` | `config/wallets.example.json` |
| `config/bridge.json` | `config/bridge.example.json` |
| `apps/hotel-ui/.env.local` | `apps/hotel-ui/.env.example` |

In `config/bridge.json`, set `wallets_path` to `config/wallets.json` (not the `.example` file).

`config/peaqos_wallets.json` is created when you first run the settler (or import a controller key once via `PEAQ_CONTROLLER_PRIVATE_KEY` in `.env` — see [`RUN.md`](RUN.md) Stage 0).

**Windows — check all files exist:**

```powershell
cd C:\Users\Omen\Desktop\Butler   # your path
Test-Path .env, config\wallets.json, config\peaqos_wallets.json, config\bridge.json, apps\hotel-ui\.env.local
```

Every line should be `True` before you expect payments to work.

### A4. Fund test wallets (before each demo day)

Each order needs headroom on Arc testnet (USDC is also used for fees):

| Wallet role | Rough minimum |
|-------------|----------------|
| Guest | ~**6.20** USDC (6.00 order + fees) |
| Robot | ~**2.20** USDC (2.00 to kitchen on pickup + fees) |
| Settler | Enough for one contract call |

Refill from the **operator** wallet or the Circle faucet. Wallet addresses are in [`README.md`](../README.md#the-money-arc-testnet).

### A5. Install settler dependencies (once per machine)

From repo root:

**Windows:**

```powershell
uv venv --python 3.12 packages\settler\.venv
uv pip install --python packages\settler\.venv\Scripts\python.exe -r packages\settler\requirements.txt
```

**macOS / Linux:**

```bash
uv venv --python 3.12 packages/settler/.venv
uv pip install --python packages/settler/.venv/bin/python -r packages/settler/requirements.txt
```

**hotel-ui / landing (once):**

```bash
cd apps/hotel-ui && pnpm install && cd ../..
cd apps/landing && pnpm install && cd ../..
```

---

## Part B — Every demo session (start services)

Open **four terminals** (or three if you skip the guest page). Leave each running.

### B1. Terminal 1 — Settler

**Windows (repo root):**

```powershell
packages\settler\.venv\Scripts\python.exe packages\settler\run_settler.py
```

**macOS / Linux:**

```bash
packages/settler/.venv/bin/python packages/settler/run_settler.py
```

**You should see:** a line like `butler settler http://127.0.0.1:8788`

**Quick check:** open http://127.0.0.1:8788/health in a browser or run `curl http://127.0.0.1:8788/health` → `{"ok": true}`

### B2. Terminal 2 — Bridge

```bash
cd packages/bridge
python run_bridge.py
```

Leave it running. If you change `config/wallets.json`, restart this process.

### B3. Terminal 3 — Guest order page (optional)

```bash
cd apps/hotel-ui
pnpm dev
```

Open **http://localhost:3001**. You should see the three drinks and room dropdown.

### B4. Terminal 4 — Landing (optional)

```bash
cd apps/landing
pnpm dev
```

Open **http://localhost:3002** if you want the marketing site.

---

## Part C — Webots (kitchen world)

1. Open **Webots R2025a**.
2. **File → Open World** → `Butler/worlds/kitchen.wbt`
3. In the scene tree, click **servebot-1** and confirm:
   - **controller** = `mission_control`
   - **supervisor** = checked
4. Confirm drinks on the kitchen counter and the robot standing in the kitchen.
5. Use **real-time** speed (avoid fast mode if the robot looked unstable before).
6. If the robot was broken or flying from a bad run: reload the world file, then continue.
7. Leave the simulation **paused** until B1 and B2 are running.

---

## Part D — Run the demo (two ways)

### Way 1 — Simulation only (Play creates the order)

1. Confirm settler + bridge are up (Part B).
2. In Webots, press **Play**.
3. Watch the **Webots console** and the **settler terminal**.

**Good signs:**

- `Play: posting order 0x…` (if no order existed yet)
- `locking 6.00 USDC for room-1204`
- `paid goal is on the bridge`
- Robot starts moving; later `Circle vending 2.00` and `peaq pickup revenue …`
- After the beer is on the table (and a short wait), `Circle release` and `peaq delivery revenue …`
- Run ends with **DONE**

Do **not** press Play again mid-run.

### Way 2 — Guest page first (recommended for audiences)

1. Confirm settler + bridge are up; hotel-ui on port 3001 (Part B3).
2. On http://localhost:3001, choose a room and click **Order the drinks**.
3. Success message should include a job id like `Order sent. Job 0x…`
4. In Webots, press **Play**.
5. Console should say **`using paid goal`** (not a second order).
6. Watch the same payment and robot lines as Way 1.

---

## Part E — What a complete run looks like

| Step | What happens |
|------|----------------|
| 1 | **6.00 USDC** locked from the guest (escrow) |
| 2 | Robot picks up heineken → **2.00 USDC** to kitchen/vending |
| 3 | peaq records **pickup** for servebot-1 |
| 4 | Beer on table → escrow **releases** (operator / maker / robot reserve) |
| 5 | peaq records **delivery** |
| 6 | Robot places can and water (same job, no second charge) |
| 7 | **DONE** — safe to start a new order |

**Public checks**

- Machine: [servebot-1 on peaq](https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819)
- Arc testnet: [testnet.arcscan.app](https://testnet.arcscan.app)
- peaq txs: [peaq.subscan.io](https://peaq.subscan.io)

For step-by-step curl verification, use [`RUN.md`](RUN.md) Stages 5–8.

---

## Part F — Stop and reset

1. Stop Webots (pause or close).
2. Ctrl+C in settler, bridge, and UI terminals.
3. If starting a **new** order after a finished run, reload `kitchen.wbt` if the scene looks wrong.
4. Do not reuse a **job id** that already settled end-to-end.

---

## Part G — Common problems

| What you see | What to try |
|--------------|-------------|
| Settler won’t start | Use Python **3.12** venv under `packages/settler/.venv`, not system 3.9 |
| http://127.0.0.1:8788/health fails | Start settler; check nothing else uses port 8788 |
| Order page “can’t reach hotel service” / 503 | Settler not running |
| Order page error / 502 | Read settler terminal — often guest wallet low on test USDC or bridge down |
| `order failed` in Webots | Same as above; guest needs ~6.20 USDC on testnet |
| Robot doesn’t move | **servebot-1** controller must be `mission_control`, supervisor on |
| `bridge post failed` in Webots | Start bridge; reload `kitchen.wbt` |
| Pickup pays but no peaq line | Check `config/peaqos_wallets.json` / controller key ([`RUN.md`](RUN.md)) |
| Release never happens | Wait for beer on table ~8 seconds after delivery proof; pickup must have run first |
| Robot exploded / flying | Reload world; use real-time; Play once |

Full failure table: [`RUN.md`](RUN.md#if-a-stage-fails).

---

## Part H — Demo script (60 seconds, for a room)

1. “This is a hotel kitchen in simulation. **servebot-1** delivers a fixed drink order.”
2. Open hotel-ui → choose room → **Order the drinks**. “Guest money is **held** until delivery is proved.”
3. Play Webots. “Robot runs; kitchen gets **2 dollars** when pickup is detected; guest **6 dollars** release when delivery is detected.”
4. Show settler lines or explorers: “**Arc** moved USDC; **peaq** shows which robot did the job.”
5. Open machine page on peaq. “Same idea as pay-per-skill hotel demos—here built for Kenya / Tameion.”

---

*Butler · Manual run guide · October 2026*
