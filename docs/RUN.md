# Confirm kitchen payments end to end

Follow these stages in order. Do not skip a pass check. One robot, one paid job at a time. Wait until `servebot-1` is idle before the next run. Do not replay a job that already settled.

Open `worlds/kitchen.wbt`. The robot controller is `mission_control`. `butler_observe` only reads the scene and posts telemetry. Rooms 1204, 1205, and 1206 are who ordered. The robot does not drive into them.

Press Play with the settler and bridge already up. If the bridge has no paid goal, Play posts the kitchen order (honey jar, jam jar 1, jam jar 2 for room 1204). The hotel page can place that same order first; Play then uses the existing goal.

The Webots controller talks to the settler the way peaq ROS talks to `peaqos_node`: job id and room only. Circle’s entity secret and the peaq controller key stay in the settler.

## What must already exist on this machine

These stay out of git. Do not print secret values.

| File | Role |
| --- | --- |
| `.env` | `CIRCLE_API_KEY`, `CIRCLE_ENTITY_SECRET`, `CIRCLE_ENV=production`, `BUTLER_SECRET=change-me`, settler bind `127.0.0.1:8788` |
| `config/wallets.json` | Arc Testnet Circle wallet ids. Guest has already approved ButlerEscrow |
| `config/peaqos_wallets.json` | Local peaq key registry. Signer `0x4360d54AdB797bf75013870de1AAD152839587D0` |
| `config/bridge.json` | Bridge on `8787`, pickup/delivery URLs on `8788` |
| `apps/hotel-ui/.env.local` | `BUTLER_SETTLER_URL=http://127.0.0.1:8788` and `PEAQ_MACHINE_ID` as 32 bytes |

Copy from the matching `*.example` files if any of those are missing.

Fixed addresses for this project:

- Escrow `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet `5042002`. Explorer: https://testnet.arcscan.app
- USDC `0x3600000000000000000000000000000000000000`
- Machine decimal `63056357364750406110742192000069244844268702226710579694851149582072404420819`
- Machine bytes32 `0x8b68a22dc5d3c9c64f444db3928d7ee5907c829a8e4419dbcc04d1103c9aa8d3`
- Machine page: https://machines.peaq.xyz/machine/63056357364750406110742192000069244844268702226710579694851149582072404420819
- EventRegistry `0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e` (Economics 2.0)

## Money each order needs

The kitchen set is 6.00 USDC from the guest into escrow. On honey-jar pickup the robot pays vending 2.00 from its own wallet. After that honey jar sits on the first table spot `(-0.38, -0.68)`, escrow releases 4.80 / 0.60 / 0.60 to operator / manufacturer / robot reserve. peaq records 200 cents on pickup and 600 cents on delivery. The two jam jars are the rest of the same run. They do not open a second payment.

On Arc Testnet native gas and USDC are the same token. `eth_getBalance` is 18 decimals. ERC-20 transfers use 6. A wallet that holds exactly 2.00 cannot send 2.00.

Before a run, guest about 6.20, robot about 2.20, settler enough for one contract call. Operator is the refill source. Faucet: https://faucet.circle.com. Check Arc balances with User-Agent `butler-check/1.0`.

- Guest `0x566c7344100b046e467eae9d1efb8bd5abf646a2`
- Robot `0x9a8709845445661fd9b044bc907e38faf6d27168`
- Operator `0x0fa08f931a9d4430f614ab5c49f095bf0ae2240d`
- Settler `0x2838270efa7a1aa0196bb98a8f8230771aed3b80`
- Vending `0x01ed2f186edab0b28dd796afe0762fac5a5b092d`

---

## Stage 0 — files, not money

Confirm the gitignored files exist. Do not open them in chat or commit them.

```
cd C:\Users\Omen\Desktop\Butler
dir .env
dir config\wallets.json
dir config\peaqos_wallets.json
dir config\bridge.json
dir apps\hotel-ui\.env.local
```

Pass: all five exist.

If `config/peaqos_wallets.json` is empty, put the controller hex in `PEAQ_CONTROLLER_PRIVATE_KEY` once, start the settler so it imports the address, then you can clear the env value. `defaults.machine_address` in `config/peaq.yaml` should be `0x4360d54AdB797bf75013870de1AAD152839587D0`.

---

## Stage 1 — settler is up

`peaq-os-sdk` needs Python 3.10+. PATH `python` here is 3.9, so use the settler venv.

```
cd C:\Users\Omen\Desktop\Butler
uv venv --python 3.12 packages\settler\.venv
uv pip install --python packages\settler\.venv\Scripts\python.exe -r packages\settler\requirements.txt
packages\settler\.venv\Scripts\python.exe packages\settler\run_settler.py
```

Leave this terminal open.

Pass: the process prints `butler settler http://127.0.0.1:8788`.

