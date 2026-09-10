## Context

See proposal.md — Why. The reference implementation is `linny-mcp-server`:
`flake.nix` (explicit `systems` list, `forAllSystems`, `overlays.default`,
`nixosModules.linny-mcp = import ./nix/module.nix`) and `nix/module.nix` (option
set, generated config file containing paths only, system user, hardened unit).
Its consumer, `mipnix/modules/HOSTS/dapperehaan-server/linny-mcp.nix`, shows what
a host is expected to supply: values, agenix secret paths, and tmpfiles rules.

Two facts from the existing code shape the design:

- `startaste sync` already performs one full pass and exits, so it is a oneshot
  as-is. Nothing in the application needs to change for scheduling.
- `startaste serve` binds `127.0.0.1` unconditionally (`cli.py:99`,
  `app.run(host="127.0.0.1", port=args.port)`). There is a `--port` flag but no
  host flag, so a `listenAddress` option cannot be honoured without a small CLI
  addition.

## Goals / Non-Goals

**Goals:**

- A host can run scheduled sync and the dashboard by setting options only.
- The module is the single place that knows unit shape and hardening, so hosts
  do not each reinvent it.
- Enabling one surface does not force the other.

**Non-Goals:**

- An MCP service option. The server does not exist yet (`startaste-qbtu`);
  options for an unimplemented binary would be dead surface. The module gains it
  with that work.
- A `checks` flake output for build/test/coverage. Worth having — the `/mip:ship`
  gate expects it and startaste has no `scripts/` or `checks` — but it is
  release tooling, not part of running as a service. Its own bean.
- Multi-instance support. One database per host is the whole point; several
  startaste instances on one machine is not a use case.
- Backup or retention of the database. It is reconstructible from the sources.

## Decisions

**The module owns the timer, not the host.** A host should say "sync hourly",
not assemble a oneshot unit and a timer. This moves work that
`deploy-startaste-dapperehaan` currently plans host-side into the module, which
is where it belongs: every future consumer gets it. Alternative considered:
leave unit definition to the host, as its tasks currently assume — rejected
because it duplicates the unit in every consumer and leaves the hardening
profile as a copy-paste.

**Two independent enables, one shared state root.** `sync` and `dashboard` are
separately enableable so the deployment can land sync first and add the
dashboard once WAL is in place (already shipped, `sqlite-wal-mode`, but the
staging matters for the MCP surface later). They coordinate only through the
database file.

**Loopback by default.** `listenAddress` defaults to `127.0.0.1`, so exposing
the dashboard is an explicit act. The dashboard has no authentication of any
kind, so the default must be the safe one; the deployment binds it to the mesh
IP deliberately and relies on nebula as the access control.

**`environmentFile`, not a `.env` and not option values.** Options land in the
world-readable store, and the application's `.env` discovery resolves from the
working directory, which `ProtectHome = true` puts out of reach. A path to a
file read at unit start is the only mechanism that works under the hardened
profile. Same hygiene rule as linny's `tokensFile`: the module takes a path and
never a secret.

**State via the existing env vars.** `STARTASTE_DATA` / `STARTASTE_DB` /
`STARTASTE_LOG` already exist and are specified in the `paths` capability, so
the module sets them rather than introducing a second configuration mechanism.
Defaults point at `/var/lib/startaste`.

**Hardening copied wholesale from linny.** Divergence between two services on
the same host is a liability, and linny's profile is already proven against a
Python-shaped workload's needs (network, one writable tree). `ReadWritePaths`
is computed from the configured state locations.

**`--host` is added to `serve`.** The smallest application change that lets the
module honour `listenAddress`. It keeps the loopback default, so behaviour for
existing users is unchanged.

**Systems enumerated explicitly, no flake-utils.** Matching linny, and
`aarch64-linux` alongside `x86_64-linux` even though dapperehaan is x86_64
(`hardware.nix`: `nixpkgs.hostPlatform = "x86_64-linux"`) — the cost is one list
entry and it stops the flake from being single-system again.

## Risks / Trade-offs

- **`ProtectHome` failures are opaque.** linny hit `226/NAMESPACE` when a
  `ReadWritePaths` target did not exist → the module creates its state
  directories itself (tmpfiles), rather than relying on each host to do it.
- **A timer interval that is shorter than a run.** A first sync takes minutes; a
  ten-minute interval would overlap. systemd will not start a concurrent run, so
  the failure mode is a skipped tick rather than corruption → document the
  first-run cost in the option description and default to an hour.
- **The `--host` addition widens what the dashboard can bind.** It is an
  explicit flag defaulting to loopback, and the module's default matches, so the
  unsafe configuration has to be chosen twice → acceptable; the alternative is a
  module option the application cannot honour.
- **Hardening may be too tight for a workload we have not run as a service
  yet.** startaste needs outbound HTTPS, one writable directory, and nothing
  else, so the profile should fit → verify by actually starting both units in a
  NixOS VM test rather than reasoning about it.
- **Two repos move together.** The mipnix change's tasks assume host-side units
  → its tasks are edited as part of this change's verification, so the two do
  not drift.

## Migration Plan

1. Flake restructure first (`forAllSystems`, overlay), verified by building the
   default package unchanged.
2. Module added, verified in a NixOS VM test with both units enabled.
3. Edit `deploy-startaste-dapperehaan` tasks 3.2/3.3 to set options instead of
   defining units.
4. Rollback is dropping the module import; `packages` and `devShells` keep
   working independently of it.
