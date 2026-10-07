# Manual run: kitchen table order

This is the paid kitchen demo on this machine. `servebot-1` waits for a paid goal, then picks up the honey jar, jam jar 1, and jam jar 2 and places them on the kitchen table. The local settler is the only commander. Webots publishes pose, pickup, and delivery. peaq and Circle are called from the settler. The robot never holds Circle’s entity secret or the peaq controller key.

One robot, one paid job at a time. Wait until `servebot-1` is idle before the next order. Every hotel order creates a new 32-byte job id. Do not replay a job that already settled.

Open `worlds/kitchen.wbt`, not a hotel world. The robot controller is `mission_control`. A second supervisor, `butler_observe`, only reads the scene and posts to the local bridge. The robot does not drive into rooms 1204, 1205, or 1206. Those names are who ordered. Completion is the first jar on a table spot.

## What is already set up

These stay on the machine and out of git. Do not print the secret values.

- Circle credentials live in gitignored `.env` at the Butler root. Copy from `.env.example`. `CIRCLE_ENV=production`. The peaq signer is an address. Its key lives in gitignored `config/peaqos_wallets.json`, the same local registry pattern as the peaq robotics stack.
- The eight Arc Testnet wallets live in gitignored `config/wallets.json`. The guest has already approved ButlerEscrow to spend USDC.
- ButlerEscrow is `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet, chain `5042002`. USDC is `0x3600000000000000000000000000000000000000`. Explorer: https://testnet.arcscan.app.
- `servebot-1` is already activated on peaq mainnet, chain `3338`. Machine id `59328440066796600542199572455408389928436277639102769462180386810815539058720`. The hotel UI stores that same id as 32 bytes in `PEAQ_MACHINE_ID`. Machine page: https://machines.peaq.xyz/machine/59328440066796600542199572455408389928436277639102769462180386810815539058720.
- The bridge reads gitignored `config/bridge.json`. Its shared secret is `change-me`. Pickup and delivery post to `http://127.0.0.1:8788`.
- The hotel UI reads gitignored `apps/hotel-ui/.env.local`, which holds `BUTLER_SETTLER_URL=http://127.0.0.1:8788`.

## Money each order needs

The kitchen set is the honey jar, jam jar 1, and jam jar 2. It is 6.00 USDC, locked by the guest into escrow. On pickup of the honey jar the robot pays the vending counter 2.00 USDC from its own wallet. After that honey jar is on the first table spot, the settler releases the 6.00 as 4.80 to the operator, 0.60 to the manufacturer, and 0.60 to the robot reserve. peaq records 200 cents for the vending fee and 600 cents for the order. The two jam jars are the rest of the same run. They do not open a second payment.

On Arc Testnet the native gas balance and the USDC balance are the same token. `eth_getBalance` shows it with 18 decimals. The ERC-20 transfer uses 6 decimals. A wallet that holds exactly 2.00 cannot send 2.00, because gas comes out of that same balance.

Before you order, the guest needs at least about 6.20, the robot at least about 2.20, and the settler enough left for one contract call. The operator wallet is the refill source. Public faucet: https://faucet.circle.com (one drip per address, then a captcha). The Circle faucet API returns 403 for this key.

Check native balances with a User-Agent of `butler-check/1.0`. Arc’s RPC rejects the request without it.

- Guest `0x566c7344100b046e467eae9d1efb8bd5abf646a2`
- Robot `0x9a8709845445661fd9b044bc907e38faf6d27168`
- Operator `0x0fa08f931a9d4430f614ab5c49f095bf0ae2240d`
- Settler `0x2838270efa7a1aa0196bb98a8f8230771aed3b80`
- Vending `0x01ed2f186edab0b28dd796afe0762fac5a5b092d`

## 1. Start the settler

```
cd C:\Users\Omen\Desktop\Butler
uv venv --python 3.12 packages\settler\.venv
uv pip install --python packages\settler\.venv\Scripts\python.exe -r packages\settler\requirements.txt
packages\settler\.venv\Scripts\python.exe packages\settler\run_settler.py
```

`peaq-os-sdk` needs Python 3.10 or newer. The `python` on PATH here is 3.9, so the settler runs from `packages\settler\.venv`. The bridge can stay on 3.9.

