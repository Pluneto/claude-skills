# Merge review: `merge-mattpocock`

What the branch changed, how it was checked, and what is still unproven. The keep/merge/drop decisions are in [merge-map.md](merge-map.md); before and after token counts are in [baseline.md](baseline.md). Review with `git diff origin/main...merge-mattpocock`.

## Commits

One per milestone, in order: baseline and merge map → restructure and copy-in → merges and splits → wiring → neutral wording and README → setup.

## Changes per skill

| Skill | What happened | Where to look |
|---|---|---|
| tdd, diagnosing-bugs, pr, prototype, codebase-design, domain-modeling, improve-codebase-architecture | Copied from mattpocock-skills 1.3.1 with its LICENSE. Adapted: tdd points to review-changes; diagnosing-bugs gets an autopilot line; prototype captures into the plan or ticket; improve-codebase-architecture calls interview instead of grilling | `plugins/engineering/skills/` |
| review-changes | Copied from code-review and renamed. Takes the fixed point and Spec path from a caller (build-this) and asks nothing under autopilot; reads plans and tickets under `plans/`; plan constraints count as standards | `plugins/engineering/skills/review-changes/` |
| wayfinder | Copied. Calls interview (ticket type `wayfinder:interview`), research-this in facts mode and prototype; local map under `plans/<effort>/`; hands off to plan-this | `plugins/workflow/skills/wayfinder/` |
| to-tickets | Copied. Reads a plan file and skips its quiz for agreed plans; local tickets under `plans/<feature>/tickets/`; no triage labels; points to /build-this | `plugins/workflow/skills/to-tickets/` |
| to-questionnaire, wizard | Copied unchanged | `plugins/workflow/skills/` |
| writing-for-agents | Copied unchanged into skill-tools | `plugins/skill-tools/skills/writing-for-agents/` |
| interview | **New**, split from plan-this's step 2 plus grilling's triggers. Takes a root, settled decisions, caller rules and autopilot | `plugins/workflow/skills/interview/` |
| which-skill | **New**, user-invoked router rewritten from ask-matt, with its PHASE-BOUNDARIES.md | `plugins/workflow/skills/which-skill/` |
| plan-this | Step 2 now invokes interview and passes plan-specific rules; reads a wayfinder map with its decisions fixed; offers `/to-tickets` for multi-session work | `plugins/workflow/skills/plan-this/` |
| build-this | Accepts a ticket folder; records the base commit; ends with one review-changes pass | `plugins/workflow/skills/build-this/` |
| solve-this | Requires interview; passes autopilot down; calls diagnosing-bugs on failing checks | `plugins/workflow/skills/solve-this/` |
| research-this | Gains the primary-sources rule and facts mode (cited file, no verdict) from research | `plugins/workflow/skills/research-this/` |
| use-available-skills | Never picks interview or review-changes | `plugins/workflow/skills/use-available-skills/` |
| reflect | Gains retro's lenses and a "check" target; now user-invoked | `plugins/skill-tools/skills/reflect/` |
| skill-ozempic | Now user-invoked; invokes writing-for-agents before suggesting cuts | `plugins/skill-tools/skills/skill-ozempic/` |
| skill-updater | Invokes writing-for-agents before editing; clone path corrected | `plugins/skill-tools/skills/skill-updater/` |
| user-types, tool-for-users | Moved from ux to design; question-tool wording neutral | `plugins/design/skills/` |
| setup-pluneto-skills | New plugin list; tracker question and templates; repair checks 9–12 (ux, mattpocock-skills, tracker doc, engineering); version-based currency check | `plugins/setup/skills/setup-pluneto-skills/` |
| handoff, backend-design-review, dashboard-design | Codex metadata only (handoff: one neutral-wording line) | |

Every skill also gained `agents/openai.yaml`. Every plugin.json has `version: 1.0.0` and an explicit `skills` list.

Scripts: `build-marketplace` regenerates each plugin.json's `skills` list; `validate` adds the version, openai.yaml, licence and which-skill checks; new `bump` and `measure-skills`; the hook stages plugin.json files.

## Check results (2026-10-28)

| # | Check | Result |
|---|---|---|
| 1 | `scripts/build-marketplace`, `scripts/validate` | Pass (6 targets). Failure paths checked by removing a LICENSE and flipping a policy flag: both caught |
| 2 | Dangling references | Pass. Allowed hits: interview and which-skill name "grill me" as a trigger phrase; `ux:` in the design skills' `file-format.md` are User_Types.md section markers, not the plugin; reflect calls itself a "retro"; setup's repair checks 9 and 11 name `ux@pluneto-skills`, `.scratch/`, `ready-for-agent` and triage labels in order to find and fix them |
| 3 | Codex metadata in validate | Pass |
| 4 | Context cost | Pass: ~2334 → ~2132 always-on tokens (−9%) |
| 5 | Real install | Pass, in a scratch repo with an isolated `CLAUDE_CONFIG_DIR`: 5 plugins at 1.0.0, 29 skills, installed cache identical to the source. See gaps for the setup/repair run |
| 6 | skills.sh | Pass: `npx skills@latest add <clone> --list` finds 29 skills (it has a real `--list`) |
| 7 | Triggering (12 `claude -p` prompts, 4 content plugins via `--plugin-dir`) | 11/12. Fired as expected: interview ("grill me"), diagnosing-bugs, research-this facts mode, plan-this, review-changes, tdd, prototype. None of reflect, skill-ozempic, to-tickets or wayfinder fired on their own. The miss: "is there already a Python library for ICS?" was answered from memory once; reruns fired research-this 2/2 on the branch and 1/2 on main, so this is noise and not a regression. plan-this → interview wasn't reached because `-p` stops at plan-this's first approval question. solve-this → diagnosing-bugs wasn't run (it needs a full build) |

## Known gaps

- **Codex and Copilot are untested.** The layout matches Matt's verified one (explicit `skills` lists, `agents/openai.yaml`, no symlinks), but nobody has run `codex plugin add` against this repo.
- **The model-driven setup/repair run wasn't done.** The isolated config can't log in, and running it against the real config would change your real plugin installs. Its commands were run by hand: Claude Code silently drops an enabled `ux@pluneto-skills` from `claude plugin list` (which check 9 catches by reading the settings files). Run `/setup:setup-pluneto-skills repair` in both repos after merging, as planned.
- **Updates now follow versions.** Installed copies update only when a plugin's version changes. On this branch everything stays 1.0.0, so a branch install has to be reinstalled to see later commits (`claude plugin update` reports "already at the latest version"). After the merge, run `scripts/bump <plugin>` with every change. `validate` enforces this against `origin/main`, but the check couldn't be exercised on the branch because main has no versions yet.
- **Cross-plugin calls say "if available".** A repo with workflow but without engineering gets no closing review and no diagnosing-bugs in solve-this.
- **The which-skill check is a substring match.** Short names such as `pr` pass trivially.
