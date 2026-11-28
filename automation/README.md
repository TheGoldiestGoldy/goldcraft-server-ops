# Dashboard automation

These are sanitized copies of the scripts currently used by the Goldcraft dashboard.
They are included for auditability and disaster recovery; changing a copy here does
not change the live service until it is deliberately installed.

## Components

- `start-server.sh` starts the Fabric server with Java 21, a 4-12 GiB heap and
  Generational ZGC. It prevents duplicate launches and refuses to start if the
  configured port is already occupied.
- `bridge.py` exposes authenticated status, start and graceful-stop operations to
  the dashboard. Its bearer token is read at runtime from
  `~/.config/goldcraft-control/token`; no token is stored in this repository.
- `inventory.py` scans the active PollyMC instance, builds client download archives
  and writes the public inventory JSON.
- `profiles.py` builds the three hardware-targeted client profiles and validates their
  Fabric dependencies.
- `systemd/` contains templates for the user services and daily inventory timer.

## Installation notes

The Python scripts derive the account home directory at runtime. The systemd files
are documentary templates: replace every `<HOME>` with the absolute home directory
before installing them under `~/.config/systemd/user/`.

Keep the live token file mode at `0600`. Do not expose the bridge directly to the
public internet; place it behind the existing authenticated HTTPS proxy/tunnel. The
bridge controls the Minecraft process only. It cannot power on a fully shut-down PC.

After installation, validate and enable the units with:

```bash
systemd-analyze --user verify ~/.config/systemd/user/goldcraft-*.service ~/.config/systemd/user/goldcraft-inventory.timer
systemctl --user daemon-reload
systemctl --user enable --now goldcraft-control.service goldcraft-inventory.timer
```


## OS update and memory-sampling status (21 November 2026)

The daily 07:00 root-owned OS update service is **not installed**. The host-side draft and privileged installer were not installed or end-to-end tested; the system timer was reported as not found. These files are not copied here because they contain machine-specific paths and have not passed installation/reboot/failure-path validation. Do not treat OS updates or automatic post-update reboot/restart as active.

The separate user-level server boot-start unit is enabled. Three observed runs on 20, 21 and 23 November requested the dashboard start and confirmed that the server accepted connections. The 23 November process and listener remained present at 04:35 UTC. This is not a complete reboot/update recovery certification.

The temporary memory sampler timer is disabled. Its 16 observations had zero PSS values throughout and its host-memory estimate was MemTotal minus MemAvailable. The script is not published as a supported tool until its PSS collection and field semantics are corrected and tested.


## Historical observed host state (22 November 2026)

- `goldcraft-inventory.timer` is enabled and its latest daily run completed successfully at 00:02:19 UTC. The run published a 100-mod client inventory, 14 resource-pack entries (12 active), 2 shader packs and three generated profile archives. systemd reported a 2.9 GiB peak for the inventory job.
- `goldcraft-server-boot.service` is enabled. Three observed invocations on 20, 21 and 23 November confirmed the server accepting connections; this one-shot unit does not supervise it continuously. At 04:05 UTC on 22 November no Java server process was present, while the 23 November post-boot audit found the process and listener still present at 04:35 UTC.
- `arch-update.timer` is enabled, but `arch-update.service` runs `arch-update --check`. The command's help defines this as a notification check, not package installation.
- The separate root-owned `goldcraft-daily-upgrade.timer` and service are not installed in the system or user systemd unit paths. Draft local source files have not been installed or end-to-end tested. Do not claim the requested 07:00 unattended OS upgrade/reboot workflow is active.
- The temporary memory sampler timer is disabled. Its earlier PSS values were all zero, so those samples are not usable process-memory measurements.


## Observed host state (23 November 2026)

- The daily inventory timer remains enabled. Its 23 November run completed successfully at 00:02:49 UTC, refreshing the 100-mod client inventory, 14 resource-pack entries (12 active), two shader packs and three profile archives.
- The enabled boot-start helper ran after the 02:12:07 UTC host boot. It requested a Minecraft start at 02:12:18 and confirmed the server accepting connections at 02:12:42; the process remained present at 04:35 UTC. This is the third successful observed invocation, not a continuous supervisor or an update/reboot recovery test.
- The server startup log confirms VSS request processing and LOD store initialization. This is runtime service initialization, not proof of client transfers or acceptable performance.
- SeedGen 0.9.1 emitted two DH 3.3.3 mixin compatibility warnings and ambiguous LOD-generation messages. See the LOD issue record before changing DH, VSS or SeedGen settings.
- arch-update.timer still invokes arch-update --check only. No root-owned daily upgrade unit is installed.
- The memory sampler timer remains disabled because its previous PSS measurements were invalid. No new TPS, MSPT, FPS or player-load benchmark was collected.

## Dashboard console and same-origin API

The bridge serves an allowlisted static dashboard from the same loopback origin as its API. `/public` is read-only; `/status`, `/logs`, `/start` and `/stop` require the bearer token. The log route returns at most 500 lines from a bounded tail of the current Fabric log and uses no-store JSON. The bridge binds to loopback; do not expose it directly.

The owner console polls logs only while open and stops polling when closed. The browser stores the owner token in localStorage, so use a trusted browser profile. The proposed hardening removes wildcard CORS, omits PID/port from public status, applies a same-origin CSP, and makes the service worker cache static assets only. These changes are in a draft pull request and have not been installed on the live host.
