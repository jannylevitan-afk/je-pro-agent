# Isolated Repo Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the current folder into a standalone repository with a clean starter structure and preserved reference materials.

**Architecture:** The folder itself becomes the repo root, documentation is separated from future implementation, and the existing HTML architecture file is preserved under `docs/architecture/`. Git is initialized only inside this folder, so nothing overlaps with any other repository.

**Tech Stack:** Git, Markdown, static HTML

---

### Task 1: Create the starter project files

**Files:**
- Create: `.gitignore`
- Create: `README.md`
- Create: `docs/notes/README.md`
- Create: `docs/superpowers/specs/2026-04-24-isolated-repo-setup-design.md`
- Create: `docs/superpowers/plans/2026-04-24-isolated-repo-setup.md`

- [ ] **Step 1: Write the starter files**

Add a minimal `.gitignore`, a root `README.md`, a notes README, and the setup documentation files listed above.

- [ ] **Step 2: Verify the files exist**

Run: `find . -maxdepth 4 -type f | sort`
Expected: output includes `.gitignore`, `README.md`, and the new files under `docs/`

### Task 2: Preserve the architecture reference file

**Files:**
- Move: `content_engine_architecture_v2.html`
- Create: `docs/architecture/content_engine_architecture_v2.html`

- [ ] **Step 1: Create the destination folder**

Run: `mkdir -p docs/architecture`
Expected: folder exists at `docs/architecture`

- [ ] **Step 2: Move the HTML reference file**

Run: `mv content_engine_architecture_v2.html docs/architecture/content_engine_architecture_v2.html`
Expected: root no longer contains the HTML file and `docs/architecture/` does

### Task 3: Prepare empty working directories

**Files:**
- Create: `assets/.gitkeep`
- Create: `src/.gitkeep`

- [ ] **Step 1: Add gitkeep placeholders**

Create empty placeholder files so Git tracks the folders `assets/` and `src/`.

- [ ] **Step 2: Verify the folders exist**

Run: `find assets src -maxdepth 2 -type f | sort`
Expected: output includes `assets/.gitkeep` and `src/.gitkeep`

### Task 4: Initialize the standalone git repository

**Files:**
- Create: `.git/`

- [ ] **Step 1: Initialize git in the current folder**

Run: `git init`
Expected: output confirms an empty Git repository was initialized in this folder

- [ ] **Step 2: Verify isolation**

Run: `git status --short`
Expected: output lists only files from this folder and no files from other projects

- [ ] **Step 3: Make the first intentional commit**

Run:

```bash
git add .
git commit -m "chore: initialize isolated project repository"
```

Expected: a first commit containing only this project's starter files
