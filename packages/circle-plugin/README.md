# Circle wallets plugin (Butler copy)

Judges: read this tree. It is the Circle developer-controlled wallets plugin for KeeperHub.

It is **executed** inside the KeeperHub fork (`keeperhub-staging/plugins/circle-wallets`), because steps import `@/lib/safe-fetch` and `fetchCredentials`. After `pnpm discover-plugins` and type-check go green in the fork, copy the same files here so this snapshot matches.

Rules (from `keeperhub-staging/plugins/AGENTS.md`):

- `safeFetch` only in `steps/` (no SDK, no raw `fetch`)
- `"use step"` on the exported step function
- `_integrationType = "circle-wallets"`
- no `@circle-fin/*` in this package

Laptop provisioner (`scripts/provision-circle-wallets.ts`) may use the Circle SDK. This plugin may not.
