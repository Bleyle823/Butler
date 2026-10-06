# Run the kitchen with payments

The robot program is unchanged. Open `worlds/kitchen.wbt`, press Play, and `mission_control` still maps if needed, picks up the honey jar and both jam jars, and places them on the table.

Guest rooms 1204, 1205, and 1206 are west of the existing kitchen door. The robot does not drive into them. A separate supervisor, `butler_observe`, only reads the scene. It tells the bridge when a jar leaves the counter and when that jar has been set on a table spot. The bridge waits 8 seconds on a delivery event before it calls settle.

## What has to be running

- Webots R2025a with `worlds/kitchen.wbt`
- KeeperHub at `http://localhost:3000`
- Bridge at `http://127.0.0.1:8787`
- Hotel UI at `http://localhost:3001`
- A Cloudflare quick tunnel in front of the bridge, because KeeperHub refuses `127.0.0.1`

```
cd packages/bridge
python run_bridge.py
```

```
cloudflared tunnel --url http://127.0.0.1:8787
```

Paste the new `https://*.trycloudflare.com` host into the dispatch workflow HTTP node as `https://<host>/jobs`. The header stays `X-Butler-Secret: change-me`.

```
cd apps/hotel-ui
pnpm install
pnpm dev
```

Place the order for room 1204, 1205, or 1206, then reset the simulation so the grab happens while that job is assigned. `mission_control` does not wait for the order.

`GET /fleet` with header `X-Butler-Secret` shows `servebot-1`. Pickup is a jar moving off the counter with the robot. Delivery is that jar resting on one of the three existing table spots.

Escrow remains `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet `5042002`. Revenue writes stay on peaq mainnet `3338`. Wallet files and webhook keys stay out of git.
