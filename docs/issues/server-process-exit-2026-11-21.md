# Server process disappearance after console-input error — 21 November 2026

**Status:** unresolved. A process absence and console-input exception are confirmed; a Minecraft crash or causal relationship is not.

## Observations

- The latest server log was last modified at 23:44:57 UTC on 21 November.
- The log records startup completion at 22:56:15 UTC, followed later by a player disconnect and a server-console-handler `java.io.IOException: Input/output error`.
- No explicit clean-stop marker appears in the latest log.
- At 04:05 UTC on 22 November, no Java server process was present. The dashboard control bridge remained active.
- The newest crash-report file in the crash-report directory is dated 1 November; no report corresponding to this 21 November event was present.
- No OOM or systemd-oomd event was found in the host journal window from 23:30 to 00:10 UTC.
- The world data and Distant Horizons SQLite store had file writes around 23:44:57 UTC. This establishes write activity, not a fully completed or verified clean save.

## Interpretation

The console-input exception is an observed event. It does **not** establish that the exception caused the Java process to exit, that the process crashed, or that the world was corrupted. The absence of a clean-stop marker means the event should not be described as a confirmed graceful shutdown either.

## Evidence still needed

1. Correlate the Minecraft child PID with the dashboard bridge's process-ownership and launcher logs.
2. Inspect the launcher's stdin/console-pipe lifetime and determine whether the input stream can close independently of the server process.
3. Correlate the exact process-exit time with systemd user-session, kernel and cgroup journals.
4. Before any future restart or maintenance, confirm the latest world save and backup state.

No production process, world or configuration was changed during this audit. Raw logs, player identifiers, addresses and coordinates are intentionally not reproduced here.
