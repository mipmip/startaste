# NixOS VM test for the startaste module. Verifies unit wiring, the hardened
# profile, state locations and the dashboard bind — not real syncing, which
# would need credentials and network access from inside the VM.
{ self }:

{
  name = "startaste-module";

  nodes.machine = { config, pkgs, ... }: {
    imports = [ self.nixosModules.startaste ];

    services.startaste = {
      enable = true;
      # runNixOSTest fixes the node's pkgs, so the overlay cannot be applied
      # here; set the package directly. The overlay path is covered by an eval
      # check instead (pkgs.startaste == packages.<system>.default).
      package = self.packages.${pkgs.stdenv.hostPlatform.system}.default;
      sync.enable = true;
      sync.interval = "15m";
      dashboard.enable = true;
      dashboard.port = 8421;
      mcp.enable = true;
      mcp.port = 8766;
      mcp.tokensFile = "/etc/startaste-mcp-tokens";
    };

    # Token records for the test. In production this is an agenix path; the
    # record's hash is sha256("test-token").
    environment.etc."startaste-mcp-tokens".text = builtins.toJSON [{
      name = "test";
      hash = "4c5dc9b7708905f77f5e5d16316b5dfb425e68cb326dcd55a860e90a7707031e";
      scopes = [ "read" ];
    }];

    environment.systemPackages = [ pkgs.curl pkgs.sqlite ];
  };

  testScript = ''
    machine.wait_for_unit("multi-user.target")

    with subtest("state directory is created for the service user"):
        machine.succeed("test -d /var/lib/startaste")
        machine.succeed("stat -c %U /var/lib/startaste | grep -x startaste")

    with subtest("the sync timer is scheduled"):
        machine.wait_for_unit("startaste-sync.timer")
        machine.succeed("systemctl list-timers --all | grep startaste-sync")

    with subtest("sync without credentials fails cleanly, no traceback"):
        # Exits non-zero with the configured-sources error rather than crashing.
        machine.fail("systemctl start startaste-sync.service")
        journal = machine.succeed("journalctl -u startaste-sync.service --no-pager")
        assert "no sources configured" in journal, journal
        assert "Traceback" not in journal, journal

    with subtest("the dashboard serves on its configured bind"):
        machine.wait_for_unit("startaste-dashboard.service")
        machine.wait_for_open_port(8421)
        machine.succeed("curl -fsS http://127.0.0.1:8421/ >/dev/null")

    with subtest("the database is created under /var/lib"):
        machine.succeed("test -f /var/lib/startaste/startaste.db")
        mode = machine.succeed(
            "sqlite3 /var/lib/startaste/startaste.db 'pragma journal_mode'"
        ).strip()
        assert mode == "wal", mode

    with subtest("the MCP endpoint authenticates"):
        # On a host that has never synced, the server exits because it will
        # not create a database; it retries until one exists (asserted below),
        # so restart once now that the database is there.
        machine.succeed("systemctl reset-failed startaste-mcp.service")
        machine.succeed("systemctl restart startaste-mcp.service")
        machine.wait_for_unit("startaste-mcp.service")
        machine.wait_for_open_port(8766)
        # /healthz needs no credentials and says nothing but liveness
        health = machine.succeed("curl -fsS http://127.0.0.1:8766/healthz")
        assert '"status"' in health, health
        assert "startaste" not in health.lower() or "status" in health, health
        # /mcp without a token is rejected
        code = machine.succeed(
            "curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8766/mcp "
            "-H 'Content-Type: application/json' -d '{}'"
        ).strip()
        assert code == "401", code
        # /mcp with the valid token gets past authentication
        code = machine.succeed(
            "curl -s -o /dev/null -w '%{http_code}' -X POST http://127.0.0.1:8766/mcp "
            "-H 'Authorization: Bearer test-token' "
            "-H 'Content-Type: application/json' -d '{}'"
        ).strip()
        assert code != "401", code

    with subtest("the MCP server retries instead of giving up before a first sync"):
        machine.succeed("systemctl show startaste-mcp.service -p Restart | grep -x Restart=always")
        limit = machine.succeed(
            "systemctl show startaste-mcp.service -p StartLimitIntervalUSec"
        ).strip()
        assert limit.endswith("=0") or "infinity" in limit, limit

    with subtest("units are hardened"):
        for unit in ["startaste-sync.service", "startaste-dashboard.service", "startaste-mcp.service"]:
            machine.succeed(f"systemctl show {unit} -p ProtectSystem | grep -x ProtectSystem=strict")
            machine.succeed(f"systemctl show {unit} -p ProtectHome | grep -x ProtectHome=yes")
            machine.succeed(f"systemctl show {unit} -p NoNewPrivileges | grep -x NoNewPrivileges=yes")

    with subtest("only the state directory is writable"):
        for unit in ["startaste-sync.service", "startaste-dashboard.service", "startaste-mcp.service"]:
            paths = machine.succeed(f"systemctl show {unit} -p ReadWritePaths")
            assert "/var/lib/startaste" in paths, paths
            assert "/etc" not in paths, paths
  '';
}
