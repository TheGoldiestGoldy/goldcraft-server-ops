# Security

Live addresses, credentials, authentication mode, access-control state and firewall rules are private operational data. They are deliberately absent from this public repository.

## Public operating rules

1. Keep credentials and control tokens outside the repository.
2. Keep raw logs, player records, UUIDs, IP addresses and account caches private.
3. Distribute the Minecraft connection address only through the intended community channel.
4. Review authentication, admission control and firewall exposure privately before changing network access.
5. Keep the dashboard control API protected by a bearer token; the public status endpoint remains read-only.
6. Review mod, resource-pack and shader redistribution licences before publishing archives.
7. Run the repository sanitizer and validation checks before every public update.

## Reporting

Report security problems privately through the repository's security policy. Do not open a public issue containing a live address, token, player identity or exploit procedure.

## Dashboard same-origin security review (26 November 2026)

The dashboard UI and API are served from the same loopback bridge origin. The public `/public` endpoint is read-only. Owner endpoints `/status`, `/logs`, `/start` and `/stop` require the bearer token. The owner token is stored in the browser's localStorage by the UI; use a trusted browser profile and do not use a shared/public browser. Log output can contain player information and must not be pasted into public issues.

The 26 November draft follow-up makes these boundaries explicit in code:

1. The service worker caches only a fixed list of static UI assets. Dynamic status, log and download requests bypass Cache Storage; the cache version bump removes the previous broad cache.
2. The HTML and static-response CSP restrict connections to the same origin.
3. Wildcard CORS and the unused OPTIONS handler are removed because the UI and API are same-origin.
4. Public status omits the server PID and network port. The public properties reader is limited to max players and view/simulation distance.
5. The bounded `/logs` route remains behind bearer authorization and returns no-store JSON.
6. Browser download links are restricted to the same-origin, seven-file archive allowlist enforced by the bridge. The repository validator checks that the browser and bridge allowlists stay identical; invalid inventory URLs are rendered as unavailable rather than clickable links.

These changes are in a stacked draft pull request, not deployed. The running host was not modified during this audit. Recheck the deployed bridge and service worker after a deliberate maintenance-window rollout.
