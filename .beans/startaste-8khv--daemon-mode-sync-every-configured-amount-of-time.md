---
# startaste-8khv
title: Daemon mode, sync every configured amount of time
status: completed
type: task
priority: normal
created_at: 2026-05-12T11:18:05Z
updated_at: 2026-09-10T15:38:09Z
---

Decision from exploring this: do NOT build an interval loop into the
application. `startaste sync` is already the perfect oneshot — wrap it in a
`Type=oneshot` unit plus a `systemd.timer`.

systemd then provides the interval, restart-with-backoff, journald logging,
survival across reboots, and refusal to start a second run while one is still
going. That last point is the single-instance lock we would otherwise have to
write. The pattern is already in use on the target host:
`systemd.timers.git-sync-secondbrain` in
`mipnix/modules/HOSTS/dapperehaan-server/linny-mcp.nix`
(`OnBootSec` + `OnUnitActiveSec`).

So this bean is mostly nix work and belongs with [[startaste-zrap]]; the
application side is close to zero:

- confirm `startaste sync` exits non-zero on failure so `Restart=on-failure`
  and journald see it (config errors already `SystemExit`; an HTTP error
  currently propagates as a traceback — cosmetics tracked in
  [[startaste-gpvq]])
- decide the interval (HN upvotes and GitHub stars change slowly; hourly is
  generous)

Deliberately deferred: a portable `--interval` flag for people without systemd
(docker, macOS). Not needed for this deployment; revisit if startaste is ever
packaged for non-systemd users.

## Summary of Changes

Satisfied by openspec change `nixos-service-module` (archived
`openspec/changes/archive/2026-09-10-nixos-service-module`, commit `119a423`),
which is where the decision recorded above landed: no interval loop in the
application.

`services.startaste.sync.enable` creates a `Type=oneshot` unit running
`startaste sync`, and `sync.interval` (default `1h`) drives its timer. systemd
supplies the schedule, `OnBootSec` catch-up, journald logging, and refusal to
start an overlapping run. Verified in a NixOS VM test: the timer is scheduled,
and a run without credentials exits non-zero with the clear error and no
traceback.

No Python was needed. The portable `--interval` flag for non-systemd users stays
deferred, as recorded above.

Configured per host in `mipnix` change `deploy-startaste-dapperehaan`, group 3.
