---
name: "skill-updater"
description: Update or modify an existing skill, and nothing else. Use whenever the user wants to change, fix, tighten, extend, or refactor a skill that already exists (e.g. "update the X skill", "the skill got Y wrong, fix it", "add this lesson to the skill"), and whenever /reflect has a skill edit to apply. Handles skills installed in claude.ai (returns a same-name .skill file to upload), skills from a plugin marketplace whose source repo is cloned locally (edits the source, commits and pushes), and skills that live in a repository (edits them in place). Does not create new skills (use skill-creator) and never runs benchmarks, evals, or description-optimization loops.
---

# Skill Updater

A narrow sibling of skill-creator for one job: changing a skill that already exists. It skips skill-creator's test-run, benchmark, and review-viewer machinery on purpose. The user judges the result by using the skill, so the work here is making a small, correct, well-placed edit and delivering it the right way.

## Principle: general-purpose but specialised

Skills are reused across many different requests, so an edit must make the skill better for the whole class of tasks it covers, not for the one session that exposed the problem. Before writing anything, restate the lesson in general terms ("when X kind of input appears, do Y because Z") and ask whether it still holds with the specifics of this session removed. If it only holds for one project, one file name, or one phrasing, it belongs in project notes or memory, not in the skill. Say so and propose that instead.

A skill should stay specialised: it has a clear domain and a trigger description that matches it. Don't widen the domain to absorb an unrelated lesson. Suggest a separate skill rather than bloating this one.

## Principle: autonomy

The more a skill lets the agent finish on its own, the better. When an edit touches a point where the skill makes the agent stop and ask the user, prefer a default plus "state the assumption and continue", a command the agent can run to check, or a rule it can apply itself. Keep a question or confirmation only for what is irreversible or affects others (deleting, sending, spending, publishing) or is expensive to redo and genuinely ambiguous, and never remove one of those. Apply the same thinking to this skill's own work: decide and deliver rather than asking.

## Workflow

### 1. Pin down the change

Get the target skill's name and the change wanted. Sources: the user's request, or an edit from /reflect (its Problem / Change text and session evidence). Edits from /reflect are applied as given; don't add an approval round. If the request is vague ("improve the pdf skill"), infer the most likely change from the session (what went wrong, what the user corrected), apply it, and say which reading you took. Ask one short question only when the session gives no hint at all.

### 2. Find where the skill lives

Check all three places before deciding how to deliver:

- **Marketplace skill**: a plugin skill (listed as `plugin:skill`) whose marketplace source repo is cloned locally. Pluneto's own skills live in the local clone of `Pluneto/skills` (usually `~/github/skills`; otherwise find a clone whose `git remote -v` is Pluneto/skills), at `plugins/<plugin>/skills/<name>/` (marketplace `pluneto-skills`). The installed copy under `~/.claude/plugins/cache/` is a read-only cache; edit the source.
- **Repository skill**: a skill folder in the working project that is writable (typically `.claude/skills/<name>/` or a `skills/` directory). Search with Glob for `**/<name>/SKILL.md`.
- **Cloud skill**: a skill installed in claude.ai. Its files are read-only here (for example under `/mnt/skills/` or an uploads folder), or it is only known by name from the skills list.

Delivery follows from this:

| Where it exists | What to do |
|---|---|
| Marketplace source repo (wins over any claude.ai copy, which is then stale) | `git pull`, edit it in the source repo, commit to `main` and push (step 6). |
| Cloud (claude.ai), with or without a repo copy | Edit a working copy and deliver a downloadable `.skill` file (step 5). If a repo copy also exists, apply the same edit there directly so the two don't drift. |
| Repository only | Edit it in place yourself. No `.skill` file needed. Don't commit or push unless asked. |
| Neither found | Say so and ask where the skill is, or whether the user wants a new skill (that is skill-creator's job). |

### 3. Read before you edit

Read the whole current SKILL.md and any bundled files the change could touch (scripts, references). You can't keep a skill lean or consistent without knowing what is already there. Note the exact `name` in the frontmatter and the folder name; both must stay unchanged.

### 4. Make the smallest good edit

First invoke the **writing-for-agents** skill (in Claude Code, call the Skill tool with `writing-for-agents`) if available: its pointer, no-op and pruning rules govern every edit below.

- Edit or delete before adding. If an instruction exists but was missed or misread, reword, move, or tighten it. If two lines conflict, fix one. A pure removal is a good change.
- A new line is a short imperative with its reason in a clause. Explain why rather than shouting MUST; the model reading the skill is capable and generalises better from reasons.
- Keep SKILL.md focused (well under 500 lines). If the edit would push it over, move detail into `references/` and point to it from SKILL.md.
- Update the frontmatter `description` only if what the skill covers or when it should trigger really changed. It is the trigger mechanism, so keep it specific and slightly pushy about when to use the skill.
- Preserve everything the change doesn't concern: structure, tone, bundled files, and the `name`. Never rename (`foo-v2` breaks the replace-on-upload step).
- No secrets, tokens, or personal data in a skill; skills get shared.

### 5. Check lightly, without benchmarks

Do not run test prompts, baselines, graders, benchmark aggregation, the eval viewer, or description-optimization scripts. Instead:

1. Re-read the edited SKILL.md once, top to bottom, for contradictions and leftover wording from the old version.
2. Mentally walk the originating problem through the new text: would a fresh session have avoided it? Would an unrelated task the skill also covers still behave the same?
3. Validate the structure (frontmatter, name, description) with skill-creator's `scripts/quick_validate.py` when it is available.

If the user explicitly asks for real test runs, hand off to skill-creator.

### 6. Deliver

**Cloud skill: produce the `.skill` file.**

1. Copy the skill folder to a writable scratch location (the installed path may be read-only), keeping the folder name identical to the original, and apply the edit there.
2. Package it. Preferred: from the skill-creator directory run `python -m scripts.package_skill <path/to/skill-folder> <output-dir>`. If that script isn't available, zip the folder with the skill folder as the top-level entry (`zip -r <name>.skill <name>/ -x "*/evals/*" "*/__pycache__/*" "*.pyc" "*.DS_Store"`).
3. The file must be named `<original-name>.skill`, exactly the previous skill's name, so uploading it replaces the old version instead of creating a second one.
4. Check the archive contains `<name>/SKILL.md` at the top level (`unzip -l`), then send the file to the user with the file-delivery tool (`SendUserFile` or `present_files`). Never hand over raw SKILL.md text in place of the packaged file.
5. Tell the user in a line or two what changed and that they need to upload it manually in claude.ai (Settings → Capabilities → Skills), replacing the existing version. The edit isn't live until they do.

**Marketplace skill:** commit only the skill's files (stage them by name) to `main` and push. The repo's pre-commit hook regenerates and validates the marketplace; if it fails, fix the cause and commit again, never `--no-verify`. Tell the user installed copies pick it up on the next auto-update, or now with `/plugin marketplace update <marketplace>` then `/reload-plugins`.

**Repository-only skill:** the edit is already made; say which file changed and what changed.

Finish with two or three lines: what changed, where, and (for cloud skills) the file to upload. Don't recap the steps.

## Working with /reflect

/reflect decides skill edits on its own and reports them afterwards; skill-updater is where such an edit gets applied. When /reflect hands over an edit plus its session evidence, go straight to step 2, apply it, and deliver. Apply the generality check from the principle above one last time: if the wording is too specific to this session, tighten it to the general rule and tell the user what you did and why. When the user is applying lessons from /reflect to several skills, handle each skill separately and give each its own `.skill` file.
