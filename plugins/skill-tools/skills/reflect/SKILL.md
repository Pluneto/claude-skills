---
name: "reflect"
description: End-of-session retro. Finds friction and repeated work in the session and applies up to five lean edits to project notes or skills. Optionally takes a focus.
disable-model-invocation: true
---

# Reflect

Turn this session's avoidable problems into up to five edits, of any size, and apply them (or, for pluneto plugin skills, hand the user a ready prompt), so the next session starts further ahead and needs less of the user.

The more an agent can run on its own, without the user stepping in, the better. That is the lens for the whole retrospective: the best lesson is one that removes a future round-trip to the user, and reflect itself should not add one.

Every line of instructions is read by every future session. The goal is therefore not to record what happened but to make the instructions better, and shorter where possible. Making no changes is a valid outcome. If the user names a focus (`/reflect the build setup`), review only that.

## 1. Find the problems

Review the session for friction, strongest signal first:

- the user corrected, redirected, or repeated themselves
- the agent stopped to ask, or waited for approval, on something it could have decided, looked up, or checked itself
- commands or tools failed, or there were retries, dead ends, and workarounds
- something had to be guessed that a note would have answered (a command, path, convention, quirk)
- a skill misled, was ambiguous, skipped a needed step, or should have triggered and didn't

For each one, ask which instruction, present at the start of the session, would have prevented it. That is the root cause; the symptom is not. Drop one-offs (typos, a flaky network, details of this specific task) and keep what is likely to recur. If nothing is worth keeping, say so in a sentence and stop.

Also look for procedures, helper scripts or dictated checklists repeated in the session.

## 2. Find where instructions live

Look before deciding, because that depends on the project. Typical places: CLAUDE.md, AGENTS.md, rules directories, README, CONTRIBUTING, docs, a notes file, project instructions, memory, and the skills directory, including nested files close to the work involved. Read in full whatever could overlap with your lessons, since you cannot keep things lean without knowing what is already there. For automation candidates, also list the skills that already exist, because the right fix is often to extend one of them.

Put each note at the narrowest scope where it matters, so it only loads when relevant. If there is no established place (a plain chat with no project, say), pick the simplest option, use it, and say where it went.

## 3. Choose the target and keep it lean

For each lesson pick one target:

- **existing skill**: the problem came from a skill used in this session, or the skill is the natural home for the lesson
- **pluneto plugin skill**: an existing skill from the `pluneto-skills` marketplace (listed as `<plugin>:<skill>`). These serve many projects, so the lesson must still hold with this session's specifics removed ("when X kind of situation comes up, do Y because Z"); if it only holds here, it is a project note. The user applies it from a prompt you write (step 4)
- **new skill**: a repeated procedure that no existing skill or note covers (criteria below)
- **project note**: a fact, convention, command, or gotcha; the file from step 2
- **no change**: a one-off, or already covered

Edit or delete before you add. If an instruction exists but was missed, reword, move, or tighten it. If two lines conflict, fix one of them. Stale or redundant lines found along the way are fair edits, and a pure removal is a good change. A new line is one short imperative with its reason in a clause, specific enough to act on (the exact command or path), with no story of what happened.

Write instructions that let the agent keep going on its own: give a default and a note to state the assumption instead of "ask the user"; name the command or path instead of "find out"; let it verify its own work instead of asking for confirmation. Keep asking only for what is irreversible or affects others (deleting, sending, spending, publishing) or what is expensive to redo and genuinely ambiguous. Never write a line that removes a confirmation step for those.

A new skill created here is a **repository skill**: it lives in the project's skills directory and is committed with the project, not published to claude.ai. If the project has no skills directory, use the conventional `.claude/skills/` and say so.

Keep secrets, tokens, and personal data out of notes and skills, since instructions get shared.

**Be harsh on your own edits.** Make at most five in total, but five is a ceiling, never a target; most sessions deserve zero to two. Every edit is a cost paid by every future session, so assume it should be dropped and keep it only if it passes all of these:

- **It will recur**: you can name the situation where a future session hits this again. "Might be useful" fails.
- **It would have changed this session**: name the specific delay, correction, or failure it would have prevented.
- **Nothing covers it**: no existing line, skill, or default behaviour already says it. If it was covered but missed, reword that line instead of adding another.
- **It pays for its size**: the future time saved clearly outweighs the tokens it adds to every session. When in doubt, shorter, or nothing.

A **new skill** must also show evidence of repetition from this session (or a clear reason it will recur, such as the user calling it routine), that no existing skill or note covers it and extending one would not do, and that it is a multi-step procedure or judgment call, not a single fact.

Rank what survives by expected payoff and cut from the bottom. Say plainly when you dropped candidates (one line is enough).

## 4. Apply, then report

Do not ask for approval; the user wants less back-and-forth, and every edit is small, visible and easy to revert.

- **Project notes**: edit in the file's own style, in place rather than appended wherever an existing line should change.
- **Existing skills**: hand the edit and the evidence from this session to the skill-updater skill, which makes the change and delivers it the right way (a same-name `.skill` file for skills installed in claude.ai, an in-place edit for repository skills). It applies the edit without asking.
- **Pluneto plugin skills**: the user runs these edits themselves, in a session of their choosing, so your output is a prompt and the plugin's files stay as they are. Read the skill's current SKILL.md (the installed copy under `~/.claude/plugins/cache/pluneto-skills/` is fine for reading), then write one prompt per skill, covering all its edits, in a fenced block the user can paste into a fresh session:

  ```
  Use the skill-updater skill to update `<plugin>:<skill>` (pluneto-skills marketplace).
  Edit 1, section "<heading>": replace "<exact current text>" with "<new text>"
    (or: add "<new text>" after "<exact current text>"; or: remove "<exact current text>")
  General rule: when <kind of situation>, <do this>, because <reason>.
  Evidence: <one or two lines on what went wrong, without project names, paths or personal data>.
  ```

  Quote the current text verbatim so skill-updater can find the spot, and make the prompt self-contained: the session that runs it has none of this context.
- **New skills**: hand the proposal and its evidence to the skill-creator skill, which builds it as a repository skill. The evidence answers its intent questions, so it can go straight to drafting.

If the user names a change they do not want, or says something is wrong, revise it and apply the revision.

## 5. Report

Show what changed in a message the user will actually see (not narration between tool calls), one block per edit:

**Edit N: short title**
- **Problem**: what happened, and why it will recur.
- **Change**: target file and the exact text, as add / replace X with Y / remove; for a pluneto plugin skill, the prompt from step 4.
- **Net effect**: what it merges, replaces, or removes, or why a pure addition is justified.

For a new skill, give its name, one-sentence scope, location, and which tests from step 3 it passed. Add one line on candidates dropped, and, for cloud skills, the file to upload. Don't repeat the explanations beyond that.
