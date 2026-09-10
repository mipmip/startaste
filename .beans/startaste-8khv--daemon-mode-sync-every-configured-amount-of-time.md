---
# startaste-8khv
title: Daemon mode, sync every configured amount of time
status: todo
type: task
priority: normal
created_at: 2026-05-12T11:18:05Z
updated_at: 2026-09-10T15:06:48Z
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
