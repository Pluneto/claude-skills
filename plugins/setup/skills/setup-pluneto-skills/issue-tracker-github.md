# Issue tracker: GitHub

Tickets and wayfinder maps for this repo live as GitHub issues. Plans stay as files under `plans/`. Use the `gh` CLI for every operation; it infers the repo from `git remote -v`.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`, with a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --json number,title,body,labels,comments`.
- **List issues**: `gh issue list --state open --json number,title,labels` with `--label` and `--state` filters.
- **Sub-issue of a parent**: `gh issue create --parent <parent> ...`, or `gh issue edit <parent> --add-sub-issue <child>` (gh 2.94+). Without sub-issues, put `Part of #<parent>` at the top of the child body.
- **Comment**: `gh issue comment <number> --body "..."`.
- **Labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`.
- **Close**: `gh issue close <number> --comment "..."`.
- **Blocking**: GitHub's native issue dependencies: `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where the database id comes from `gh api repos/<owner>/<repo>/issues/<n> --jq .id` (not the `#number`). Without dependencies, a `Blocked by: #<n>, #<n>` line at the top of the body. A ticket is unblocked when every blocker is closed.

## When a skill says "publish to the issue tracker"

Create a GitHub issue.

## When a skill says "fetch the relevant ticket"

Read it as in **Read an issue**.

## Wayfinding operations

Used by `/wayfinder`. The map is one issue with child issues as tickets.

- **Map**: an issue labelled `wayfinder:map` (`gh issue create --label wayfinder:map`).
- **Child ticket**: a sub-issue of the map, labelled `wayfinder:<type>` (`research`, `prototype`, `interview`, `task`).
- **Frontier**: the map's open children with no open blocker (`issue_dependencies_summary.blocked_by` is 0, or every issue in the `Blocked by` line is closed) and no assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, `gh issue close <n>`, then append a context pointer (gist + link) to the map's Decisions so far.