Wait until the terminal says `butler settler http://127.0.0.1:8788`. This process is the only writer to Circle and peaq. Leave it open.

peaq writes go through `peaq-os-sdk`, the same client the robotics package uses. The settler looks up the signer by address in `config/peaqos_wallets.json`. Contract addresses and the RPC live in `config/peaq.example.yaml` (copy to `config/peaq.yaml` to override). Pickup and delivery HTTP bodies never include a key.

To seed the registry once, put the machine controller hex in `PEAQ_CONTROLLER_PRIVATE_KEY` and start the settler. It imports that key under the derived address and later calls only pass the address. After that import you can clear the env value and set `defaults.machine_address` in `config/peaq.yaml`. Without a registry entry, deposit still works and pickup or delivery fail on the peaq write. Circle still needs `CIRCLE_API_KEY` and `CIRCLE_ENTITY_SECRET`. The signer must be the controller of machine `59328440066796600542199572455408389928436277639102769462180386810815539058720`. Creating a fresh wallet would be a different machine.

## 2. Start the bridge

```
cd C:\Users\Omen\Desktop\Butler\packages\bridge
python run_bridge.py
```

Python 3.9 on this machine is enough for the bridge. Leave the terminal open.

The bridge listens on `http://127.0.0.1:8787`. It is the only HTTP surface in front of the sim. It does not call Circle or peaq. It stores the current job, serves the robot’s goal, accepts telemetry, and calls the settler on pickup and delivery.

`GET /health` returns 404. That is normal. `GET /fleet` with header `X-Butler-Secret: change-me` returns the robots. Until Webots is playing and `butler_observe` has published, `robots` is empty. `GET /robots/servebot-1/goal` needs no secret and returns the current job id and room, or `{}`.

Wallets are loaded once at process start. If you edit `config/wallets.json`, restart the bridge.

No Cloudflare tunnel is required. The settler posts jobs to `127.0.0.1:8787`.

## 3. Start the hotel page

```
cd C:\Users\Omen\Desktop\Butler\apps\hotel-ui
pnpm dev
```

This serves `http://localhost:3001`. The page lists the honey jar, jam jar 1, and jam jar 2, and the button is “Order the jars.” Rooms are 1204, 1205, and 1206. Anything other than that set returns 400. The room is who ordered.

The order route creates `jobId` as `0x` plus 32 random bytes, because escrow deposit and release take `bytes32`. It sends `machineId` from `PEAQ_MACHINE_ID` when that value is 32 bytes. It posts to the settler `/order`. The page loads `.env.local` only at process start, so restart the hotel UI after changing it. A missing settler returns 503.

Leave the page open. Do not click Order yet.

## 4. Open the kitchen world, and leave it paused

Open `C:\Users\Omen\Desktop\Butler\worlds\kitchen.wbt` in Webots R2025a. Select `servebot-1`. Its controller must be `mission_control`, and the supervisor checkbox must be on. `butler_observe` is already in the world as a second robot. `mcp_robot` on `servebot-1` means the mission is not running.

Do not press Play yet if this is a fresh launch. `mission_control` waits until the bridge goal has a job id, then maps if needed, picks the honey jar, then the two jam jars, and places them on the table. Pressing Play with no goal leaves the robot waiting. No USDC moves until that goal exists and the honey jar is actually picked up.

If another Webots is already listening on port 1234, this world comes up on 1235 and the extern controllers can fail to attach. Close the extra instance, or start this world with `--port=1236`.

If `servebot-1` is already running from an earlier order and the fleet event is idle, you can leave it playing only after you have a new job id on the bridge. A new job id is what the next pickup and table place will settle. Do not replay a job that already settled.

## 5. Place the order

On `http://localhost:3001`, choose room 1204 and order the jars. The button can sit while Circle accepts the deposit. Success on the page is `Order sent. Job 0x….` Copy that job id.

What that click starts:

- The hotel route posts `jobId`, `room`, `item`, and `machineId` to the settler.
- Escrow deposit calls `deposit(bytes32,bytes32,uint256)` from the guest Circle wallet for 6000000 base units, which is 6.00 USDC. Circle accepts slightly before the chain receipt is final. The guest must still have allowance and balance.
- The settler POSTs that job id, `servebot-1`, and the room to `http://127.0.0.1:8787/jobs`. The bridge answers 201 and stores the goal.

