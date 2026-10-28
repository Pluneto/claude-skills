# Merge map: mattpocock-skills → pluneto-skills

Source: mattpocock-skills **1.3.1** (MIT, (c) 2026 Matt Pocock), from `~/.claude/plugins/cache/claude-plugins-official/mattpocock-skills/1.3.1/`. Diff a later upstream release against this version to pick up improvements. The plan is `plan-merge-mattpocock-skills.md` in the `plans/` folder above this clone (moved to `plans/archive/` once merged).

## Matt's skills

| Skill | Outcome | Where it went / why |
|---|---|---|
| tdd | keep | engineering |
| diagnosing-bugs | keep | engineering; solve-this's retry loop calls it |
| code-review | keep, renamed | engineering/review-changes (avoids the built-in /code-review); build-this ends with it |
| pr | keep | engineering |
| prototype | keep | engineering |
| codebase-design | keep | engineering |
| improve-codebase-architecture | keep | engineering; its final step calls interview |
| domain-modeling | keep | engineering |
| wayfinder | keep | workflow; hands off to plan-this, local map under `plans/<effort>/` |
| to-tickets | keep | workflow; reads a plan file, local tickets under `plans/<feature>/tickets/` |
| to-questionnaire | keep | workflow |
| wizard | keep | workflow |
| writing-for-agents | keep | skill-tools |
| research | merge | research-this (facts mode, primary-sources rule) |
| retro | merge | reflect (retro's lenses) |
| grilling | drop | the interview skill (split from plan-this) takes its job and triggers |
| grill-me, grill-with-docs | drop | plan-this / interview |
| to-spec, implement, implement-spec | drop | plan-this / build-this |
| triage, setup-matt-pocock-skills | drop | the triage flow is gone; setup-pluneto-skills configures the tracker |
| ask-matt | drop, rewritten | workflow/which-skill (user-invoked router over the merged set) |
| handoff | drop | identical to workflow/handoff, which is kept |
| teach, wait-what | drop | not selected |
| `in-progress/*`, `misc/*` | drop | unfinished or frozen upstream |

## Pluneto's skills

| Skill | Outcome |
|---|---|
| plan-this | interview method split out into workflow/interview |
| build-this, solve-this, research-this, use-available-skills, handoff | kept in workflow, adapted |
| reflect, skill-updater, skill-ozempic | kept in skill-tools (reflect, skill-ozempic now user-invoked) |
| backend-design-review, dashboard-design | kept in design |
| user-types, tool-for-users | moved from ux to design; the ux plugin is removed |
| setup-pluneto-skills | kept in setup, gains migration checks |

## New skills

- workflow/interview: plan-this's design-tree interview, callable by plan-this, wayfinder and improve-codebase-architecture.
- workflow/which-skill: user-invoked router.

## Plugins after the merge

| Plugin | Skills |
|---|---|
| workflow (12) | plan-this, build-this, solve-this, research-this, use-available-skills, handoff, interview, which-skill, wayfinder, to-tickets, to-questionnaire, wizard |
| skill-tools (4) | reflect, skill-updater, skill-ozempic, writing-for-agents |
| engineering (8) | tdd, diagnosing-bugs, review-changes, pr, prototype, codebase-design, improve-codebase-architecture, domain-modeling |
| design (4) | backend-design-review, dashboard-design, user-types, tool-for-users |
| setup (1) | setup-pluneto-skills |
