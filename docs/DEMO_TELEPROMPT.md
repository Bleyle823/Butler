# Butler kitchen demo — teleprompter (full run)

**Recorded run · job `0x59b29…` · October 2026**

Use this as a spoken script while you show hotel-ui, Webots, settler terminal, and explorers.  
**Pause** where marked `[SHOW]`. **Do not rush** the Arc/peaq links—let people read one hash at a time.

---

## Cast (one sentence each)

| Piece | What it is |
|--------|------------|
| **Guest** | Orders three drinks for a room; pays from a Circle wallet on **Arc Testnet**. |
| **servebot-1** | TIAGo robot in Webots; identity is on **peaq mainnet**. |
| **Settler** | Local service (`:8788`); only process that signs Circle + peaq. |
| **Bridge** | Local ledger (`:8787`); connects simulation proof to the settler. |
| **Escrow** | Smart contract on Arc; holds **6.00 USDC** until delivery is proved. |

**Order:** heineken beer, beverage can, water bottle · **6.00 USDC** · example room **1204**.

---

## 0:00 — Hook (15 sec)

[SAY]

“This is a hotel kitchen in simulation. A guest orders drinks from their room. **Six dollars in USDC** go into **escrow on Arc** before the robot moves. The kitchen gets **two dollars** when pickup is detected. The rest **releases** when delivery is proved—split between operator, manufacturer, and the robot’s reserve. In parallel, **peaq** records that **servebot-1** did the work, with public transaction hashes you can audit.”

[SHOW] Webots `kitchen.wbt` paused · **servebot-1** selected · controller `mission_control`.

---

## 0:15 — Guest order (30 sec)

[SAY]

“The guest doesn’t touch a wallet in the demo UI—they tap **Order the drinks** on the hotel page. Behind that, our **settler** creates a unique **job id**—a 32-byte key the escrow contract uses for this delivery.”

[SHOW] http://localhost:3001 → room **1204** → **Order the drinks**.

[SAY]

“Success text includes a job id. That same id is tied to **servebot-1** on peaq from the moment of deposit.”

**Job id (this run):**

`0x59b29db1805714cf06d906b76237df8c092321ab67ccd0ba0a72f99d2a2b4780`

[SHOW] Optional: `http://127.0.0.1:8787/robots/servebot-1/goal` → same job + room + items.

---

## 0:45 — Step 1: Escrow deposit — lock 6.00 USDC (45 sec)

[SAY]

“Step one is **not** ‘pay the robot yet.’ Step one is **lock guest money**. The settler calls Circle to run **`deposit(jobId, machineId, 6_000_000)`** on our **ButlerEscrow** contract on **Arc Testnet**. Six USDC—with six decimals, that’s six million units—moves from the **guest** wallet into escrow. Until release, nobody spends that six dollars; it’s bound to this job and this machine.”

[SHOW] Settler terminal: `locking 6.00 USDC for room-1204` → `Circle deposit` with Arcscan link.

| | |
|---|---|
| **What it means** | Guest funds are **held**, not spent. Robot motion is allowed only after this succeeds. |
| **Arc tx (deposit)** | `0x4285f5e6c7f30b6617722ada5f5f0f10980561f6ac79e5010a264ec494e5ef40` |
| **Arcscan** | https://testnet.arcscan.app/tx/0x4285f5e6c7f30b6617722ada5f5f0f10980561f6ac79e5010a264ec494e5ef40 |
| **Circle id** | `7a42ed2f-f0c0-5002-b0fa-d96e70737166` (verify in Circle Console → Wallets → transactions) |
| **Escrow contract** | `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` · https://testnet.arcscan.app/address/0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD |
| **Guest wallet (Arc)** | `0x566c7344100b046e467eae9d1efb8bd5abf646a2` |

[SAY]

“If deposit fails—guest short on test USDC—you’ll see a failed Circle state, **no** Arc hash, and **no** real lock. Top up the guest to about **six point two** USDC before the demo.”

