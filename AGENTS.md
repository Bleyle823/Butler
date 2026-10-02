# Butler

Hotel room-service demo. A guest orders pizza. A simulated ServeBot picks it up and delivers it. USDC on Arc Testnet moves only after proof. peaq mainnet holds identity, the bond, and a checkable revenue event. KeeperHub is the only commander.

Open [`worlds/hotel.wbt`](worlds/hotel.wbt) in Webots R2025a. Plugin copies live in `packages/circle-plugin` and `packages/peaqos-plugin`. Planning docs stay local and are gitignored.

## Architecture rules

These three rules do not get bent.

1. Webots never talks to peaq or Circle. It publishes pose, battery, pickup, and delivery. It accepts job goals.
2. peaq never talks to Webots. peaq has no robot URL. KeeperHub is the only commander of the sim and the only writer on peaq.
3. The robot never holds Circle’s entity secret or peaq’s controller key. Circle custody plus KeeperHub Turnkey as peaq controller.

## Git

integration: on
integration branch: develop
branch prefix: feat/
commit: per-milestone

Never build on `main`. Land work on `develop` through `feat/<feature-slug>`. Offer a one-line Conventional Commit when a milestone typechecks. Do not push and do not open a PR until the engineer asks.

```
feat(bridge): add fleet and job HTTP API

Co-Authored-By: Cursor Grok 4.6 <noreply@cursor.com>
```

Never commit `.env`, entity secrets, recovery files, Turnkey keys, or webhook secrets.

## Stack

| Layer | Choice |
|---|---|
| World | Webots R2025a + local `assets/webots` catalog, `ButlerServe` (TIAGo++ with Hey5 hands and torso item slots) |
| Sim host | Windows Webots binary. ROS 2 Jazzy in WSL2 Ubuntu 24.04 |
| Bridge | Python ROS 2 package in `packages/bridge` |
| Money | Circle developer-controlled wallets and Foundry escrow on Arc Testnet `5042002` |
| Trust | peaqOS Economics 2.0 on peaq mainnet `3338` |
| Execution | KeeperHub (`keeperhub-staging` fork, then app.keeperhub.com) |
| Guest UI | Next.js in `apps/hotel-ui` |

## Agent skills

- `scope` (`skills-main/skills/scope/`) owns `docs/scope/`
- `architect` (`skills-main/skills/architect/`) owns `docs/specs/`
- `develop` (`skills-main/skills/develop/`) builds one feature from its spec
- `check` (`skills-main/skills/check/`) verifies against acceptance criteria
- `test` (`skills-main/skills/test/`) runs tests
- `document` (`skills-main/skills/document/`) writes the PR
- `sync` (`skills-main/skills/sync/`) updates this file after a feature ships
- `peaqos` (`~/.agents/skills/peaqos/`) for machine activate, MCR, Verify, and events
- KeeperHub plugin rules: `keeperhub-staging/plugins/AGENTS.md` (`safeFetch`, `"use step"`, `_integrationType`, no SDKs)

## Plugin copies

`packages/circle-plugin` and `packages/peaqos-plugin` are judged here and executed in the KeeperHub fork. After a green `pnpm discover-plugins` and type-check in `keeperhub-staging`, copy the same files into Butler.

## Secrets

Never commit: `.env`, Circle entity secret, recovery file, Turnkey keys, webhook secrets, Pinata or peaq keys. Operator generates and registers the Circle entity secret themselves.
