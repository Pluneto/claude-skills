---
name: user-types
description: Create or maintain UX/User_Types.md, a repository's list of user-types (role + goal), each with a profile and MoSCoW requirements. Use whenever the user wants to define, list, add, edit, review or rebuild user-types, user roles, personas, target users or audiences for a repo or product, or runs /user-types. Also use it when another skill such as tool-for-users needs UX/User_Types.md and the file is missing or lacks a user-type.
---

# User types

Maintains `UX/User_Types.md` at the repository root: the list of user-types, each with a profile (description, goals, access level, contexts) and MoSCoW requirements, plus a generated list of the tool features each type is mapped to.

A user-type is a **role + goal**: what someone is allowed to do, combined with why they come. That pairing maps cleanly onto both permissions and features, so the file stays small and other skills (tool-for-users) can reference stable IDs. Situational differences, such as phone versus desktop or using a screen reader, are *contexts*. They go on the profile and become journey variations later, not extra types.

## What's in this skill

Read `references/file-format.md` before writing anything, and `references/glossary.md` (about 30 generic user-types by product kind) before drafting, since every profile starts from it. Run the helper from the repo root as `python3 <this skill's base directory>/scripts/ux.py <command>` (`--help` lists the commands). Without Python, follow file-format.md by hand.

## Asking the user

Ask each named choice with AskUserQuestion (a numbered list if it's unavailable). These choices are the user's; don't make them yourself, even when one looks obvious.

## Step 0: Where are we?

Run `ux.py status`, then:

- **Called by another skill** with `mode=create` or `mode=append names="A; B"`: skip the menus. Go straight to 1A (create) or Append (with those names), then follow "Handing back".
- **Alternative filename** reported (for example `UX/User_Type.md`): ask whether to rename it to `UX/User_Types.md` and continue with it. Do this before anything else.
- **File missing**: go to 1A.
- **File present**: go to 1B.

## 1A: No file yet

Tell the user there is no `UX/User_Types.md` yet, then ask how to make it:

- **A. Read the repo + glossary**: scan the repository, make educated guesses, and match each guess to the glossary.
- **B. Glossary only**: pick product kinds, then take candidates from those glossary groups.
- **C. I'll name them**: the user lists the types, and you match each to glossary profiles.

### Option A: repo + glossary

1. Run `ux.py scan`. It lists root docs, docs/ files, persona-like files, role and permission evidence (`path:line`), candidate role names and route folders.
2. Read what the scan points to: README, CLAUDE.md, AGENTS.md or AGENT.md, any persona or user-type file, and the role definitions it found. Skip the rest of the codebase. The scan already found the signals, and reading more costs time without changing the answer.
3. Decide the product kind using the glossary's "Choosing groups" table.
4. List candidate types. Each candidate needs either a piece of evidence (`path:line`) or a ★ entry from CORE. Keep the evidence; it goes on the profile's **Evidence** line.
5. Match each candidate to one glossary entry, using "Repo signals" and "Telling similar types apart". Name the type the way the repo does, for example "Committee member" rather than "Board member".
6. Go to Drafting.

### Option B: glossary only

1. Ask which product kinds apply, as a multi-select of the glossary groups. CORE is always included.
2. Candidates are the CORE ★ entries plus every entry in the chosen groups.
3. Go to Drafting. The Review step is where the user drops the ones that don't apply.

### Option C: the user names them

1. Ask the user to list the user-types in free text.
2. For each name, find the closest glossary entries:
   - One clear match: use it.
   - Several plausible matches: ask which to base it on, offering up to 3 entries plus "Write it fresh".
3. Go to Drafting.

## 1B: File exists

Ask what to do:

- **A. Append a new user-type**
- **B. Edit user-type(s)**
- **C. Remake from scratch**

### Append

1. Ask which user-type(s) to add, in free text, unless names were handed over.
2. Compare each against the existing types. If one is effectively the same role + goal as an existing type, say so and ask whether to edit that type instead.
3. Match each new name to the glossary as in Option C, then go to Drafting.
4. New IDs come from the "Next user-type ID" line in `status`.

### Edit

1. Ask which type(s) to change. With 4 or fewer types, use a multi-select card. With more, show a numbered list and let the user answer with numbers.
2. Ask what to change, in free text.
3. Run `ux.py refs <IDs>` and tell the user which tool docs use those types. Rewording is harmless. Dropping a type, or removing a requirement that a feature lists under **Serves**, leaves those docs inconsistent.
4. Draft the revised profile and show it as before → after.
5. Confirm per type: **Apply** / **Change more** / **Discard**.
6. Dropping a type is also an edit: confirm it, remove the section, then offer to re-run tool-for-users on the affected tool docs.

### Remake

1. If `status` says the file is UNCOMMITTED, warn that remaking overwrites changes git has no copy of. Ask whether to continue or stop.
2. Run `ux.py refs` on every existing type, so you know which tool docs depend on which IDs.
3. Run the 1A flow, including its A/B/C menu.
4. When drafting, reuse an existing ID for any new type with the same name or the same glossary basis, so the tool docs keep working. Every other type gets a fresh ID. The helper's ID tracker makes sure dropped IDs are never handed out again.
5. Write with `ux.py init --force`, then add the sections.
6. List tool docs that now reference missing IDs, and offer to re-run tool-for-users on them.

## Drafting a profile

Start from the glossary entry and adjust it to what the repo or the user says. Specific detail from the repo or user always beats generic glossary text.

- **Description:** 1 or 2 sentences on who they are and why they come, in this product's own terms.
- **Goals:** 2 to 4 bullets.
- **Access level, Contexts, Based on and Evidence:** as in file-format.md.
- **Requirements (MoSCoW):**
  - Counts: Must 3–5, Should 2–4, Could 1–3, Won't 1–2.
  - Phrase each as a need a feature could satisfy ("Can see which events still have places"), not as a feature spec ("Event list with capacity badge"). Needs survive design changes; specs don't.
  - Leave out what the Baseline section already covers (accessibility, mobile, error handling, privacy). Every human type inherits those.

If two candidates end up with the same access level and the same goals, they are one type, so merge them.

## Review: always before writing

1. Show every planned type with its full profile, exactly as it will appear in the file.
2. Ask per type, up to 4 types per card. For example: "UT-03 Organiser: add it?" with the options **Add as suggested** / **Change something** / **Drop**.
   - **Add as suggested**: queue the type for writing.
   - **Change something**: ask what to change (free text), redraft, and show it again in the next round.
   - **Drop**: leave it out.
3. Repeat until every type is either added or dropped.

Write nothing until the review is finished. The user should never discover a type in the file they didn't approve.

## Writing

1. If the file is missing, run `ux.py init`.
2. Add each approved type as a section, in ID order, in the exact format from file-format.md. Take IDs from `status`.
3. Run `ux.py sync`. It rebuilds the index, the mapped-features blocks and the ID tracker.
4. Run `ux.py check`. Fix every ERROR and run it again until it reports none.
5. Report in a short list: ID · name · access level for each type added or changed, plus the file path.

## Handing back

If another skill (such as tool-for-users) sent you here:

1. Finish Writing.
2. Say in one line which IDs now cover the names it asked about.
3. Carry on with that skill's next step without asking. The user already asked for that skill, so checking whether to continue only adds a stop.
