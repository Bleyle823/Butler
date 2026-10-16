# Butler — Project Details (Notion source)

> Synced content for [Project Details](https://www.notion.so/Project-Details-3fbe6f3c0667802ca6e1f4060b445d87). Full investor narrative: `docs/Butler_Investor_Pitch.md`.

## Executive summary

**Butler** is a pay-per-skill hospitality robot: **servebot-1** runs kitchen delivery in a **Webots** hotel simulation; **Circle** holds **USDC** in escrow on **Arc**; **peaq** records identity and proof of pickup/delivery. The guest pays when the work is proved—not when someone raises an invoice.

- **Programme:** [Tameion Agents Hackathon](https://tameion.thecanteenapp.com/) (Canteen × Circle)
- **Builder:** Bleyle Osewe · Bennybleylle09@gmail.com · 0705297628
- **Community:** [Web3 Clubs Kenya](https://web3clubs.xyz) (lab + robotics space for post-hackathon pilot)
- **Repo:** Butler monorepo (Webots world + settler + bridge + hotel-ui + landing)

---

## What Butler is

A hotel service robot with a financial layer:

1. Guest orders the fixed demo bundle (heineken beer, beverage can, water bottle) via **hotel-ui** or Play in Webots.
2. **Settler** locks **6.00 USDC** (Circle / Arc Testnet) before the robot moves.
3. **servebot-1** picks up at the kitchen; vending is paid from the robot wallet on pickup proof.
4. On delivery proof, escrow releases to operator, manufacturer, and robot reserve.
5. **peaq mainnet** records the job against **servebot-1**’s machine id.

**Principle:** The robot that gets paid when the work is done.

---

## Why it matters (Kenya hospitality)

| Metric | Figure |
|--------|--------|
| Tourism earnings (2025) | ~KSh 0.5 trillion |
| Accredited hotels | 900+ |
| Hotel rooms | 45,000+ |
| Travel & tourism jobs | ~1.8 million |

Tourism CS **Rebecca Miano** (Feb 2026, World Governments Summit) framed AI in tourism as directing value to people who do the work—with less leakage. Butler is a small, demonstrable version of that idea.

---

## Tameion / Circle agent alignment

Hackathon theme: an **AI agent** runs the money—hold USDC, pay obligations, stay within policy, log decisions, escalate only on threshold.

| Requirement | Butler |
|-------------|--------|
| Hold USDC | Circle dev-controlled wallets; settler custody |
| Pay vendors | Kitchen/vending on pickup |
| Policy limits | Escrow only releases on delivery; failure blocks next order |
| Decision log | peaq events + Circle/Arc transfers |
| Human escalation | Payment/settlement errors surface to operator |

---

## Why Arc (network opportunity)

[Arc](https://www.arc.io/) is Circle’s stablecoin-native L1 (USDC gas, sub-second finality, agentic commerce). Butler is **repeatable settlement volume**, not a one-off demo:

- Each delivery ≈ **3+ USDC movements** (lock, kitchen pay, release/split).
- Aligns with **agentic economy** (job escrow, verify, settle) and **physical AI** settlement—not only API x402 micropayments.
- Illustrative scale: Web3 Clubs pilot **50 deliveries/week → 150+ settlement events**; multi-hotel fleets multiply tx count and USDC velocity on Arc.

Public network activity (explorer-indexed): tens of millions of transactions per month on Arc mainnet since launch; Butler targets **high-frequency, small-dollar machine commerce** in hospitality.

---

## Physical AI context

Embodied / physical AI = perceive, reason, act in the real world. Hospitality **delivery robots** are among the most deployed service-robot categories (~40% of hospitality robot revenue in industry analyses). Operators succeed on **high-frequency, repetitive** tasks (room delivery)—the same wedge Butler models.

**peaqOS + LG CLOiSim (2026):** simulated hotel, fleet dispatch, pay-per-skill settlement—same story arc as Butler, different hardware (TIAGo in Webots today).

---

## Architecture

```
Guest UI (apps/hotel-ui :3001)  →  Landing (apps/landing :3002)
         ↓ POST /api/order
Settler (packages/settler :8788)  →  Circle + peaq-os-sdk (Python 3.10+)
         ↓ paid goal
Bridge (packages/bridge :8787)  ←  butler_observe (telemetry)
         ↓
Webots: mission_control on servebot-1 (TIAGo, kitchen.wbt)
```

**Security rules (see AGENTS.md):**

- Robot never holds Circle entity secret or peaq controller key.
- Only settler writes peaq and holds Circle secrets.
- Webots controller is Python 3.9; peaq SDK runs in settler only.

---

## servebot-1 & onchain identity

| Item | Value |
|------|--------|
| Robot | PAL TIAGo, `servebot-1`, controller `mission_control` |
| World | `worlds/kitchen.wbt` — rooms **1204, 1205, 1206** (who ordered; robot does not enter rooms) |
| peaq chain | Mainnet **3338**, Economics 2.0 |
| Machine page | https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819 |
| Controller | `0x4360d54AdB797bf75013870de1AAD152839587D0` |

---

## Money (Arc Testnet 5042002)

| Role | Address |
|------|---------|
| USDC | `0x3600000000000000000000000000000000000000` |
| Escrow | `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` |
| Explorer | https://testnet.arcscan.app |

Guest locks **6.00 USDC**; pickup pays vending **2.00** from robot wallet; delivery releases split (operator / manufacturer / robot reserve). See README for wallet roles and example job hashes.

---

## What’s live vs in progress

| Item | Status |
|------|--------|
| servebot-1 on peaq | Live |
| Pickup / delivery on peaq | Recorded |
| Vending payment on Arc | Cleared (example tx in README) |
| hotel-ui + landing styled | Running |
| Full guest lock → release on Arc testnet | In progress |

---

## Roadmap

**Phase 0 — Hackathon:** End-to-end demo + public proof (tx hashes, machine page).

**Phase 1 — Pilot (Web3 Clubs lab):** Physical hardware in robotics space; hotel manager demos; 60-day willing-hotel pilot.

**Phase 2 — Product:** 2–3 Nairobi hotels; pay-per-skill pricing; fleet settler.

**Phase 3 — Scale:** East Africa hospitality → other embodied-AI venues (warehouses, healthcare, airports).

---

## Team & support

**Bleyle Osewe** — BBIT 2024, Africa Nazarene University; Web3 Clubs Kenya.

- **NIRU National AI Hackathon** — podium / award, Maritime Anomaly System (physical AI drone).
- **Mashariki Cooperation Conference (Apr 2026)** — presented to President Ruto, CS Murkomen, DG NIS.
- **ETH Safari** — hackathon prizes including **MetaMask prize**; active GitHub shipping record.

**Institutional (in progress):**

- **NI3C**, Ministry of Education, Kenya — discussions with Head of Centre; prior **internship at NI3C** (strong fit for innovation support; timelines are government-paced).
- **ANU** — Head of Department, Education — exploring capstone / partnership support.

**Web3 Clubs Kenya** — letter of recognition for Tameion; lab + robotics space for pilot; copy **arjun@thecanteenapp.com** on official club correspondence.

---

## Media & placeholders

- [ ] Cover: robot in hotel corridor + tx hash overlay
- [ ] hotel-ui order screen
- [ ] Simulation pickup / delivery screenshots
- [ ] NIRU stage + Mashariki photos
- [ ] Web3 Clubs lab / robotics space
- [ ] Robot hardware spec sheet (pilot)

Video: `proposals/videos/one-delivery-order-to-table.mp4` (see GitHub README).

---

## Run locally

Full operator steps: **`docs/RUN.md`**

Quick ports:

| Service | URL |
|---------|-----|
| Settler | http://127.0.0.1:8788 |
| Bridge | http://127.0.0.1:8787 |
| hotel-ui | http://localhost:3001 |
| landing | http://localhost:3002 |

---

## Links

- Tameion: https://tameion.thecanteenapp.com/
- Canteen: https://thecanteenapp.com/about/
- peaq Economics 2.0: https://docs.peaq.xyz/peaqos/concepts/economics-2-0
- Circle dev wallets: https://developers.circle.com/wallets/dev-controlled
- Arc docs: https://docs.arc.io/
- Arc testnet faucet: https://faucet.circle.com
- Web3 Clubs: https://web3clubs.xyz · X: @Web3Clubs

---

*Last updated: October 2026*
