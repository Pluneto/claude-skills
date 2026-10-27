# pluneto-skills

A Claude Code plugin marketplace with Pluneto's own skills: plan-then-build workflows, tools for maintaining skills, and design and UX reviews. Every plugin is plain Markdown instructions (plus one Python helper script, shipped in both `ux` skills): no hooks, MCP servers or binaries.

## Plugins

| Plugin | Skills | Install |
|---|---|---|
| `workflow` | plan-this, build-this, solve-this, research-this, use-available-skills, handoff | per project |
| `skill-tools` | reflect, skill-updater, skill-ozempic | per project |
| `design` | backend-design-review, dashboard-design | per project |
| `ux` | user-types, tool-for-users | per project |
| `setup` | setup-pluneto-skills (`/setup:setup-pluneto-skills`, user-invoked only) | user scope, once per machine |

## Install

```bash
# once per machine
claude plugin marketplace add Pluneto/skills
claude plugin install setup@pluneto-skills --scope user

# per repo
claude plugin install workflow@pluneto-skills --scope project   # or --scope local
# then in Claude Code: /setup:setup-pluneto-skills   (setup or repair)
```

Inside a session the same works as `/plugin marketplace add Pluneto/skills`. No GitHub credentials are needed; on a machine without a GitHub SSH key, set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` if adding fails.

**Updates:** plugins have no `version` field, so an update brings you to the latest commit. Auto-update is off for third-party marketplaces: turn it on in `/plugin` → Marketplaces → pluneto-skills → Enable auto-update, or run `claude plugin marketplace update pluneto-skills` now and then.

Plugins run with your permissions and skills enter Claude's context, so read what you install. These skills are built for my own setup; they work elsewhere, but some wording (paths like `~/projects/claude-skills`) assumes it.

## Edit a skill

1. Edit `plugins/<plugin>/skills/<skill>/SKILL.md` (copy files in; symlinks are rejected).
2. Commit to `main` and push. The pre-commit hook regenerates `.claude-plugin/marketplace.json` and validates everything.
3. Installed copies update on the next marketplace update.

No `version` fields: updates follow the git commit SHA. New plugin: add `plugins/<name>/.claude-plugin/plugin.json` (`name`, `description`, `author`, `license`) and a `skills/` folder.

After cloning, enable the hook: `git config core.hooksPath scripts/hooks` (needs `claude` and Python 3 with PyYAML). The hook also refuses commits whose author email is not a GitHub noreply address, so a personal address never lands in public history: `git config user.email <id>+<user>@users.noreply.github.com`.

## Scripts

- `scripts/build-marketplace`: regenerates the marketplace file and checks skill frontmatter (valid YAML, `name` matches the folder, `description` present) and that there are no symlinks.
- `scripts/validate`: `claude plugin validate --strict` on the marketplace and every plugin, allowing only the missing-version warning.
- `scripts/measure-context`: estimates always-on skill tokens outside any project (see `docs/baseline.md`).

## Licence

MIT, see [LICENSE](LICENSE). `plugins/workflow/skills/handoff` is adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, its notice is kept in that folder). Anthropic's source-available skills (docx, pdf, pptx, xlsx, …) are deliberately not included.
