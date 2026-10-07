# Kitchen payments

The kitchen simulation is the working robot. Butler supplied the name `servebot-1` and the payment stack. The arm, gripper, jars, and `mission_control` behavior tree stay as they are.

## Architecture rules

1. peaq’s ROS robots run `peaqos_node` on the robot host. Callers pass an address and a machine id. Keys stay in a local wallet registry. Butler uses the same split: `mission_control` calls the settler; the settler runs `peaq-os-sdk`. Webots R2025a’s controller Python is 3.9, and the SDK needs 3.10+, so the SDK does not load inside the controller process.
2. `mission_control` may POST `/order` and GET `/jobs/<id>` on the settler when Play starts. `butler_observe` still only publishes pose, pickup, and delivery to the local bridge.
3. peaq never talks to Webots. peaq has no robot URL. The settler is the only writer on peaq and the only process that holds Circle’s entity secret.
4. The robot never holds Circle’s entity secret or peaq’s controller key. Callers pass a job id and room. The peaq key stays in the settler’s address-keyed wallet registry.

`mission_control` starts a kitchen order on Play if the bridge has no paid goal, then places the honey jar, jam jar 1, and jam jar 2 on the kitchen table. The Webots console prints settler lines as Circle and peaq settle.

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

Never commit `.env`, entity secrets, recovery files, Turnkey keys, webhook secrets, `config/wallets.json`, `config/bridge.json`, or `config/peaqos_wallets.json`.
