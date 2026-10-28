---
name: skill-ozempic
description: Slim down a bloated skill. Confirms its purpose, proposes numbered cuts with pros and cons, and hands the approved cuts to skill-updater.
disable-model-invocation: true
---

# Skill Ozempic

Take an existing skill and remove everything that doesn't earn its place, without changing what the skill is for. A leaner skill costs less context on every trigger and is easier for the model to follow, because the instructions that matter aren't buried.

The user decides every cut. Your job is to find them and make the trade-offs visible.

## Steps

### 1. Read the whole skill

Find the target skill by name (Glob for `**/<name>/SKILL.md`, check `/mnt/skills/`, or the skills list). Read its SKILL.md and every bundled file (scripts, references, assets) it points to. You can't judge what is bloat without seeing all of it. If you can't find it, ask where it is.

### 2. State the purpose and get agreement

Tell the user, in two or three sentences, what the skill is for: the job it does and when it should trigger. Add one line on what it must keep doing after the diet. Then stop and wait for a yes or a correction.

This comes first because the purpose is the yardstick for every cut. If you and the user disagree about what the skill is for, every suggestion after that is wasted.

### 3. Suggest cuts

First invoke the **writing-for-agents** skill (in Claude Code, call the Skill tool with `writing-for-agents`) if available: hunt its no-ops, duplication, sediment and restated identity in the description.

Once the purpose is confirmed, suggest removing as much as possible while keeping that purpose working. Be bold: the user can say no, and a timid list defeats the point. Number each suggestion and order them by biggest saving first. For each one give:

- **Cut:** what goes, and where it lives (section, bullet, file), with the approximate saving
- **Pros:** what gets better
- **Cons:** what could get worse or break, stated honestly

Typical fluff worth looking for:

- Instructions repeated in several places
- Explanations of things the model already knows
- Shouting (MUST, ALWAYS, NEVER) with no reason attached; keep the reason, drop the volume, or drop the line
- Examples that illustrate the same point twice
- Preambles, recaps and motivational filler
- "When to use" detail in the body that the description already covers
- Sections or branches for cases the purpose doesn't need
- Bundled scripts or reference files nothing points to
- A padded description; keep it specific and slightly pushy about when to trigger

Leave the `name` alone, since renaming breaks replacing the installed version. If the skill is already lean, say so and suggest only the few cuts that are real; don't invent bloat to fill a list.

### 4. Collect decisions

The user accepts, rejects or modifies each number ("all but 3", "2 only if you keep the example"). Take their answer as final and don't re-argue a rejected cut. Ask a short question only if a decision is unclear. If nothing is accepted, say the skill stays as it is and stop.

### 5. Hand off to skill-updater

Once every suggestion has a decision, invoke skill-updater with: the skill name, the confirmed purpose, and the accepted cuts spelled out precisely enough to apply without guessing (including any modifications the user asked for). Say these are already approved, so skill-updater applies them without another approval round. skill-updater handles the edit and delivery, so don't edit the skill yourself, and don't run tests or benchmarks.
