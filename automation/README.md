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
