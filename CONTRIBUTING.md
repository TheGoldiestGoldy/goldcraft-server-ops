# Contributing and experiment discipline

Every operational change should answer:

- What exact problem is being tested?
- What is the baseline?
- What single variable changes?
- What measurement decides success?
- How is rollback performed?

For experiments, create a dated Markdown file under docs/experiments with:

1. hypothesis;
2. confirmed starting facts;
3. changed files and values;
4. test duration and player layout;
5. measured results;
6. conclusion;
7. rollback status.

Do not commit raw player logs, IPs, chat, credentials, world files, mod JARs, resource-pack archives or shader binaries.
