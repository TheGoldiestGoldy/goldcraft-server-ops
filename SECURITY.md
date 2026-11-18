# Security policy

Do not report live server addresses, authentication tokens or player data in public issues.

If a secret is committed:

1. rotate or revoke it immediately;
2. remove it from current files;
3. treat Git history as compromised;
4. rewrite history only after preserving a private backup;
5. verify dashboard, tunnel and GitHub credentials separately.

This repository intentionally stores hashes and sanitized aggregates instead of raw logs or binaries.
