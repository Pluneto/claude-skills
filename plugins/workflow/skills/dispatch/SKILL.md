---
name: dispatch
description: Group a repo's open agent tickets into waves of parallel workers, write a tracking issue with one self-contained prompt per ticket, and launch a wave when you say so.
argument-hint: "[issue numbers]"
disable-model-invocation: true
---

# Dispatch

Run several workers on one repo at once without them colliding. Dispatch plans **waves**: tickets in one wave touch no shared hotspot, so their PRs merge cleanly; anything that would collide waits for a later wave. Each worker gets a **self-contained prompt** that works in a Claude or a Codex thread, because it names no skill and carries every command it needs.

Dispatch plans and launches; it never builds a ticket itself. It writes to the tracker only in steps 6–8 (the tracking issue, its loose ends, launches and ticks), and opens a PR only when the user asks for the areas map.

`docs/agents/issue-tracker.md` is the source for label names, the Claim and Release commands and the Parallel work fields. Read it whole first; every step below uses it.

## Steps

1. **Check the tracker.** Read `docs/agents/issue-tracker.md`. When it is missing or describes the local tracker, stop: parallel workers need the GitHub tracker, because local claims live in each worktree and stay invisible to other threads until they merge. Suggest one `/build-this` thread on the tickets instead, and `/setup:setup-pluneto-skills` to switch trackers. Done when the doc is a GitHub tracker and you have its agent, human and claim label names, Max workers, Land command, Land status command and Areas map path (blank fields mean their fallbacks).

2. **List the tickets.** `gh issue list --state open --label "<agent label>" --json number,title,body,url --limit 200` (only the issues the user named, when they named some). For each, run the doc's winner command: a ticket with a live claim is taken; leave it out of the waves. Get each ticket's open blockers (the doc's **Count open blockers**, or its `Blocked by` line). List the open `<human label>` issues separately. Done when every open agent ticket is marked free or taken, with its open blockers.

3. **Map the areas.** Read the Areas map when it exists: areas → paths, **hotspots** (files many tickets edit, such as generated types, shared registries, lockfiles, top-level docs) and **shared functions** (for example SQL functions several migrations redefine). Without it, infer them: hotspots are the files that show up in many merges in `git log --name-only --format='--%h %s' -n 300` (count the distinct commits per file), and areas are the folders the tickets' text points at. For each free ticket, from its title and body, write down the areas it touches and the hotspots and shared functions it is likely to edit. When unsure, count the hotspot as touched: a later wave costs minutes, a conflict costs a human. Done when every free ticket has its areas, hotspots and functions, each marked "map" or "inferred".

4. **Plan the waves.** Take the free tickets in blocker order, then by number. Put each in the first wave that comes after the waves of all its blockers in this batch, holds no ticket sharing a hotspot or shared function with it, and has fewer than Max workers tickets. Sharing an area alone is fine: different files merge cleanly. A ticket whose open blocker is outside the batch goes in no wave; list it as blocked. Done when every free ticket is in exactly one wave or listed as blocked, and no wave holds two tickets that share a hotspot or function.

5. **Write the prompts.** For each waved ticket, fill [worker-prompt.md](worker-prompt.md) with: the repo (`gh repo view --json nameWithOwner,defaultBranchRef`), the issue, the branch `t3/<n>-<slug>` (slug: two to four lowercase key words of the title, hyphenated, dropping articles and prepositions: `t3/41-sponsor-entity`), its areas and hotspots, the doc's Claim and Release commands with this issue's number and the doc's label names filled in, the check commands the repo's `AGENTS.md` names (else its package scripts or Makefile targets), and the Land command and status command, or their fallback. Done when `grep -nE 'CLAUDE\.md|(^|[[:space:]])/[a-z][a-z-]*([[:space:]]|$)|(workflow|engineering|skill-tools|design|setup):[a-z-]+|[Ss]kill[[:space:]]' <prompts>` has no hit left that tells the worker to load a skill, run a slash command or read `CLAUDE.md`: a Codex worker can do none of these. Review each hit: one inside the repo name, a path or a check command is fine; rewrite the rest as the plain command or rule.

6. **Write the tracking issue.** Create one issue titled `Batch YYYY-MM-DD` (add ` (2)` when that title exists), with no labels. Body: one checklist per wave (`- [ ] #<n> <title> · <areas> · waits on #<m>`), then the blocked, taken and human tickets with one line each, then each ticket's prompt in a fenced block under a `### #<n>` heading. Done when the issue exists and every waved ticket has its checklist line and its prompt.

7. **List the loose ends.** **Stale claims**: open issues with the claim label whose winning claim comment is more than a day old and that have no open PR (no `gh pr list --state open --json number,headRefName,body` entry whose branch starts with `t3/<n>-` or whose body says `#<n>`); give each its release command from the doc. A claim label with no live claim is stale too. **Areas map**: when step 3 inferred anything, offer to open it as a docs-only PR (`docs/agents/areas.md` on a `docs/areas-YYYY-MM-DD` branch, `gh pr create`; CI usually skips docs, and the user merges it). Done when both lists are in the tracking issue (or "none").

8. **Wait for the word, then launch.** End with a plain message, not a question tool (a question card in a T3 thread breaks when the user types into the thread): the waves as a table, the tracking issue link, the loose ends, and the replies that act: `launch wave <N>` (add `merge if green` to let workers merge, and `#<n> on codex` to pick a provider per ticket), or `open the map PR`. Launch nothing until the user replies `launch wave <N>`. Then:
   - A wave starts once every ticket in earlier waves is closed. When some are open, name them and wait.
   - Tick the closed tickets' lines in the tracking issue.
   - For each ticket in the wave, run the winner command again (skip it if it is now taken), then start a thread with T3's `t3_thread_launch` tool: the ticket's prompt (with `merge if green` as its last line when the user said so), a worktree strategy on the default branch (`baseRef` the default branch, `branch` the ticket's `t3/<n>-<slug>`, `startFromOrigin: true`), the title `#<n> <title>`, and the provider the user named (default: Claude (pool)). Follow the tool's own schema for the exact field names.
   - When `t3_thread_launch` isn't available, say so, and point to the prompts in the tracking issue: the user pastes each into a new thread on its branch.

   Done when every ticket in the wave has a thread id recorded as a comment on the tracking issue, or the user has been pointed to the prompts. Then wait for the next reply (`launch wave <N+1>`, or `status` to re-tick the tracking issue).
