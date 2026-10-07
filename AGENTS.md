# Kitchen payments

The kitchen simulation is the working robot. Butler supplied the name `servebot-1` and the payment stack. The arm, gripper, jars, and `mission_control` behavior tree stay as they are.

## Architecture rules

1. Webots never talks to peaq or Circle. `butler_observe` only publishes pose, pickup, and delivery to the local bridge.
2. peaq never talks to Webots. peaq has no robot URL. The local settler is the only commander of payments and the only writer on peaq.
3. The robot never holds Circle’s entity secret or peaq’s controller key. Circle stays in the settler. The peaq key stays in the settler’s local address-keyed wallet registry. Callers pass the signer address only.

`mission_control` waits until the bridge has a paid goal for the honey jar, jam jar 1, and jam jar 2, then places those jars on the kitchen table. It does not call Circle or peaq.

## Stack

| Layer | Choice |
|---|---|
| World | `worlds/kitchen.wbt`. Guest rooms 1204, 1205, and 1206 are west of the existing door. They are who ordered. The robot does not drive into them. |
| Robot | Existing TIAGo hardware, named `servebot-1`, controller `mission_control` |
| Proof | `controllers/butler_observe` reads the scene and posts to the bridge |
| Bridge | `packages/bridge` at `http://127.0.0.1:8787` |
| Commander | `packages/settler` at `http://127.0.0.1:8788` |
| Money | Circle developer-controlled wallets and Foundry escrow on Arc Testnet `5042002` |
| Trust | peaqOS on peaq mainnet `3338` |
| Guest UI | `apps/hotel-ui` |

KeeperHub is not in the run path. Plugin copies in `packages/circle-plugin` and `packages/peaqos-plugin` are unused references.

Never commit `.env`, entity secrets, recovery files, Turnkey keys, webhook secrets, `config/wallets.json`, or `config/bridge.json`.