```
curl.exe http://127.0.0.1:8788/health
```

Pass: `{"ok": true}`.

---

## Stage 2 — bridge is up

New terminal:

```
cd C:\Users\Omen\Desktop\Butler\packages\bridge
python run_bridge.py
```

Leave it open. Wallets load once at start. Restart the bridge if you edited `config/wallets.json`.

Pass: it is listening. `GET /health` is 404. That is normal.

```
curl.exe -H "X-Butler-Secret: change-me" http://127.0.0.1:8787/fleet
curl.exe http://127.0.0.1:8787/robots/servebot-1/goal
```

Pass: fleet JSON comes back (`robots` may still be empty). Goal is `{}` until an order exists.

---

## Stage 3 — hotel page (optional)

You can skip this stage. Play will post the same order. Use the page if you want to see the guest UI.

New terminal:

```
cd C:\Users\Omen\Desktop\Butler\apps\hotel-ui
pnpm dev
```

Pass: `http://localhost:3001` lists honey jar, jam jar 1, jam jar 2. Button is “Order the jars.” Rooms 1204, 1205, 1206. Do not click yet unless you want the hotel to create the job before Play.

Restart this process after changing `.env.local`. Missing settler returns 503.

---

## Stage 4 — kitchen world, still paused

Open `C:\Users\Omen\Desktop\Butler\worlds\kitchen.wbt` in Webots R2025a.

Select `servebot-1`. Controller must be `mission_control`. Supervisor checkbox on. `butler_observe` is a second robot in the world. If `servebot-1` is `mcp_robot`, the mission will not run.

If another Webots already owns port 1234, this world binds 1235 and extern controllers can fail. Close the extra instance, or use `--port=1236`.

If a previous fast-mode run exploded the TIAGo pose, reload the world file before Play.

Pass: kitchen visible, robot on the floor, three jars on the counter, world still paused.

---

## Stage 5 — Play starts the paid order (Circle deposit)

Press Play. Watch the **Webots console** and the **settler terminal**.

If no goal was on the bridge, pass lines look like:

```
[kitchen] Play: posting order 0x…
[kitchen] locking 6.00 USDC for room-1204
[kitchen] Circle deposit <uuid> arc https://testnet.arcscan.app/tx/0x…
[kitchen] paid goal is on the bridge
servebot-1 starting kitchen order 0x…
```

If the hotel already ordered, you see `[kitchen] using paid goal 0x…` instead of Play posting.

Copy the `0x` job id (66 characters).

```
curl.exe http://127.0.0.1:8787/robots/servebot-1/goal
curl.exe http://127.0.0.1:8788/jobs/0xYOUR_JOB_ID
```

Pass:

- Goal `jobId` matches, `room` is `room-1204` (or the room you ordered from the page).
- Settler job lines include the Circle deposit id and the Arcscan link.
- Guest USDC dropped by 6.00 plus gas. Circle transaction reaches COMPLETE. Arc hash (when present) opens at `https://testnet.arcscan.app/tx/<hash>`.

The robot may map first. That is still the same job. Do not press Play again.

