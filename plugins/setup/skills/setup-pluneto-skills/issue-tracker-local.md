# Issue tracker: local Markdown

Plans, tickets and wayfinder maps for this repo live as Markdown files under `plans/`. This is also the default when this file is missing.

## Conventions

- One feature or effort per folder: `plans/<slug>/`.
- Tickets: one file per ticket at `plans/<slug>/tickets/NN-<slug>.md`, numbered from `01` with blockers first, never one combined file.
- Each ticket starts with `Blocked by: NN, NN` (or `None`) and `Status: open|claimed|resolved` lines; wayfinder tickets add `Type: research|prototype|interview|task`.
- Answers go under an `## Answer` heading; discussion appends under `## Comments`.

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
