<!-- Epic: .beans/startaste-zrap--nix-module-for-a-service.md -->

## Why

startaste cannot be deployed on a host today. Its flake exposes only
`packages.x86_64-linux.default` and `devShells.x86_64-linux.default`, so there
is nothing for a NixOS configuration to import — no module, no overlay, and the
package attribute is hardcoded to one system.

This blocks the whole deployment: the `mipnix` change
`deploy-startaste-dapperehaan` opens with
`imports = [ inputs.startaste.nixosModules.startaste ]`, and it cannot be
applied until that attribute exists. Beans `startaste-8khv` (scheduled sync) and
`startaste-qbtu` (MCP server) sit behind the same gap.

The pattern to follow already exists and is proven on the target host:
`linny-mcp-server`'s `flake.nix` and `nix/module.nix`, consumed by
`mipnix/modules/HOSTS/dapperehaan-server/linny-mcp.nix`.

## What Changes

- Restructure the flake to enumerate systems explicitly (`x86_64-linux`,
  `aarch64-linux`) with a `forAllSystems` helper instead of a hardcoded
  `nixpkgs.legacyPackages.x86_64-linux`, so `packages` and `devShells` are no
  longer single-system. No flake-utils, matching linny.
- Add `overlays.default`, exposing the package as `pkgs.startaste`, so a host
  can get the module's default package.
- Add `nixosModules.startaste`: a `services.startaste` option set and the
  systemd units to run it.
- **Scheduled sync** as a `Type=oneshot` unit plus a `systemd.timer` owned by
  the module, configured with an interval option. This is where bean
  `startaste-8khv` lands: no interval loop goes into the application, because
  systemd already supplies the schedule, backoff, journald logging and
  non-overlapping runs.
- **Dashboard** as a long-running unit with `listenAddress` and `port` options,
  defaulting to loopback so a host must opt into a wider bind.
- Credentials via an `environmentFile` option — a path, never a value, so no
  credential can land in the world-readable `/nix/store`. The application's
  `.env` discovery is unusable under a hardened unit (`ProtectHome = true`
  seals off `/home`, and `.env` resolves from the working directory).
- Data, database and log locations default under `/var/lib/startaste` via the
  existing `STARTASTE_DATA` / `STARTASTE_DB` / `STARTASTE_LOG` env vars, with
  the directories created by the module and listed in `ReadWritePaths`.
- A hardened unit profile matching linny's (`ProtectSystem = "strict"`,
  `ProtectHome`, `PrivateTmp`, `NoNewPrivileges`, `SystemCallFilter`,
  `CapabilityBoundingSet`, `RestrictAddressFamilies`, `UMask = "0077"`, …), a
  system user and group, and `Restart = "on-failure"`.

Not breaking: `packages.<system>.default` keeps working for existing users, and
`nix develop` is unchanged apart from now resolving per system.

## Capabilities

### New Capabilities
- `nixos-service`: how startaste is consumed as a NixOS service — the flake
  attributes a host imports, the `services.startaste` option surface, the
  scheduled-sync and dashboard units, where state lives, and how credentials
  reach the units.

### Modified Capabilities
<!-- None with a live spec. The archived `cli` capability has an "Installable
     binary via flake" requirement, but that capability exists only as an
     archived delta (see startaste-4t8b), so it cannot carry a MODIFIED delta.
     The new requirements here supersede it in practice; reconciling the two is
     part of the spec backfill, not this change. -->

## Impact

- `flake.nix` — `forAllSystems`, `overlays.default`, `nixosModules.startaste`.
- `nix/module.nix` — new file, the module itself.
- No change to any Python module. `startaste sync` is already the oneshot the
  timer needs, and the dashboard already takes `--port`; the only application
  gap is that `startaste serve` binds `127.0.0.1` unconditionally
  (`cli.py:99`), which the module cannot override — so a `listenAddress`
  option requires a small CLI addition, tracked in tasks.
- Downstream: `mipnix` change `deploy-startaste-dapperehaan` currently plans to
  define the sync unit and timer in its host module. Once the module owns them,
  its tasks 3.2 and 3.3 reduce to setting `services.startaste.sync.interval`.
  That change is not yet applied, so this is an edit to its tasks, not a
  migration.
- Deliberately out of scope: an MCP service option (the server does not exist
  yet — bean `startaste-qbtu`), and a `checks` flake output for the
  build/test/coverage gate, which is a release-tooling concern with its own
  bean rather than part of running as a service.
