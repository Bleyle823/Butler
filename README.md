# Butler

Autonomous Economic Actor on Circle.

Hotel room-service demo: a guest orders the honey jar and both jam jars, `servebot-1` sets them on the kitchen table, USDC on Arc Testnet moves only after proof, and peaq records the revenue. The local settler is the only commander.

Open [`worlds/kitchen.wbt`](worlds/kitchen.wbt) in Webots R2025a. How to run the demo is in [`docs/RUN.md`](docs/RUN.md). Agent rules live in [`AGENTS.md`](AGENTS.md).

- World: `worlds/kitchen.wbt`
- Settler: `packages/settler`. Circle stays here. peaq writes use `peaq-os-sdk` and a local address-keyed wallet file, the same pattern as the peaq robotics stack.
- Bridge: `packages/bridge`
- Hotel UI: `apps/hotel-ui`
- Escrow: `packages/escrow`, contract `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet `5042002`

Planning docs (`docs/PLAN.md`, `docs/scope/`, `docs/specs/`) stay on the operator machine and are not in git. Wallet files and Circle or peaq keys stay out of git too.
