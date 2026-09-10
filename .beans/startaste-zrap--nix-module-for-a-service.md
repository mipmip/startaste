---
# startaste-zrap
title: nix module for a service
status: completed
type: task
priority: normal
created_at: 2026-05-12T11:30:03Z
updated_at: 2026-09-10T15:36:43Z
---

Expose startaste as a NixOS service so it can run on dapperehaan. This is the
blocker for [[startaste-8khv]] (timer-driven sync) and [[startaste-qbtu]] (MCP
server) — neither can be wired into a host until the flake offers something to
import.

The flake currently outputs only `packages.x86_64-linux.default` and
`devShells.x86_64-linux.default`. Needed:

- `nixosModules.startaste` and `overlays.default`, so a host can do what
  `mipnix/modules/HOSTS/dapperehaan-server/linny-mcp.nix` does:
  `imports = [ inputs.startaste.nixosModules.startaste ]` plus
  `nixpkgs.overlays = [ inputs.startaste.overlays.default ]`
- module options following the linny-mcp shape (`nix/module.nix` in
  linny-mcp-server is the reference): enable, listenAddress, port, dataDir,
  stateDir, environmentFile, user/group, hardened unit
- the flake declares only `x86_64-linux`; decide whether to keep it that way

Constraints found while exploring, all of which the module has to respect:

- The linny unit sets `ProtectHome = true`. Anything under `/home` is invisible
  to the service, so `dataDir`/`stateDir` must be under `/var/lib/startaste`
  (set via `STARTASTE_DATA` / `STARTASTE_DB` / `STARTASTE_LOG`) and listed in
  `ReadWritePaths`. linny hit `226/NAMESPACE` when a path was missing before
  start — create dirs with `systemd.tmpfiles.rules`.
- Credentials must come from `EnvironmentFile=` pointing at an agenix secret,
  never a `.env`. As of `fix-env-file-loading`, `.env` is resolved from the
  working directory, which under `ProtectHome` cannot be the user's home. Never
  a token literal in a Nix option.
- SQLite needs WAL before a second unit reads the database — see
  [[startaste-hq9c]].

## Summary of Changes

Shipped as openspec change `nixos-service-module`, archived at
`openspec/changes/archive/2026-09-10-nixos-service-module`, commit `119a423`.

`flake.nix` restructured around an explicit `systems` list with `forAllSystems`
(`x86_64-linux`, `aarch64-linux`, no flake-utils), plus `overlays.default`
exposing `pkgs.startaste`, `nixosModules.startaste`, a `checks` entry for the VM
test, and a formatter.

`nix/module.nix` provides `services.startaste`: `sync.enable` /
`sync.interval` (oneshot + timer, default 1h) and `dashboard.enable` /
`listenAddress` / `port`, independently enableable, both under linny-mcp's
hardened profile. State defaults under `/var/lib/startaste` via
`STARTASTE_DATA` / `STARTASTE_DB` / `STARTASTE_LOG`, with directories created by
tmpfiles. Credentials come from `environmentFile` (a path, never a value).

One application change: `startaste serve` gained `--host`, still defaulting to
`127.0.0.1`. It previously hardcoded its bind, so `listenAddress` could not have
been honoured.

Verified by a NixOS VM test (`nix/tests/module.nix`, 22s) and by evaluating
configurations for independent enables, ExecStart arguments and credential
hygiene. New live capability `nixos-service` (7 requirements, 24 scenarios).

Also closes [[startaste-8khv]] in substance — the timer is where scheduled sync
landed, with no interval loop in the application.

Unblocks `mipnix` change `deploy-startaste-dapperehaan`, whose tasks 3.1-3.3 and
4.1 were rewritten to set options instead of defining units host-side.