Confirm the goal before you press Play:

```
GET http://127.0.0.1:8787/robots/servebot-1/goal
```

The `jobId` must be the one the page just printed, and `room` must be `room-1204`. If the goal is still empty, the settler did not finish posting the job. Check the settler terminal.

## 6. Press Play

Press Play only after the goal matches the new job. `mission_control` reads that goal and then starts the jar tree. The Webots console prints `servebot-1 waiting for honey jar...` until the goal exists, then `servebot-1 starting kitchen order`. `butler_observe` prints pickup and delivery with the jar names and posts telemetry every eight steps. Pickup is the honey jar leaving the counter with the robot. Delivery is that honey jar resting on the first table spot `(-0.38, -0.68)`. The tree then continues with jam jar 1 and jam jar 2. Those later places do not open a second payment. Wait until the robot is idle, then send a new job id, before you order again.

Fleet telemetry, with header `X-Butler-Secret: change-me`, is the proof the trip is real. You should see `event` move to `pickup` with a jar name in `carried`, then `delivery` with that jar on a table spot. The robot does not go to `(-5.95, …)`.

The bridge waits 8 seconds on a `delivery` event before it calls the settler. It will not call delivery until pickup has already been sent for that job id.

## 7. What pickup and settle do

When the jar is with the robot, the bridge POSTs `/pickup` to the settler. That does two things:

- Pay vending sends 2.00 USDC from the robot wallet to the vending address.
- Record pickup revenue calls peaq `submitEvent` for machine `servebot-1`, value 200, currency USD. The timestamp sent on chain is the local clock minus 30 seconds, because peaq rejects a timestamp ahead of the block. Arc’s chain id is not an allowed event source, so `sourceChainId` stays 0 and the Arc hash is carried in the note.

After the 8 second dwell on `delivery`, the bridge POSTs `/delivery` to the settler. A normal table place is `failure: false`.

- Escrow release is sent by the Circle settler wallet. `release` splits the 6.00 as 4.80 / 0.60 / 0.60.
- Record delivery revenue writes value 600 on the same machine.

The settler terminal prints Circle transaction ids and peaq hashes. The bridge waits up to 120 seconds for each call.

## 8. Confirm the money and the record

Escrow `jobs(jobId)` should show amount 6.00, released true, refunded false.

Circle transactions should reach COMPLETE. Their Arc hashes open at `https://testnet.arcscan.app/tx/<hash>`.

peaq hashes open at `https://peaq.subscan.io/tx/<hash>`. Use `/tx/`, not `/evmtx/`.

A finished run has one Arc deposit, one Arc vending payment, one Arc release, and two peaq revenue transactions. The first jar is on the table. The robot may still be placing the remaining jam jars. Those are not a second paid job.

## If a step fails

| What you see | What it means |
| --- | --- |
| Hotel page 503 | The settler is not running on `8788`. Start `packages/settler`. |
| Hotel page 502 | Circle deposit failed, or the bridge rejected `/jobs`. Read the settler terminal. |
| Deposit succeeds, robot never stores a goal | The settler could not POST to `127.0.0.1:8787`. Start the bridge. |
| Robot grabs before any USDC moves | Play was pressed before a paid goal was on the bridge. Reset the world, order again, then Play. |
| Vending transfer fails with insufficient native token | The robot holds 2.00 or less. Refill it from the operator so it can pay 2.00 plus gas. |
| Guest deposit reverts | The guest is short of 6.00 plus gas, or the USDC allowance for the escrow is spent. |
| Pickup Circle works, peaq fails | The local wallet registry has no controller key, or the signer address is not the machine controller. |
| Settle never starts | `delivery` was not held for 8 seconds, or pickup never fired for this job. |
| Revenue reverts | Value must be cents (200 on pickup, 600 on delivery) and the timestamp must be at or before the peaq block. The settler already sends the clock minus 30 seconds. |
| Soup, or any item other than the three jars | The hotel route returns 400. The order is honey jar, jam jar 1, and jam jar 2. |
| Unknown room | The bridge returns 409. The page only offers 1204, 1205, and 1206. |
