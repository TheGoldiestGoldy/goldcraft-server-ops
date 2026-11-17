# Contributing and experiment discipline

Every submitted experiment should answer:

- What exact problem was tested?
- What was the sanitized baseline?
- What single variable changed?
- What aggregate measurement decided success?
- Was rollback required?

For experiments, create a dated Markdown file under `docs/experiments` containing:

1. hypothesis;
2. confirmed starting facts;
3. generalized changed settings;
4. test duration and coarse player layout;
5. aggregate measured results;
6. conclusion;
7. rollback status.

Never commit real names, player handles, emails, UUIDs, IP addresses, chat, private messages, credentials, machine-specific paths, hostnames, server addresses, world seeds, exact coordinates, raw logs, crash reports, world files, control code, private configuration, mod JARs, resource-pack archives or shader binaries.

Use labels such as Player A and coarse regions rather than identifiers or exact locations. If evidence cannot be adequately anonymized, keep it in the private operations archive and publish only the conclusion.
