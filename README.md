# pluneto-skills

Pluneto's own Claude Code skills, published as a private plugin marketplace. This repo is the source of truth: write and edit skills here, not in claude.ai.

## Plugins

| Plugin | Skills | Install |
|---|---|---|
| `workflow` | plan-this, build-this, solve-this, research-this, use-available-skills, handoff | per project |
| `skill-tools` | reflect, skill-updater, skill-ozempic | per project |
| `design` | backend-design-review, dashboard-design | per project |
| `setup` | setup-pluneto-skills (`/setup:setup-pluneto-skills`, user-invoked only) | user scope, once per machine |

## Use

```bash
# once per machine (auto-update is on via extraKnownMarketplaces in ~/.claude/settings.json)
claude plugin marketplace add Pluneto/claude-skills
claude plugin install setup@pluneto-skills --scope user

# per repo
claude plugin install workflow@pluneto-skills --scope project   # or --scope local
# then in Claude Code: /setup:setup-pluneto-skills   (setup or repair)
```

Private repo: Claude Code fetches with non-interactive git, so HTTPS needs the gh credential helper (`gh auth setup-git`).

## Edit a skill

1. Edit `plugins/<plugin>/skills/<skill>/SKILL.md` (copy files in; symlinks are rejected).
2. Commit to `main` and push. The pre-commit hook regenerates `.claude-plugin/marketplace.json` and validates everything.
3. Installed copies update automatically (or run `/plugin marketplace update pluneto-skills`).

No `version` fields: updates follow the git commit SHA. New plugin: add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `description`, `author`) and a `skills/` folder.

After cloning, enable the hook: `git config core.hooksPath scripts/hooks` (needs `claude` and Python 3 with PyYAML).

## Scripts

- `scripts/build-marketplace`: regenerates the marketplace file and checks skill frontmatter (valid YAML, `name` matches the folder, `description` present) and that there are no symlinks.
- `scripts/validate`: `claude plugin validate --strict` on the marketplace and every plugin, allowing only the missing-version warning.
- `scripts/measure-context`: estimates always-on skill tokens outside any project (see `docs/baseline.md`).

## Licences

`plugins/workflow/skills/handoff` is adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, notice kept in that folder). Everything else is Pluneto's own. Anthropic's source-available skills (docx, pdf, pptx, xlsx, …) are deliberately not included.
