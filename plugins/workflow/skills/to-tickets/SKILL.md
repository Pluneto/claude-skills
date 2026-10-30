---
name: to-tickets
description: Break a saved plan, a spec, or the current conversation into tracer-bullet tickets, each declaring its blocking edges, as local files under plans/ or issues on the repo's tracker. For work that spans sessions or parallel agents.
disable-model-invocation: true
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

**Tracker:** follow `docs/agents/issue-tracker.md` (setup-pluneto-skills writes it): it says where tickets go and which labels mark them. When the repo has none, read [no-tracker-doc.md](no-tracker-doc.md) before publishing.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. If the user passes a reference (a `plan-*.md` path, a spec path, an issue number or URL) as an argument, fetch it and read all of it, with any comments. A plan from plan-this is agreed: its decisions are settled, and its milestones, done-when checks and Needs from you are the starting material for the slices.

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

### 4. Quiz the user

When the source is an agreed plan file, skip the questions: its interview already settled the work. Show the breakdown below in one message and go on to step 5.

Otherwise, present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Who**: agent or human
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Publish the tickets to the configured tracker

Publish the approved tickets. **How** depends on the tracker (see Tracker above); the tickets are the same either way, only the shape of the blocking edges changes:

- **Local files** → write one file per ticket under `plans/<feature-slug>/tickets/<NN>-<slug>.md`, numbered from `01` in dependency order (blockers first). Each file's `Who:` line says agent or human, and its `Blocked by:` lists the numbers it depends on. Use the per-ticket file template below: one ticket per file, never a single combined file.
- **GitHub Issues** → publish one issue per ticket in dependency order (blockers first) so each ticket's blocking edges can reference real issue numbers. Give each issue the tracker doc's agent or human label, and use native blocking (the tracker doc's **Blocking**), falling back to the "Blocked by" section only where it isn't available. If the source was an existing issue, make each ticket its sub-issue (tracker doc's operation).

Work the **frontier**: any ticket whose blockers are all done. For a purely linear chain that means top to bottom.

Do NOT close or modify any parent issue.

Finish with the published list (number or file, title, agent/human, blocked by) and the exact line to run next:

- `/build-this <tickets folder>` or `/build-this issues #<first>-#<last>`: one session works them in blocker order, skipping human tickets.
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
