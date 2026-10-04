# Run the hotel demo

KeeperHub is the only commander. Webots publishes pose, battery, pickup, and delivery. The bridge is the only HTTP surface on the sim. peaq and Circle are called from KeeperHub, never from the robot.

## What has to be running

- Webots R2025a with `worlds/hotel.wbt`
- KeeperHub at `http://localhost:3000`
- Bridge at `http://127.0.0.1:8787`
- Hotel UI at `http://localhost:3001`
- A Cloudflare quick tunnel in front of the bridge, because KeeperHub refuses `127.0.0.1`
- Neon is already the KeeperHub database. Docker is not required.

## Already done on this machine

These stay out of git. Do not print the values.

- `CIRCLE_ENTITY_SECRET` is set in the KeeperHub `.env`, and the local `circle-wallets` integration was re-saved from that file. `CIRCLE_ENV=production`. The plugin field is `CIRCLE_ENV`, not `CIRCLE_ENVIRONMENT`.
- Eight ARC-TESTNET wallets are in `config/wallets.json`. The guest approved `ButlerEscrow` for USDC. The guest ERC-20 balance covers one 6.00 USDC deposit. The robot wallet holds the 2.00 USDC vending fee.
- `ButlerEscrow` is `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet `5042002`. USDC is `0x3600000000000000000000000000000000000000`. The settler is the Circle settler wallet. It is not the operator, and it is not the Turnkey peaq controller.
- The three workflows are imported, enabled, and bound to the local Circle and peaqOS integrations:
  - Dispatch `http://localhost:3000/api/workflows/rfj60n5bjmu21wqo88rj6/webhook`
  - Pickup `http://localhost:3000/api/workflows/zx04hm5dgzkf0l3mqrbe8/webhook`
  - Settle `http://localhost:3000/api/workflows/lw4vi21u40a4xi4fgbaee/webhook`
- `apps/hotel-ui/.env.local` and `config/bridge.json` hold the webhook URLs and a `wfb_` webhook key. The hotel UI and the bridge send `Authorization: Bearer`. Without that header KeeperHub returns 401.
- `config/bridge.json` points `wallets_path` at `config/wallets.json`. The bridge reads `config/bridge.json` when that file exists. The shared secret is still `change-me`, matching the dispatch header `X-Butler-Secret`.
- The dispatch HTTP step posts to the current quick tunnel, `https://shipments-drum-parameter-graham.trycloudflare.com/jobs`. That hostname dies when `cloudflared` stops.

servebot-1 is activated on peaq mainnet. Machine id `59328440066796600542199572455408389928436277639102769462180386810815539058720`. Activation `0xd977ea3da9cf5428f4b605bf83a658551116db4ef3fd49c3cf3c95ce11aa74ca`. The KeeperHub Turnkey controller is `0x0061f86eE9bE903552a431a03ecAD60607D1B767`. `PEAQ_MACHINE_ID` in the hotel UI is that id as 32 bytes. Revenue writes go to chain `3338`. Arc stays on Arc Testnet. The order `jobId` is a 32-byte hex value, because `deposit` and `release` take `bytes32`.

Order `0xb37fed842a0ee45d9caae8f9bf2e3d802df2a15d2a80e8ed68b43f158cb8032b` (room 1204) is settled. Arc locked 6.00 USDC, paid the 2.00 vending fee, and released 4.80 / 0.60 / 0.60. peaq recorded $2.00 as `0xebaa0eb27f243e55dadc0475e6bdb6944fc85018c6b1ba64a269f039c7d30411` and $6.00 as `0xc7f6939db1c9655d0f5ad8d27e91e15d8b065e918f573665ebc50ad7ad3c4ee6`. Those values are 200 and 600 cents.

The Circle faucet API returns 403 for this key. The public page at `https://faucet.circle.com` is what funded the guest. One address, one drip, about 20 USDC, then the captcha blocks repeats.

## Every run

```
cd keeperhub-staging
pnpm dev
```

```
cd Butler/packages/bridge
python run_bridge.py
```

```
cloudflared tunnel --url http://127.0.0.1:8787
```

Copy the new `https://*.trycloudflare.com` host into the dispatch workflow HTTP node as `https://<host>/jobs`, and into `packages/workflows/dispatch.json` if you want the file to match. The header stays `X-Butler-Secret: change-me`.

```
cd Butler/apps/hotel-ui
pnpm dev
```

Open `worlds/hotel.wbt` in Webots. Select servebot-1. The controller is `butler_serve`. Press Play.

Open `http://localhost:3001`, choose room 1204, and order pizza. Kitchen staff still loads the pizza onto the chest tray. Pickup is the tray contact sensor or the box sitting on the tray. The robot then waits 8 seconds at the room before it publishes delivery. The bridge waits that same 8 seconds before it calls the settle webhook.

Confirm:

- `GET /fleet` with header `X-Butler-Secret` shows servebot-1 moving
- Arc release is 4.80 / 0.60 / 0.60 USDC (operator / manufacturer / reserve) on 6.00 USDC
- peaq `record-revenue` uses the servebot-1 machine id on mainnet. The value is cents: 200 for the vending fee and 600 for the order.

`J` on the robot still starts the room-1204 trip without a paid order. That path does not move USDC.

## Escrow

Tests live in `packages/escrow/test/ButlerEscrow.js`: split, dust, refund, replay, and settler must not be the operator.

```
cd packages/escrow
npm install
npx hardhat test
npx hardhat run scripts/deploy.js --network arc_testnet
```

`DEPLOYER_PRIVATE_KEY` stays in the gitignored KeeperHub `.env`. Do not commit it. A new deploy needs a new address in the workflow files and a new guest `approve` on USDC.

## Local HTTP limit

KeeperHub's HTTP Request node rejects `127.0.0.1` even when `SAFE_FETCH_SHADOW=true`. Dispatch must use the public tunnel. The hotel UI and the bridge call KeeperHub on `localhost:3000`, which is the other direction and is not blocked.

Quick tunnels have no uptime guarantee. Start `cloudflared` again next session and paste the new host into the dispatch HTTP node before ordering.

## If something is missing

| Gap | What you see |
|---|---|
| Webhook key missing | KeeperHub returns 401. The key is only in `apps/hotel-ui/.env.local` and `config/bridge.json`. |
| Tunnel stopped | Dispatch deposits USDC, then the HTTP step cannot reach `/jobs`. Start `cloudflared` and update the endpoint. |
| Circle key on the wrong host | Sandbox returns 401. Production returns the wallet list. `CIRCLE_ENV` must stay `production` for this key. |
| Revenue step reverts | The event timestamp has to be at or before the peaq block. The plugin sends the clock minus 30 seconds. Value is cents, currency is `USD`, and the note is stored as its hash. |
| `mcp_robot` still on servebot-1 | The demo controller is not running. Set the controller back to `butler_serve`. |
| Another Webots already on port 1234 | Start this world with `--port=1236`. |
| Dispatch webhook empty | Hotel UI returns 503 and names `KEEPERHUB_DISPATCH_WEBHOOK`. |
| Unknown room | Bridge returns 409. The UI only offers rooms 1204, 1205, and 1206. |
| Guest allowance short | `deposit` reverts. The guest must `approve` the escrow on Arc USDC before the next order. |
