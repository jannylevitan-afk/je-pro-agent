# Smoke Instructions

Smoke flows are read-only by default.

Allowed default smoke:

- import core contracts;
- instantiate fixture objects;
- verify dry-run contracts;
- read stable public fixture IDs from env.

Forbidden default smoke:

- real publishing;
- real payments;
- live writes;
- deleting records;
- scraping private or login-only content;
- mutating production systems.

Stateful smoke must be explicitly marked dangerous and excluded from CI by default.
