---
name: to-tickets
description: Break a saved plan, a spec, or the current conversation into tracer-bullet tickets, each declaring its blocking edges, as local files under plans/ or issues on the repo's tracker. For work that spans sessions or parallel agents.
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

**Tracker:** follow `docs/agents/issue-tracker.md` (setup-pluneto-skills writes it): it says where tickets go and which labels mark them. When the repo has none, read [no-tracker-doc.md](no-tracker-doc.md) and ask its tracker question before publishing, also for an agreed plan file: no plan says where its tickets go.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a `plan-*.md` path, a spec path, an issue number or URL) as an argument, fetch it and read all of it, with any comments. A plan from plan-this is agreed: its decisions are settled, and its milestones, done-when checks and Needs from you are the starting material for the slices.

Read the tracker too, so step 4 can find tickets that already cover the work:

- **GitHub**: every open issue, `gh issue list --state open --limit 1000 --json number,title,labels,assignees,body`, plus the issues closed in the last 30 days (same fields, `--state closed --search "closed:>=<date 30 days ago>"`). Keep the first ~300 characters of each body. When 1000 come back, the list is cut off: in step 4, also run 2-3 `gh search issues "<phrasing>" --state open` per draft.
- **Local**: every ticket file under `plans/*/tickets/`, whatever its `Status:` (open, claimed or resolved).

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

Mark each ticket **agent** or **human**. **Human** when the user must do its core work: a console step, a decision, a physical action. **Agent** otherwise, also when the agent only needs the user's go or one reply along the way; name that step under **Needs you** in the ticket. For an agreed plan file, take the split from its "Needs from you" section.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Check the tracker for matches

First fold the batch into itself: when two drafts deliver the same outcome, merge them into one draft with both sets of acceptance criteria.

Then, for each draft, shortlist the step 1 tickets that look like the same work, read each candidate in full (GitHub: body and comments; local: the whole file), and sort the closest one with the **outcome test**:

- **duplicate**: finishing the existing ticket would also deliver this draft.
- **overlap**: the existing ticket delivers part of the draft; the rest is missing.
- **related**: same area, different outcome.
- **new**: no candidate passes. The source issue (when the source is an existing issue) is never a candidate.

When a match sits between two classes, take the weaker one (related over overlap, overlap over duplicate): the user confirms each match in step 5, and a weaker class loses no work.

Record the existing ticket's state. **Claimed**: on GitHub, it has an assignee, the `in-progress` label, or a `claimed by` comment with no `released:` comment after it (the tracker doc's claim rule); locally, `Status: claimed`. **Done**: closed (GitHub) or `Status: resolved` (local). **Open**: anything else. The class and the state give the action:

| Class | Existing ticket | Action in step 6 |
|---|---|---|
| duplicate | open or claimed | skip the draft; point to the existing ticket |
| duplicate | done | skip the draft; report "already done in <ticket>" |
| overlap | open | **append**: add the missing acceptance criteria to the existing ticket |
| overlap | claimed or done | **delta ticket**: create a ticket for only the missing part, blocked by the existing one when it is claimed, with a `Related:` line when it is done |
| related | any | create the draft with a `Related: <ticket>` line, or a blocked-by edge on the existing ticket when the draft needs it done first |
| new | | create the draft |

Claimed tickets are never rewritten and done tickets are never reopened: someone else owns them. When a skipped draft blocked another draft, point that edge at the existing ticket (drop it when that ticket is done).

Done when every draft has a class, its target ticket (or "new") and its action.

### 5. Quiz the user

When the source is an agreed plan file, skip the breakdown questions below (not the tracker question): its interview already settled the work. Show the breakdown below in one message and go on to step 6, except when step 4 found at least one match: then ask the match question below first.

Otherwise, present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Who**: agent or human
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work
- **Match**: the step 4 class, existing ticket and action (`overlap #12 → append`), or `new`

**Match question**, whenever step 4 found a match, also for an agreed plan file: one question asking the user to confirm the matched rows, naming any to reject. A rejected match turns that draft back into a new ticket.

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 6. Publish the tickets to the configured tracker

Run each draft's step 4 action: make the appends, then publish the tickets to create (new, related and delta tickets).

**Append**: just before writing, re-read the existing ticket's claim state; when it is now claimed, create a delta ticket instead. Add a section to the end of its body, keeping everything above it:

```
## Added from <source plan, spec or issue> (<YYYY-MM-DD>)

- [ ] Missing acceptance criterion
```

On GitHub, save the body (`gh issue view <n> --json body --jq .body`), add the section and write it back with `gh issue edit <n> --body-file <file>`. Locally, append it to the ticket file.

**How** to publish depends on the tracker (see Tracker above); the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `plans/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's `Who:` line says agent or human, and its `Blocked by:` lists the numbers it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **GitHub Issues** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real issue numbers. Give each issue the tracker doc's agent or human label, and use native blocking (the tracker doc's **Blocking**), falling back to the "Blocked by" section only where it isn't available. If the source was an existing issue, make each ticket its sub-issue (tracker doc's operation).

Do NOT close or modify any parent issue.

A `Related:` line goes at the top of the body, under the title. A local edge or `Related:` line to a ticket in another folder names its path.

Finish with the published list (number or file, title, agent/human, blocked by), one line per appended or skipped draft naming its existing ticket, the counts (`created N, merged N, skipped N`: merged counts appends, skipped counts duplicates), and the exact line to run next:

- `/build-this <tickets folder>` or `/build-this issues <first>-<last>` (bare numbers: T3's composer turns a typed `#<n>` into a pull-request chip): one session works them in blocker order, skipping human tickets.
- On GitHub, when two or more agent tickets can run at the same time, also offer `/dispatch`: it groups them into waves of parallel workers.

<local-ticket-template>

# <NN>: <Ticket title>

Who: agent | human
Blocked by: the numbers of the tickets that gate this one, or None
Status: open

**What to build:** the end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

**Needs you:** the step where an agent ticket waits on the user (a go, a reply), or omit.

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

</local-ticket-template>

<issue-template>

The agent or human label carries Who; the body has no Who line.

## Parent

A reference to the parent issue on the tracker (if the source was an existing issue, otherwise omit this section).

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not layer-by-layer implementation.

## Needs you

The step where an agent ticket waits on the user (a go, a reply). Omit when there is none.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Blocked by

- A reference to each blocking ticket, or "None (can start immediately)". Omit this section when blockers were set as native edges.

</issue-template>

In either form, avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
