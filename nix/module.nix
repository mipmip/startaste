{ config, lib, pkgs, ... }:

# NixOS module for startaste.
#
# SECRET HYGIENE: `environmentFile` is a PATH, never a credential value. Never
# place a token or password in a Nix option — options land world-readable in
# /nix/store. Point it at e.g. config.age.secrets.startaste-env.path.
#
# The application's own `.env` discovery is unusable here: the unit sets
# ProtectHome = true, and `.env` is resolved from the working directory.

let
  cfg = config.services.startaste;
in
{
  options.services.startaste = {
    enable = lib.mkEnableOption "startaste (own your stars, upvotes and favorites)";

    package = lib.mkOption {
      type = lib.types.package;
      default = pkgs.startaste;
      defaultText = lib.literalExpression "pkgs.startaste";
      description = "The startaste package to run (add overlays.default to get it).";
    };

    user = lib.mkOption {
      type = lib.types.str;
      default = "startaste";
      description = "User to run the units as. A system user is created when left at the default.";
    };

    group = lib.mkOption {
      type = lib.types.str;
      default = "startaste";
      description = "Group to run the units as.";
    };

    dataDir = lib.mkOption {
      type = lib.types.str;
      default = "/var/lib/startaste";
      description = ''
        Data directory. Must be outside /home: the units set ProtectHome = true.
        Sets STARTASTE_DATA.
      '';
    };

    dbPath = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      defaultText = lib.literalExpression ''"''${dataDir}/startaste.db"'';
      description = "Database path. Defaults to startaste.db inside dataDir. Sets STARTASTE_DB.";
    };

    logPath = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      defaultText = lib.literalExpression ''"''${dataDir}/startaste.log"'';
      description = "Log path. Defaults to startaste.log inside dataDir. Sets STARTASTE_LOG.";
    };

    environmentFile = lib.mkOption {
      type = lib.types.nullOr lib.types.path;
      default = null;
      example = "/run/agenix/startaste-env";
      description = ''
        Path to a file with source credentials (HN_COMMENTS_ACCT, HN_COMMENTS_PW,
        GITHUB_TOKEN), read at unit start. A PATH, never a value — a credential in
        a Nix option would land in the world-readable store.
      '';
    };

    sync.enable = lib.mkOption {
      type = lib.types.bool;
      default = true;
      description = "Sync sources on a timer. `startaste sync` is a oneshot; systemd owns the schedule.";
    };

    sync.interval = lib.mkOption {
      type = lib.types.str;
      default = "1h";
      example = "6h";
      description = ''
        How often to sync, as a systemd time span. Keep it comfortably longer
        than a run: a first sync takes minutes (every item's metadata is
        fetched), later incremental runs take seconds. An overlapping tick is
        skipped rather than run concurrently.
      '';
    };

    dashboard.enable = lib.mkOption {
      type = lib.types.bool;
      default = false;
      description = "Serve the local web dashboard. It has NO authentication — see listenAddress.";
    };

    dashboard.listenAddress = lib.mkOption {
      type = lib.types.str;
      default = "127.0.0.1";
      example = "192.168.100.2";
      description = ''
        Address for the dashboard to bind. Defaults to loopback: the dashboard
        has no authentication of any kind, so a wider bind must be deliberate
        and should be reachable only over a trusted network.
      '';
    };

    dashboard.port = lib.mkOption {
      type = lib.types.port;
      default = 8421;
      description = "Port for the dashboard.";
    };
  };

  config = lib.mkIf cfg.enable (
    let
      dbPath = if cfg.dbPath != null then cfg.dbPath else "${cfg.dataDir}/startaste.db";
      logPath = if cfg.logPath != null then cfg.logPath else "${cfg.dataDir}/startaste.log";

      environment = {
        STARTASTE_DATA = cfg.dataDir;
        STARTASTE_DB = dbPath;
        STARTASTE_LOG = logPath;
        STARTASTE_STATE = cfg.dataDir;
      };

      # Everything the units may write. Nothing else on the filesystem is
      # writable (ProtectSystem = strict).
      rwPaths = lib.unique [
        cfg.dataDir
        (builtins.dirOf dbPath)
        (builtins.dirOf logPath)
      ];

      hardening = {
        ProtectSystem = "strict";
        ReadWritePaths = rwPaths;
        ProtectHome = true;
        PrivateTmp = true;
        PrivateDevices = true;
        NoNewPrivileges = true;
        RestrictAddressFamilies = [ "AF_INET" "AF_INET6" "AF_UNIX" ];
        SystemCallFilter = [ "@system-service" "~@privileged" ];
        SystemCallArchitectures = "native";
        CapabilityBoundingSet = [ "" ];
        AmbientCapabilities = [ "" ];
        LockPersonality = true;
        MemoryDenyWriteExecute = true;
        ProtectKernelTunables = true;
        ProtectKernelModules = true;
        ProtectKernelLogs = true;
        ProtectControlGroups = true;
        ProtectClock = true;
        ProtectProc = "invisible";
        ProcSubset = "pid";
        RestrictNamespaces = true;
        RestrictSUIDSGID = true;
        RestrictRealtime = true;
        UMask = "0077";
      };

      common = {
        User = cfg.user;
        Group = cfg.group;
      } // hardening // lib.optionalAttrs (cfg.environmentFile != null) {
        EnvironmentFile = toString cfg.environmentFile;
      };
    in
    {
      users.users.${cfg.user} = lib.mkIf (cfg.user == "startaste") {
        isSystemUser = true;
        group = cfg.group;
        home = cfg.dataDir;
      };
      users.groups.${cfg.group} = lib.mkIf (cfg.group == "startaste") { };

      # The hardened units bind-mount ReadWritePaths, so a missing directory
      # fails namespace setup before exec. Create them up front.
      systemd.tmpfiles.rules =
        map (p: "d ${p} 0750 ${cfg.user} ${cfg.group} - -") rwPaths;

      systemd.services.startaste-sync = lib.mkIf cfg.sync.enable {
        description = "startaste source sync";
        after = [ "network-online.target" ];
        wants = [ "network-online.target" ];
        inherit environment;
        serviceConfig = common // {
          Type = "oneshot";
          ExecStart = lib.escapeShellArgs [ "${cfg.package}/bin/startaste" "sync" ];
        };
      };

      systemd.timers.startaste-sync = lib.mkIf cfg.sync.enable {
        description = "startaste source sync schedule";
        wantedBy = [ "timers.target" ];
        timerConfig = {
          OnBootSec = "2min";
          OnUnitActiveSec = cfg.sync.interval;
          Unit = "startaste-sync.service";
        };
      };

      systemd.services.startaste-dashboard = lib.mkIf cfg.dashboard.enable {
        description = "startaste dashboard";
        wantedBy = [ "multi-user.target" ];
        after = [ "network.target" ];
        inherit environment;
        serviceConfig = common // {
          ExecStart = lib.escapeShellArgs [
            "${cfg.package}/bin/startaste"
            "serve"
            "--host"
            cfg.dashboard.listenAddress
            "--port"
            (toString cfg.dashboard.port)
          ];
          Restart = "on-failure";
          RestartSec = 5;
        };
      };
    }
  );
}
