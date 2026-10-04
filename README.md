# Butler

Autonomous Economic Actor on Circle.

Hotel room-service demo: a guest orders pizza, a simulated ServeBot delivers it, USDC on Arc Testnet moves only after proof, and peaq records the revenue. KeeperHub is the only commander.

Open [`worlds/hotel.wbt`](worlds/hotel.wbt) in Webots R2025a. How to run the demo is in [`docs/RUN.md`](docs/RUN.md). Agent rules live in [`AGENTS.md`](AGENTS.md).

- World: `worlds/hotel.wbt`
- Bridge: `packages/bridge`
- Hotel UI: `apps/hotel-ui`
- Workflows: `packages/workflows`
- Escrow: `packages/escrow`, contract `0xeEFF543d9312fAc816c0C8b0f37ddB4545bBBdaD` on Arc Testnet `5042002`
- Plugin copies: `packages/circle-plugin` and `packages/peaqos-plugin`. Revenue writes go to peaq mainnet `3338`.

Planning docs (`docs/PLAN.md`, `docs/scope/`, `docs/specs/`) stay on the operator machine and are not in git. Wallet files, webhook keys, and the Cloudflare tunnel host stay out of git too.
