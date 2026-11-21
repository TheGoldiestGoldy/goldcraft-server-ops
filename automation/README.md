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

The separate user-level server boot-start unit is enabled. One observed run on 20 November requested the dashboard start and confirmed that the server accepted connections. This is a successful single run, not a complete recovery certification.

The temporary memory sampler timer is disabled. Its 16 observations had zero PSS values throughout and its host-memory estimate was MemTotal minus MemAvailable. The script is not published as a supported tool until its PSS collection and field semantics are corrected and tested.