---

## Stage 6 — honey jar pickup (Circle vending + peaq 200)

Wait until the gripper has the honey jar and the jar has left the counter.

Webots / `butler_observe` prints a pickup with `honey jar`. Fleet:

```
curl.exe -H "X-Butler-Secret: change-me" http://127.0.0.1:8787/fleet
```

Pass: `event` is `pickup`, `carried` includes honey jar. The robot is not at `(-5.95, …)`.

Then the settler / Webots console:

```
[kitchen] Circle vending 2.00 <uuid>
[kitchen] peaq pickup revenue 0x…
```

Pass:

- Robot wallet down about 2.00 plus gas. Vending up about 2.00.
- peaq hash opens at `https://peaq.subscan.io/tx/<hash>` (use `/tx/`, not `/evmtx/`).
- Machine page can show the new revenue event.

If Circle vending works and peaq fails, the registry has no controller key or the signer is not this machine’s controller. Deposit already happened; do not replay that job id.

---

## Stage 7 — honey jar on the first table spot (Circle release + peaq 600)

Delivery is the honey jar resting on `(-0.38, -0.68)`. The bridge waits 8 seconds of wall clock after that telemetry, and it will not call delivery until pickup already ran for this job id.

Pass after the dwell:

```
[kitchen] Circle release <uuid>
[kitchen] peaq delivery revenue 0x…
```

Fleet `event` is `delivery` with the honey jar on a table spot.

Escrow `jobs(jobId)` on Arc: amount 6.00, released true, refunded false. Split 4.80 / 0.60 / 0.60.

The tree then places jam jar 1 and jam jar 2. Those places do not start another payment. Wait for `DONE` in the Webots console before a new order.

---

## Stage 8 — finished job

A complete paid run has:

1. One Arc deposit (6.00 lock)
2. One Arc vending payment (2.00)
3. One Arc release (6.00 split)
4. Two peaq revenue txs (200 then 600)
5. Honey jar on the first table spot

`GET /jobs/0xYOUR_JOB_ID` on the settler should list all five console lines. Circle txs COMPLETE. Both peaq hashes on Subscan.

---

## Hotel-first variant

Same stages 0–4. On the hotel page choose room 1204 and order the jars. Success text is `Order sent. Job 0x….` Then confirm goal before or while Play is running. Play must not post a second order while that goal is still on the bridge.

---

## If a stage fails

| What you see | What it means |
| --- | --- |
| Settler never prints the listen line | Python is 3.9, venv missing, or `.env` failed to load. Use `packages\settler\.venv`. |
| `curl` health on 8788 fails | Settler is not running, or another process owns the port. |
| Hotel page 503 | Settler is not on `8788`. |
| Hotel page 502 | Circle deposit failed, or the bridge rejected `/jobs`. Read the settler terminal. |
| Play: order failed | Settler or Circle down, or guest short of 6.00 plus gas. |
| Deposit succeeds, goal stays `{}` | Settler could not POST `127.0.0.1:8787`. Start the bridge. |
| `[butler_observe] bridge post failed` | Bridge down, or the world was in a bad pose. Reload `kitchen.wbt`. |
| Vending transfer fails, insufficient native token | Robot holds 2.00 or less. Refill from the operator. |
| Guest deposit reverts | Guest short of 6.00 plus gas, or USDC allowance for the escrow is spent. |
| Pickup Circle works, peaq fails | No controller key in `peaqos_wallets.json`, or signer is not this machine controller. |
| Settle never starts | Delivery was not held 8 seconds, or pickup never fired for this job. |
| Revenue reverts | Value must be cents (200 / 600). Timestamp must not be ahead of the peaq block. The settler already sends clock minus 30 seconds. |
| Soup or any other item | Hotel route 400. Order is the three jars. |
| Unknown room | Bridge 409. Only 1204, 1205, 1206. |
| Robot in pieces / flying | Fast mode exploded physics. Reload the world, real-time, Play once. |
