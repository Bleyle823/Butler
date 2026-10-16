# Butler

**The robot that gets paid when the work is done.**

Physical AI hospitality demo for the **[Tameion Agents Hackathon](https://tameion.thecanteenapp.com/)** (Canteen × Circle): a **TIAGo** humanoid (**servebot-1**) runs kitchen delivery in **Webots**; **Circle** holds **USDC** in escrow on **Arc**; **peaq** records machine identity and proof of work.

| | |
|---|---|
| **Builder** | Bleyle Osewe · [Bennybleylle09@gmail.com](mailto:Bennybleylle09@gmail.com) · 0705297628 |
| **Community** | [Web3 Clubs Kenya](https://web3clubs.xyz) |
| **Notion** | [Project Details](https://www.notion.so/Project-Details-3fbe6f3c0667802ca6e1f4060b445d87) |
| **Long-form pitch** | [`docs/Butler_Investor_Pitch.md`](docs/Butler_Investor_Pitch.md) |

---

## One-minute story

A guest orders drinks. **6.00 USDC** locks on **Arc Testnet** before the robot moves. **servebot-1** picks up at the kitchen; the vending counter is paid from the robot’s Circle wallet on **pickup**. When telemetry shows delivery, escrow **releases** to operator, manufacturer, and robot reserve. **peaq mainnet** logs pickup and delivery against **servebot-1**’s machine id.

No front desk. No invoice. Dollars move because the work happened—and anyone can verify it.

---

## Video

<video src="proposals/videos/one-delivery-order-to-table.mp4" controls width="100%"></video>

_One simulated delivery run (5×). Source: TIAGo object manipulation demo._

---

## Screenshots

_Add paths as you capture them._

| | |
|---|---|
| Kitchen world | _placeholder_ |
| servebot-1 at counter | _placeholder_ |
| Order on kitchen table | _placeholder_ |
| Webots console (Circle + peaq lines) | _placeholder_ |
| [hotel-ui](apps/hotel-ui) order screen | _placeholder_ |

---

## Why Butler (problem)

- **Guest:** Hard to see that delivery happened and that payment matched the job.
- **Hotel:** Manual trails between kitchen, room, and staff.
- **Robot / RaaS:** Flat leases hide premium skills; pay-per-task is hard to enforce.
- **Kenya hospitality:** ~KSh 0.5T tourism earnings (2025), 900+ accredited hotels, 45k+ rooms, ~1.8M travel/tourism jobs—a high-frequency delivery environment with mostly manual settlement.

---

## Tameion / Circle agent fit

The hackathon asks for an agent that **runs the money**: hold USDC, pay obligations inside policy, log decisions, escalate on threshold.

| Requirement | Butler |
|-------------|--------|
| Agent wallet | Circle dev-controlled wallets; **settler** custody |
| Budgets / policy | Escrow release only on delivery; kitchen pay on pickup; failed payment blocks next order |
| Liquidity | Settler checks state before accepting jobs |
| Decision log | peaq events + Circle/Arc transfers |
| Human escalation | Operator alerted on settlement failure |

---

## Why Arc

[Arc](https://www.arc.io/) is Circle’s stablecoin-native L1 (USDC gas, fast finality, **agentic commerce**). Butler is built for **repeatable settlement volume**:

- **3+ USDC movements per delivery** (lock → kitchen → release/split).
- Extends agent payments from APIs to **telemetry-verified physical work**.
- Scales with fleet size (many small settlements vs. one-off transfers).

Arc mainnet has processed **tens of millions of transactions per month** since launch (explorer-indexed). Butler is a reference path for **machine commerce on Arc** in hospitality.

---

## Physical AI & pay-per-skill

**Physical AI** = systems that perceive, reason, and act in the world (not chat-only). Hospitality **delivery robots** are a leading service-robot category. **peaqOS** in **LG CLOiSim** (2026) showed pay-per-skill hotel room service with onchain settlement; Butler uses the same idea—**peaq identity + Circle/Arc money**—on **TIAGo / Webots** in Kenya.

---

## What shipped

- **servebot-1** — PAL TIAGo in Webots R2025a (`worlds/kitchen.wbt`)
- **Circle** developer-controlled wallets + Foundry escrow on **Arc Testnet `5042002`**
- **peaq** Economics 2.0 machine on **peaq mainnet `3338`**
- **Settler** (`packages/settler`) — Circle secret + `peaq-os-sdk` (Python 3.10+), same split as peaq’s `peaqos_node` pattern
- **Bridge** (`packages/bridge`) + **butler_observe** telemetry
- **Guest UI** [`apps/hotel-ui`](apps/hotel-ui) (port **3001**) · **Landing** [`apps/landing`](apps/landing) (port **3002**)
- Settlement gated on **pickup** and **delivery** proof

Operator runbook: **[`docs/RUN.md`](docs/RUN.md)** · Architecture rules: **[`AGENTS.md`](AGENTS.md)**

---

## Architecture

```
apps/hotel-ui (:3001)  ──POST /api/order──▶  packages/settler (:8788)
       │                                        ├── Circle (USDC, Arc)
       │                                        └── peaq mainnet (events)
       │
apps/landing (:3002) ──links to hotel-ui

Webots: mission_control (servebot-1)
         butler_observe ──▶ packages/bridge (:8787) ──▶ settler
```

**Rules:**

1. Webots controller Python is **3.9**; `peaq-os-sdk` needs **3.10+** → SDK only in **settler**.
2. Robot never holds Circle entity secret or peaq controller key.
3. peaq does not talk to Webots; only the settler writes peaq.

---

## The robot

| | |
|---|---|
| Name | `servebot-1` |
| Platform | PAL TIAGo, 7-DOF arm + gripper |
| Controller | `mission_control` (drink behavior tree) |
| Observer | `butler_observe` (pose, pickup, delivery → bridge) |
| Guest rooms | **1204, 1205, 1206** (who ordered; robot does not drive into rooms) |
| Demo order | heineken beer, beverage can, water bottle (**6.00 USDC**) |

Press **Play** posts `/order` to the settler if no paid goal exists; hotel-ui can order first.

---

## The machine (peaq)

| | |
|---|---|
| Network | peaq mainnet, chain `3338`, Economics 2.0 |
| Decimal id | `63056357364750406110742192000069244844268702226710579694851149582072404420819` |
| Bytes32 | `0x8b68a22dc5d3c9c64f444db3928d7ee5907c829a8e4419dbcc04d1103c9aa8d3` |
| Controller | `0x4360d54AdB797bf75013870de1AAD152839587D0` |
| EventRegistry | `0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e` |
| Activation | `0x406ed5c4f889cb9cd0c9aa940223f3144ddeb2a16b3f95c55bb8a8a7ce443e6c` |
| Explorer | [machines.peaq.xyz](https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819) |
| DID image | https://files.catbox.moe/ec4zej.png |

---

## The money (Arc Testnet)

| | |
|---|---|
| Chain | Arc Testnet **`5042002`** · [testnet.arcscan.app](https://testnet.arcscan.app) |
| USDC | `0x3600000000000000000000000000000000000000` |
| Escrow | `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` |

| Role | Address |
|------|---------|
| Guest | `0x566c7344100b046e467eae9d1efb8bd5abf646a2` |
| Robot | `0x9a8709845445661fd9b044bc907e38faf6d27168` |
| Vending | `0x01ed2f186edab0b28dd796afe0762fac5a5b092d` |
| Operator | `0x0fa08f931a9d4430f614ab5c49f095bf0ae2240d` |
| Manufacturer | `0xC26ce44fC41BB13503d20945653767abcbd17f7E` |
| Settler | `0x2838270efa7a1aa0196bb98a8f8230771aed3b80` |

**Flow:** Guest locks **6.00 USDC**. Heineken pickup → vending **2.00** from robot wallet. Delivery → escrow **4.80 / 0.60 / 0.60** (operator / manufacturer / robot reserve). peaq records **200** cents on pickup, **600** on delivery for that bottle leg; can and water complete the same job.

On Arc Testnet, **gas and USDC share one token**; leave headroom above exact transfer amounts ([`docs/RUN.md`](docs/RUN.md)). Faucet: https://faucet.circle.com

---

## Example run (on record)

Job `0xdccdc144afa9ac17fdc72e44127b2e788734b3b38740f5b3d1ae7d347b77ff46`.

| Step | Circle id | Arc |
| --- | --- | --- |
| Deposit 6.00 | `f150bf2e-53e4-5c01-ba07-4476f92ad54d` | No Arc hash. Circle state `FAILED` (`INSUFFICIENT_TOKEN`). |
| Vending 2.00 | `82652451-d1a6-5bc3-81fb-30903cf5f92e` | [0x5130…8ed43](https://testnet.arcscan.app/tx/0x513091d549e7aac239a502781b73400e5d183f1dd78921ede314c60f6308ed43) |
| Release | `4f4753ee-ee8c-5134-8d15-930c1afb1e70` | No Arc hash. Circle state `FAILED` (`ESTIMATION_ERROR`). |

**peaq pickup:** [0x7131…f21a](https://peaq.subscan.io/tx/0x7131f9366ff7c0516c8b8c911cf74090a6bb7ae7e1c5b296a433d537f434f21a)

**peaq delivery:** [0x629c…23d0](https://peaq.subscan.io/tx/0x629c774c2d85a390e4fcf2b4889582ec2d37ecdd7934d2c34f31043537e923d0)

---

## Step-by-step: run Butler locally

This guide is for someone cloning the repo for the first time. You will run **four background services** (settler, bridge, optional UIs) and then **Webots** with the kitchen world.

**End-to-end payment checklist (stages, curl checks, failure table):** [`docs/RUN.md`](docs/RUN.md)

### What you are running

| Piece | Port | Role |
|-------|------|------|
| Settler | `8788` | Circle USDC + peaq writes; holds secrets |
| Bridge | `8787` | Paid goal + robot telemetry |
| hotel-ui | `3001` | Guest “Order the drinks” page |
| landing | `3002` | Marketing site (optional) |
| Webots | — | Simulation: `servebot-1` + `butler_observe` |

One paid job at a time. Wait until the robot finishes (`DONE` in the Webots console) before starting another order.

---

### Step 1 — Install tools

| Tool | Version | Why |
|------|---------|-----|
| [Webots](https://cyberbotics.com/#download) | **R2025a** | Kitchen world and TIAGo controllers (bundled Python **3.9**) |
| [Git](https://git-scm.com/downloads) | any recent | Clone the repo |
| [Node.js](https://nodejs.org/) | 20+ LTS | hotel-ui / landing |
| [pnpm](https://pnpm.io/installation) | 9+ | Front-end apps |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest | Settler venv (Python **3.12**; `peaq-os-sdk` needs 3.10+) |
| Python **3.12** | 3.12.x | Used only inside `packages/settler/.venv` |

**Circle / Arc (for real settlement):** Circle developer account, API key, entity secret, Arc Testnet USDC from [faucet.circle.com](https://faucet.circle.com). Without these you can still explore Webots motion, but deposits and releases will fail.

---

### Step 2 — Download and install Webots

1. Open **[cyberbotics.com → Download](https://cyberbotics.com/#download)**.
2. Choose **Webots R2025a** for your OS (Windows, macOS, or Linux).
3. Run the installer and complete the setup wizard.
4. Launch Webots once so it can finish first-time setup (controllers cache, etc.).

**Open this project in Webots**

1. Clone Butler (Step 3) if you have not already.
2. In Webots: **File → Open World** → select  
   `Butler/worlds/kitchen.wbt`  
   (or open the whole repo folder as a Webots project; the world file is the entry point.)
3. In the scene tree, select robot **`servebot-1`** and confirm:
   - **controller** = `mission_control`
   - **supervisor** = enabled (checked)
4. Leave a second robot **`butler_observe`** in the world; do not change its controller.

**Tips**

- Use **real-time** simulation mode before pressing Play (not fast mode if the robot pose looks unstable).
- If another Webots instance is open, port **1234** may be busy; close extra instances or see [`docs/RUN.md`](docs/RUN.md) for alternate ports.
- If the TIAGo pose looks broken after a bad run, **reload** `kitchen.wbt` before Play.

---

### Step 3 — Clone the repository

```bash
git clone <your-butler-repo-url>
cd Butler
```

On Windows, a typical path is `C:\Users\<you>\Desktop\Butler`. All commands below assume your shell is at the **repo root** (`Butler/`).

---

### Step 4 — Configure secrets (not in git)

Copy example files and fill in values **locally**. Never commit these files.

| File | Create from | Purpose |
|------|-------------|---------|
| `.env` | [`.env.example`](.env.example) | `CIRCLE_API_KEY`, `CIRCLE_ENTITY_SECRET`, `BUTLER_SECRET`, settler bind |
| `config/wallets.json` | [`config/wallets.example.json`](config/wallets.example.json) | Circle wallet IDs + Arc addresses for guest, robot, vending, etc. |
| `config/bridge.json` | [`config/bridge.example.json`](config/bridge.example.json) | Bridge port `8787`, settler pickup/delivery URLs, `wallets_path` → `config/wallets.json` |
| `config/peaqos_wallets.json` | _(created by settler)_ | peaq controller key registry |
| `apps/hotel-ui/.env.local` | [`apps/hotel-ui/.env.example`](apps/hotel-ui/.env.example) | `BUTLER_SETTLER_URL`, `PEAQ_MACHINE_ID`, `BUTLER_SECRET` |

**`.env` (repo root)** — minimum keys:

```env
CIRCLE_API_KEY=...
CIRCLE_ENTITY_SECRET=...
CIRCLE_ENV=production
BUTLER_SECRET=change-me
SETTLER_HOST=127.0.0.1
SETTLER_PORT=8788
```

Optional one-time import: `PEAQ_CONTROLLER_PRIVATE_KEY=` → start settler once; it writes `config/peaqos_wallets.json`; then clear the env var.

**`config/bridge.json`** — point `wallets_path` at your real `config/wallets.json` (not the `.example` file).

**Verify files exist (Windows PowerShell):**

```powershell
Test-Path .env, config\wallets.json, config\peaqos_wallets.json, config\bridge.json, apps\hotel-ui\.env.local
```

All should return `True` before you expect Circle/peaq settlement to work.

---

### Step 5 — Start the settler (terminal 1)

The settler must use **Python 3.12** in its own venv (Webots uses 3.9).

**Windows (PowerShell, repo root):**

```powershell
uv venv --python 3.12 packages\settler\.venv
uv pip install --python packages\settler\.venv\Scripts\python.exe -r packages\settler\requirements.txt
packages\settler\.venv\Scripts\python.exe packages\settler\run_settler.py
```

**macOS / Linux:**

```bash
uv venv --python 3.12 packages/settler/.venv
uv pip install --python packages/settler/.venv/bin/python -r packages/settler/requirements.txt
packages/settler/.venv/bin/python packages/settler/run_settler.py
```

**Pass:** console shows the settler listening on `http://127.0.0.1:8788`.

```bash
curl http://127.0.0.1:8788/health
# {"ok": true}
```

Leave this terminal open.

---

### Step 6 — Start the bridge (terminal 2)

Uses system `python` (3.9+ is fine for the bridge).

```bash
cd packages/bridge
python run_bridge.py
```

**Pass:** process stays running on port **8787**. (`GET /health` may 404; that is normal.)

```bash
curl -H "X-Butler-Secret: change-me" http://127.0.0.1:8787/fleet
curl http://127.0.0.1:8787/robots/servebot-1/goal
```

Goal is `{}` until an order exists. Restart the bridge if you edit `config/wallets.json`.

---

### Step 7 — Start the guest UI (terminal 3, optional)

```bash
cd apps/hotel-ui
pnpm install
pnpm dev
```

Open **http://localhost:3001** — rooms **1204 / 1205 / 1206**, fixed drink bundle, **Order the drinks**.

You can skip this step: pressing **Play** in Webots will post the same kitchen order when the bridge has no goal.

**Landing site (optional, terminal 4):**

```bash
cd apps/landing
pnpm install
pnpm dev
```

Open **http://localhost:3002** → **Get started** links to hotel-ui.

---

### Step 8 — Open Webots and confirm the scene

1. Open **`worlds/kitchen.wbt`** in Webots R2025a.
2. Confirm **`servebot-1`** → controller **`mission_control`**, supervisor on.
3. Confirm drinks on the kitchen counter (heineken beer, beverage can, water bottle).
4. Keep the world **paused** until settler + bridge are up.

---

### Step 9 — Run one delivery

**Path A — Webots only**

1. Press **Play** in Webots.
2. Watch the **Webots console** and **settler terminal**.
3. If no order existed, you should see lines like:
   - `[kitchen] Play: posting order 0x…`
   - `[kitchen] locking 6.00 USDC for room-1204`
   - `[kitchen] paid goal is on the bridge`
   - `servebot-1 starting kitchen order …`
4. Let the behavior tree finish (pickup → place on table → remaining items). Wait for **`DONE`** before a new order.

**Path B — Hotel UI first**

1. On http://localhost:3001, choose a room and click **Order the drinks**.
2. Note the job id in the success message.
3. Press **Play** in Webots. The console should say **`using paid goal`** instead of posting a second order.

**What success looks like (full settlement)**

- Arc: guest **6.00 USDC** lock, robot **2.00** to vending on heineken pickup, escrow **release** on delivery.
- peaq: **pickup** and **delivery** revenue events for `servebot-1`.
- Details and curl checks: [`docs/RUN.md`](docs/RUN.md) Stages 5–8.

---

### Step 10 — Quick troubleshooting

| Symptom | Likely fix |
|---------|------------|
| Settler won’t start | Use `packages/settler/.venv` with Python **3.12**, not Webots 3.9 |
| `8788/health` fails | Settler not running or port in use |
| hotel-ui **503** | Settler down or wrong `BUTLER_SETTLER_URL` |
| hotel-ui **502** | Circle deposit failed — check guest balance + [faucet](https://faucet.circle.com) |
| Play: order failed | Guest wallet needs **~6.20 USDC** on Arc Testnet (6.00 + gas headroom) |
| Robot doesn’t move | Controller must be **`mission_control`**, not `mcp_robot` |
| `[butler_observe] bridge post failed` | Start bridge; reload `kitchen.wbt` if physics exploded |
| Goal stays `{}` after deposit | Bridge not running or settler can’t reach `8787` |

---

### Service URLs (bookmark)

| Service | URL |
|---------|-----|
| Settler | http://127.0.0.1:8788 |
| Bridge | http://127.0.0.1:8787 |
| hotel-ui | http://localhost:3001 |
| landing | http://localhost:3002 |
| Arc Testnet explorer | https://testnet.arcscan.app |
| servebot-1 on peaq | [machines.peaq.xyz](https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819) |

---

## Repository layout

| Path | Role |
|------|------|
| `worlds/kitchen.wbt` | Hotel simulation |
| `controllers/mission_control` | Robot behavior + settler client |
| `controllers/butler_observe` | Scene telemetry → bridge |
| `packages/settler` | Circle + peaq settlement agent |
| `packages/bridge` | Local goal + event bus |
| `apps/hotel-ui` | Guest order UI + `/api/order` |
| `apps/landing` | Marketing site → hotel-ui |
| `docs/RUN.md` | End-to-end operator checklist |
| `docs/Butler_Investor_Pitch.md` | Investor / hackathon narrative |
| `docs/NOTION_Project_Details.md` | Notion sync source |

`packages/circle-plugin` and `packages/peaqos-plugin` are reference copies; **KeeperHub is not in the run path.**

---

## Roadmap

| Phase | Goal |
|-------|------|
| **0 — Hackathon** | Full Arc testnet lock → release; public txs + live demo |
| **1 — Pilot** | Web3 Clubs **robotics lab**; physical robot; hotel manager demos |
| **2 — Product** | 2–3 Nairobi hotels; pay-per-skill pricing |
| **3 — Scale** | East Africa hospitality + other embodied-AI venues |

---

## Team & endorsements

**Bleyle Osewe** — BBIT 2024, Africa Nazarene University · Web3 Clubs Kenya

- **NIRU National AI Hackathon** — podium / award, *Maritime Anomaly System* (physical AI drone)
- **3rd Mashariki Cooperation Conference (Apr 2026)** — presented to H.E. President Ruto, CS Murkomen, DG NIS
- **ETH Safari** — hackathon prizes including **MetaMask prize**
- **NI3C** (Ministry of Education) — prior **internship**; ongoing talks with Head of Centre for project support
- **ANU** — discussions with Head of Department, Education

### Web3 Clubs Kenya

Formal recognition for Tameion; lab and **robotics space** for pilot; support beyond hackathon. Programme contact for letters: **arjun@thecanteenapp.com**. [web3clubs.xyz](https://web3clubs.xyz) · @Web3Clubs

_Add partner quotes in this section as they arrive._

---

## Traction (update as you go)

| Metric | Value |
|--------|--------|
| peaq pickup + delivery txs | On chain (see above) |
| Arc vending payment | Confirmed testnet tx |
| Full escrow release | In progress |
| Pilot venue | Web3 Clubs lab (target) |

---

## Security

**Never commit:** `.env`, Circle entity secrets, recovery files, Turnkey keys, webhook secrets, `config/wallets.json`, `config/bridge.json`, `config/peaqos_wallets.json`.

---

## Links

- [Tameion Hackathon](https://tameion.thecanteenapp.com/)
- [peaq Economics 2.0](https://docs.peaq.xyz/peaqos/concepts/economics-2-0)
- [Circle dev-controlled wallets](https://developers.circle.com/wallets/dev-controlled)
- [Arc documentation](https://docs.arc.io/)
- [Arc agentic economy](https://docs.arc.io/build/agentic-economy)
- [Notion — Project Details](https://www.notion.so/Project-Details-3fbe6f3c0667802ca6e1f4060b445d87)

---

## License

_Add license if/when you publish one._
