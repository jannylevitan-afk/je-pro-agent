# Isolated Repo Setup Design

## Goal

Turn this folder into a fully separate project repository so it does not intersect with any existing repositories, branches, or project histories.

## Decisions

- Use the current folder as the repository root.
- Keep the existing HTML file as a reference artifact instead of mixing it into future app code.
- Start with a small neutral structure that supports documentation, assets, and future implementation.
- Avoid worktrees or branches tied to other repositories.

## Initial Structure

- `README.md` for project orientation
- `.gitignore` for common local clutter
- `docs/architecture/` for the existing architecture HTML
- `docs/notes/` for project notes
- `docs/superpowers/specs/` for this design record
- `docs/superpowers/plans/` for setup planning
- `src/` for future implementation
- `assets/` for images and static files

## Why This Works

This approach gives the project its own `.git` directory, its own remote on GitHub, and its own collaborator access settings. That keeps the friend's project operationally separate from all other repositories while still making it easy to share by link later.
