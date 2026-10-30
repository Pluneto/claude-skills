# Issue tracker: local Markdown

Plans, tickets and wayfinder maps for this repo live as Markdown files under `plans/`.

Local tickets live in each worktree's `plans/`, so a claim is invisible to other threads until it merges: this tracker supports **one build-this thread at a time**, not parallel workers or dispatch. Parallel work needs the GitHub tracker.

## Ticket lines

Where a GitHub tracker uses labels, local tickets use header lines. Each ticket file starts with:

- `Who: agent|human`: `agent` when an agent can build it unattended, `human` when it needs the user (a console step, a decision, a physical action).
- `Blocked by: NN, NN` (or `None`).
- `Status: open|claimed|resolved`. `claimed` plays the role of the claim label.
- Wayfinder tickets add `Type: research|prototype|interview|task`, which plays the role of the `wayfinder:<type>` label; the map file plays the role of `wayfinder:map`.

## Conventions

- One feature or effort per folder: `plans/<slug>/`.
- Tickets: one file per ticket at `plans/<slug>/tickets/NN-<slug>.md`, numbered from `01` with blockers first, never one combined file.
- Answers go under an `## Answer` heading; discussion appends under `## Comments`.
- **Claim**: set `Status: claimed` and save before any work. **Release**: set `Status: resolved` when done, or back to `open` when abandoned.

## When a skill says "publish to the issue tracker"

Create the file under `plans/<slug>/` (creating the folder if needed).

## When a skill says "fetch the relevant ticket"

Read the file at the given path.

## Wayfinding operations

Used by `/wayfinder`. The map is a file with one child file per ticket.

- **Map**: `plans/<effort>/map.md` (Destination, Notes, Decisions so far, Not yet specified, Out of scope).
- **Child ticket**: `plans/<effort>/tickets/NN-<slug>.md`, with the question in the body.
- **Blocking**: the `Blocked by:` line. A ticket is unblocked when every ticket it lists is `resolved`.
- **Frontier**: the files in `plans/<effort>/tickets/` that are open, unblocked and unclaimed; lowest number first.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under `## Answer`, set `Status: resolved`, then append a context pointer (gist + link) to the map's Decisions so far.
