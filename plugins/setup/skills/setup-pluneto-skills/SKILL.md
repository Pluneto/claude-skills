---
name: setup-pluneto-skills
description: Set up or repair the pluneto-skills plugins in the current repo (setup | repair).
argument-hint: "setup | repair"
disable-model-invocation: true
---

# Set up or repair pluneto-skills in this repo

The `pluneto-skills` marketplace (`Pluneto/claude-skills`, cloned at `~/projects/claude-skills`) has these plugins: `workflow`, `skill-tools`, `design`, and `setup` (this skill, installed at user scope). Read the current list from `.claude-plugin/marketplace.json` in the marketplace's install location (`claude plugin marketplace list --json`) rather than trusting this line.

**Mode:** the argument, if given. Otherwise **repair** when the repo's `.claude/settings.json` already enables a `*@pluneto-skills` plugin, else **setup**. State the mode you picked.

Both modes inspect first, show findings, and write only after the user confirms once. Commands run from the repo root (`git rev-parse --show-toplevel`; outside git, use the current directory and say so).

## Setup

1. **Inspect.** Read `.claude/settings.json`, `.claude/settings.local.json`, `CLAUDE.md` (or `AGENTS.md` if that is the instructions file), and the output of `claude plugin list --json` and `claude plugin marketplace list --json`. Done when you know which pluneto-skills plugins are already installed for this repo, user scope included.
2. **Choose plugins.** Show the available plugins with one line each (from `marketplace.json`), marking the ones already present, and ask which this repo should have. This is the one question setup needs.
3. **Confirm.** Show the exact changes as a list: the commands below and the files they touch. Apply after one yes.
4. **Apply.**
   - Pin the marketplace in the repo, so a fresh clone is prompted: `claude plugin marketplace add Pluneto/claude-skills --scope project` (skip if `.claude/settings.json` already has `extraKnownMarketplaces.pluneto-skills`).
   - For each chosen plugin: `claude plugin install <plugin>@pluneto-skills --scope project`.
   - If `workflow` is chosen: create `plans/archive/` with an empty `plans/archive/.gitkeep` (plan-this saves to `plans/`, build-this archives to `plans/archive/`).
   - Write the CLAUDE.md block (template below).
5. **Verify.** Run every repair check. Done when all pass; then tell the user to run `/reload-plugins` (or restart) so the new skills load. User-invoked skills (this one, `workflow:handoff`) never appear in the model's skill list, so judge installs by `claude plugin list --json`, not by that list.

## Repair

Run every check, collect the findings into one table (check, status, fix), confirm once, then apply the fixes and re-run the checks that failed. Done when every check passes or a remaining failure is reported with what only the user can do about it.

| # | Check | How | Fix |
|---|---|---|---|
| 1 | Marketplace registered | `pluneto-skills` in `claude plugin marketplace list --json` | `claude plugin marketplace add Pluneto/claude-skills` |
| 2 | Marketplace current | `git -C <installLocation> rev-parse HEAD` equals `git ls-remote https://github.com/Pluneto/claude-skills HEAD` | `claude plugin marketplace update pluneto-skills` |
| 3 | Enabled means installed (Claude Code loads nothing, silently, for a plugin enabled in settings but not installed) | Every `<id>: true` in `enabledPlugins` of `.claude/settings.json` and `.claude/settings.local.json`, any marketplace, has a `claude plugin list --json` entry with that `id` whose scope is `user` or whose `projectPath` is this repo | `claude plugin install <id> --scope project` (`--scope local` if it came from `settings.local.json`) |
| 4 | Installed plugin current | For each `*@pluneto-skills` entry in `claude plugin list --json` that applies to this repo (scope `user`, or `projectPath` is this repo; ignore other projects' installs), its `version` matches the marketplace's `HEAD` (first 12 characters) | `claude plugin update <id>` |
| 5 | No duplicate skills | For each skill in an enabled pluneto-skills plugin (folder names under its `installPath`/`skills/`), no same-named copy in `~/.claude/skills/<name>`, `~/.claude/skills/synced/*/<name>` or this repo's `.claude/skills/<name>` | User-level copy: move it to `~/.claude/skills-backup/<YYYY-MM-DD>/` (outside `~/.claude/skills`, so it stops loading; Claude Code manages `.trash` itself). claude.ai copy (`synced`): the user deletes it in claude.ai → Customize → Skills; it disappears at the next sync. Repo copy: report it and ask, since the repo may depend on its version |
| 6 | Plans folders | If `workflow` is enabled: `plans/` and `plans/archive/` exist | Create `plans/archive/.gitkeep` |
| 7 | CLAUDE.md block current | The block below exists and lists exactly the enabled pluneto-skills plugins | Write or rewrite the block |
| 8 | Marketplace pinned in repo | `.claude/settings.json` has `extraKnownMarketplaces.pluneto-skills` | `claude plugin marketplace add Pluneto/claude-skills --scope project` |

## CLAUDE.md block

Put it under the file's `## Agent skills` heading (create the heading at the end if missing), replacing any earlier `### pluneto-skills` block. Keep it this short: it loads in every session.

```markdown
### pluneto-skills

Installed here:
- `<plugin>`: <its skills, comma-separated>

Plans go in `plans/`, finished ones in `plans/archive/`. Missing or stale skills: run `/setup:setup-pluneto-skills repair`.
```

One `- <plugin>` line per enabled plugin.

Leave out the plans sentence when `workflow` is not enabled.
