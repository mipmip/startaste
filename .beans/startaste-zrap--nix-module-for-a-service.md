---
# startaste-zrap
title: nix module for a service
status: todo
type: task
priority: normal
created_at: 2026-05-12T11:30:03Z
updated_at: 2026-09-10T15:06:48Z
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
