## 1. Flake restructure

- [x] 1.1 Replace the hardcoded `pkgs = nixpkgs.legacyPackages.x86_64-linux`
      with an explicit `systems` list (`x86_64-linux`, `aarch64-linux`) and a
      `forAllSystems` helper, no flake-utils; verify
      `nix build .#packages.x86_64-linux.default` still produces a working
      `bin/startaste` and `nix develop` still enters a shell with the deps
- [x] 1.2 Add `overlays.default` exposing the package as `pkgs.startaste`;
      verify `nix eval` on a nixpkgs instance with the overlay applied resolves
      `startaste` to the same store path as `packages.<system>.default`
- [x] 1.3 Verify `nix flake show` lists `nixosModules.startaste`,
      `overlays.default`, and `packages`/`devShells` for both systems

## 2. Application gap

- [x] 2.1 Add a `--host` flag to `startaste serve` defaulting to `127.0.0.1`
      and pass it to `app.run` (`cli.py:99` currently hardcodes the address);
      verify a test asserts the default is unchanged and that an explicit host
      is passed through

## 3. The module

- [x] 3.1 Create `nix/module.nix` with the `services.startaste` option set —
      `enable`, `package`, `user`/`group`, `dataDir`, `dbPath`, `logPath`,
      `environmentFile`, `sync.enable`, `sync.interval`, `dashboard.enable`,
      `dashboard.listenAddress`, `dashboard.port` — and wire it as
      `nixosModules.startaste`; verify the option set evaluates and that
      `environmentFile` is typed as a path so a literal cannot be passed
- [x] 3.2 Create the system user and group, and the state directories under
      `/var/lib/startaste` via `systemd.tmpfiles.rules` owned by that user;
      verify a first start on a fresh host does not fail namespace setup
- [x] 3.3 Add the sync oneshot unit with `EnvironmentFile`, the
      `STARTASTE_DATA`/`STARTASTE_DB`/`STARTASTE_LOG` environment, and its
      timer (`OnBootSec` plus `OnUnitActiveSec` from `sync.interval`, default
      1h); verify the timer is listed and that the unit populates the database
- [x] 3.4 Add the dashboard unit passing `--host`/`--port` from the options,
      `Restart = "on-failure"`; verify it serves on the configured address and
      on loopback by default
- [x] 3.5 Apply the hardened serviceConfig profile from
      `linny-mcp-server/nix/module.nix` to both units, with `ReadWritePaths`
      computed from the configured state locations; verify both units start
      under it and that a write outside the state paths is denied
- [x] 3.6 Make `sync.enable` and `dashboard.enable` independent; verify enabling
      either alone creates only that unit

## 4. Verification

- [x] 4.1 A NixOS VM test enabling both surfaces: sync populates the database,
      the dashboard answers on its configured address, and the dashboard reads
      while a sync run is in progress without a locked-database error (WAL
      landed in `sqlite-wal-mode`)
- [x] 4.2 Verify no credential reaches the store: evaluate a configuration with
      an `environmentFile` and grep the closure for the values
- [x] 4.3 `pytest tests/ -v` passes and `nix build .#default` succeeds
- [x] 4.4 Update CHANGELOG.md under Unreleased — new NixOS module and overlay,
      multi-system flake outputs, `startaste serve --host`
- [x] 4.5 Edit `mipnix` change `deploy-startaste-dapperehaan` tasks 3.2 and 3.3
      to set `services.startaste.sync.*` options instead of defining the unit
      and timer host-side, so the two changes do not drift
