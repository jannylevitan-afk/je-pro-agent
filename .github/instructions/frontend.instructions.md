# Frontend Instructions

Canonical docs:

- `AGENTS.md`
- `docs/README.md`
- `docs/runbooks/validation-and-deploy.md`

Applies to future admin or frontend paths:

- `apps/admin/**`
- `apps/web/**`
- `frontend/**`
- `public/**`
- `index.html`

Local invariants:

- The UI is an Admin Operating Hub for final review-ready assets.
- Do not expose internal pipeline mechanics unless the product spec asks for it.
- Long content must be readable and copyable.
- Browser-sensitive changes require real-browser verification.
- Do not add remote fonts, CDNs, or external dependencies unless an ADR approves it.

Validation:

```bash
make check
```

For browser-sensitive flows, also record the browser target and manual checks in
the final handoff.