[SHOW] Settler: `paid goal is on the bridge`.

[SAY]

“The **bridge** now holds the paid goal: job id, room, three items. **Play** in Webots will say **using paid goal** instead of posting a second order.”

---

## 1:30 — Play simulation (20 sec)

[SAY]

“Press **Play**. **mission_control** drives the robot. **butler_observe** only **reads** the scene—pose, what’s carried, what’s on the table—and posts telemetry to the bridge. The robot never holds Circle keys; the settler does.”

[SHOW] Webots console: `using paid goal 0x59b29…` → robot maps / picks up / delivers.

---

## 1:50 — Step 2: Pickup — vending 2.00 USDC (45 sec)

[SAY]

“When telemetry shows **heineken beer** left the counter, the bridge calls the settler **`/pickup`**. That triggers a **second** Arc payment: **two USDC** from the **robot’s** Circle wallet to the **vending** address—the kitchen counter. This is separate from escrow; it’s pay-on-pickup.”

[SHOW] Settler: `Circle vending 2.00` · Arcscan link.

| | |
|---|---|
| **What it means** | Kitchen gets paid when pickup is **proved**, not on a timer. |
| **Arc tx (vending transfer)** | `0x513784057a66b3179a7d8279a875b6964f664f8650ec88eb0f4185c018c528c8` |
| **Arcscan** | https://testnet.arcscan.app/tx/0x513784057a66b3179a7d8279a875b6964f664f8650ec88eb0f4185c018c528c8 |
| **Circle id** | `46ff7189-e4d7-5153-830e-6e1aca209b1e` |
| **Robot wallet (Arc)** | `0x9a8709845445661fd9b044bc907e38faf6d27168` |
| **Vending wallet (Arc)** | `0x01ed2f186edab0b28dd796afe0762fac5a5b092d` |

[SAY]

“Immediately after Arc pickup payment, the settler writes a **revenue event** on **peaq mainnet** for **servebot-1**: **two hundred** cents—two dollars—linked to the Circle payment in metadata. Always use the **`0x` prefix** on peaq hashes in Subscan.”

[SHOW] Subscan EVM tx.

| | |
|---|---|
| **What it means** | Public proof: **this machine** earned revenue at pickup, tied to Arc. |
| **peaq tx (pickup / 200¢)** | `0x61877b9401345c2151d70adc593c98a2b09cc713cca46de7900b943c94827f24` |
| **Subscan** | https://peaq.subscan.io/tx/0x61877b9401345c2151d70adc593c98a2b09cc713cca46de7900b943c94827f24 |
| **Contract (EventRegistry)** | `0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e` |
| **Controller signer** | `0x4360d54AdB797bf75013870de1AAD152839587D0` |

---

## 2:35 — Between pickup and release (20 sec)

[SAY]

“The robot still delivers the **can** and **water**—same job, **no second charge**. Escrow stays locked. The bridge waits until the **heineken** is on the table spot and holds for about **eight seconds** of dwell time, then calls **`/delivery`**. That’s the policy gate for releasing the guest’s six dollars.”

[SHOW] Beer on table · Webots → `DONE` when mission finishes.

---

## 2:55 — Step 3: Delivery — escrow release 6.00 USDC (45 sec)

[SAY]

“Delivery proof triggers **`release(jobId)`** on Arc, signed from the **settler** wallet—the only address the escrow contract accepts. The six USDC in escrow splits: **eighty percent** operator, **ten percent** manufacturer, **ten percent** robot reserve. Integer math leaves dust with the operator.”

[SHOW] Settler: `Circle release` · Arcscan link.

