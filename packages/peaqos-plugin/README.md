# peaqOS plugin (Butler copy)

Judges: read this tree. It is the peaqOS Economics 2.0 plugin for KeeperHub.

It is **executed** inside the KeeperHub fork (`keeperhub-staging/plugins/peaqos`), because steps import `@/lib/safe-fetch` and Turnkey write helpers. After type-check goes green in the fork, copy the same files here.

Rules: `safeFetch` only, `"use step"`, `_integrationType = "peaqos"`, no `peaq-os-sdk`.

Butler Record Revenue uses `sourceChainId = 0`, `trustLevel = 0`, `currency = "USD"`, Arc hash in `rawData`. EventRegistry on peaq mainnet: `0xA1e7F1d7B24dAb55Dc92491e6d9B89F6E925Ad1e`.
