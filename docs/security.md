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