| | |
|---|---|
| **What it means** | Guest escrow **settles**; operator, maker, and robot reserve get paid. |
| **Arc tx (release)** | `0x1f34793b8a0cc2a1b15d77a8068efe45ede13163bd162fee10ea4033277ba927` |
| **Arcscan** | https://testnet.arcscan.app/tx/0x1f34793b8a0cc2a1b15d77a8068efe45ede13163bd162fee10ea4033277ba927 |
| **Circle id** | `31074c7f-55eb-5106-8887-cc214895dd13` |
| **Settler wallet (Arc)** | `0x2838270efa7a1aa0196bb98a8f8230771aed3b80` |
| **Operator (Arc)** | `0x0fa08f931a9d4430f614ab5c49f095bf0ae2240d` |
| **Manufacturer (Arc)** | `0xc26ce44fc41bb13503d20945653767abcbd17f7e` |
| **Robot reserve (Arc)** | `0x9a8709845445661fd9b044bc907e38faf6d27168` (same as servebot-1 wallet) |

[SAY]

“Then a second peaq revenue event: **six hundred** cents—six dollars—for the delivery leg, again tied to the Circle release id.”

| | |
|---|---|
| **peaq tx (delivery / 600¢)** | `0x404ca080f07f35a8d3a1a7cd6316f38d29295ab267102173d4a6670faedc6cfc` |
| **Subscan** | https://peaq.subscan.io/tx/0x404ca080f07f35a8d3a1a7cd6316f38d29295ab267102173d4a6670faedc6cfc |

**On-chain check:** read `jobs(0x59b29…)` on escrow → `released: true`.

---

## 3:40 — Machine identity (30 sec)

[SAY]

“Arc moved **USDC**. peaq answers **which machine** did the job. **servebot-1** is registered on peaq mainnet with a stable machine id—that’s the same id hashed into the escrow deposit.”

[SHOW] Machine explorer.

| | |
|---|---|
| **Machine name** | `servebot-1` |
| **Machine id** | `63056357364750406110742192000069244844268702226710579694851149582072404420819` |
| **URL** | https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819 |

---

## 4:10 — Close (20 sec)

[SAY]

“One guest order, one job id: **three Arc movements**—lock six, pay kitchen two, release six—and **two peaq receipts** for the robot. Circle holds wallets and signs; Arc settles dollars; peaq keeps the auditable work record. That’s the Butler loop for agentic hospitality—hold, prove, pay, split, and show the machine on chain.”

---

## Quick reference — all links (copy sheet)

**Job:** `0x59b29db1805714cf06d906b76237df8c092321ab67ccd0ba0a72f99d2a2b4780`

| Step | Link |
|------|------|
| Arc deposit | https://testnet.arcscan.app/tx/0x4285f5e6c7f30b6617722ada5f5f0f10980561f6ac79e5010a264ec494e5ef40 |
| Arc vending 2.00 | https://testnet.arcscan.app/tx/0x513784057a66b3179a7d8279a875b6964f664f8650ec88eb0f4185c018c528c8 |
| Arc release | https://testnet.arcscan.app/tx/0x1f34793b8a0cc2a1b15d77a8068efe45ede13163bd162fee10ea4033277ba927 |
| peaq pickup 200¢ | https://peaq.subscan.io/tx/0x61877b9401345c2151d70adc593c98a2b09cc713cca46de7900b943c94827f24 |
| peaq delivery 600¢ | https://peaq.subscan.io/tx/0x404ca080f07f35a8d3a1a7cd6316f38d29295ab267102173d4a6670faedc6cfc |
| servebot-1 | https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819 |
| Escrow contract | https://testnet.arcscan.app/address/0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD |

**Networks:** Arc Testnet `5042002` · peaq mainnet `3338` · USDC on Arc testnet `0x3600000000000000000000000000000000000000`.

---

## Operator reminders (whisper, not spoken)

- Start **settler** then **bridge** before Play; keep both up through dwell/release.
- One paid job at a time; wait for **DONE** before a new order.
- Subscan needs **`0x` + 64 hex**; Circle Console uses **UUID** ids.
- Guest ~**6.20** USDC, robot ~**2.20** USDC headroom on Arc testnet before demo day.

---

*Butler · Demo teleprompter · ties to [`MANUAL_RUN_GUIDE.md`](MANUAL_RUN_GUIDE.md) and recorded job `0x59b29…`.*
