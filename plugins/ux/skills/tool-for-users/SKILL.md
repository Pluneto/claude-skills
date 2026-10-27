---
name: tool-for-users
description: Analyse a requested tool, page or feature set for a repository and who it is for. It breaks the tool into features, maps each feature to the user-types in UX/User_Types.md, checks their Must-requirements are covered, and maps each user's journeys into a UX/tools/ doc. Use whenever the user runs /tool-for-users or asks who will use something they plan to build, for user journeys or user flows, feature-to-user mapping, or a UX breakdown of a planned tool or feature, even if they don't name this skill.
---

# Tool for users

Turns a requested tool into `UX/tools/<slug>.md`. User-types live in `UX/User_Types.md`, owned by the **user-types** skill.

## What's in this skill

Read `references/file-format.md` before writing anything, and `references/journey-dimensions.md` at Step 6. Run the helper from the repo root as `python3 <this skill's base directory>/scripts/ux.py <command>` (`--help` lists the commands). Without Python, follow file-format.md by hand.

## Asking the user

Ask each named choice with AskUserQuestion (a numbered list if it's unavailable). These choices are the user's; don't make them yourself, even when one looks obvious.

## Step 0: User-types

Run `ux.py status`.

- **No `UX/User_Types.md`:** tell the user there isn't one yet and that you'll create it first. Then run the **user-types** skill with `mode=create`, and continue here when it hands back.
- **Alternative filename reported** (such as `UX/User_Type.md`): run the **user-types** skill. It handles the rename and hands back.

## Step 1: Understand the request

Collect these five things:

1. **Tool name.** This gives the slug, in kebab-case.
2. **Purpose.** What users achieve with the tool, and what problem it solves.
3. **Target users,** as the requester describes them.
4. **Platform and context:** a web page, admin panel, Discord bot, API, and so on.
5. **Constraints and out of scope.**

Take what the request and the repo already say: README, CLAUDE.md or AGENTS.md, existing `UX/tools/` docs, and the code area involved. Ask only for what's missing, in one card. Use free text where an answer can't be multiple choice.

If `UX/tools/<slug>.md` already exists, ask: **Update it (keep IDs)** / **Replace it** / **Use a different name**. For an update, see the last section.

## Step 2: Match target users to user-types

For each target user named in Step 1, find the user-type in User_Types.md that matches. A match means the same role and goal, or a name the file already uses.

Then add the user-types the requester didn't name but who will plainly interact with the tool, such as an admin who configures it. Mark these as **suggested**; the user confirms or drops them at the checkpoint.

If a target user has no matching user-type, run **user-types** with `mode=append names="<name 1>; <name 2>"` and continue when it hands back. Don't write the type here: an unreviewed profile would weaken everything mapped to it.

## Step 3: Features

Break the tool into features:

- **One capability per feature.** A feature is one thing a user acts on, named verb + object, for example "RSVP to an event" or "Export attendee list".
- **Split by access.** Split a feature when user-types need different access to parts of it (for example "View attendees" vs "Edit attendees"). Merge when splitting adds nothing.
- **Include supporting features.** Add notifications, settings or admin management when the tool truly needs them. Leave out platform features such as sign-in unless this tool changes them.
- **Expect 4–15.** More than 15 usually means the tool is really several tools. Say so, and ask whether to split it.
- **Fill in Serves.** List the requirement IDs (`UT-NN-Mn` and so on) of the mapped types that each feature satisfies. The coverage check depends on it.

## Step 4: Map and check coverage

1. Run `ux.py init-tool <slug> "<Name>"`. Skip this when updating an existing doc.
2. Fill in Summary, Features and the Feature map:
   - The map has one column per user-type, headed `UT-NN Name`.
   - Mark each cell P (primary user), S (secondary user) or leave it blank.
   - Every feature needs at least one P or S.
3. Run `ux.py check <slug>`. Fix every ERROR.
4. The check also lists coverage gaps: Must-requirements of a mapped type that no feature serves. Propose one response per gap:
   - **Add or extend a feature**, and update Serves.
   - **Served elsewhere:** another tool or the platform already covers it. Say where.
   - **Out of scope:** say why.

   Leave undecided gaps as `Open` in Coverage.

## Step 5: Checkpoint

Show the user:

- the features table;
- the feature map;
- the suggested user-types from Step 2;
- the coverage gaps, each with your proposed decision.

Then ask: "Features and mapping for <Name>: ready for journeys?" with the options **Yes, map the journeys** / **Change something**.

If the user wants a change, ask what in free text. Apply it, re-run `check`, and show the result again. Repeat until they say yes, then record the coverage decisions.

Don't start journeys before that yes. Every journey depends on the feature IDs and the map, so journeys are the most expensive part to redo.

## Step 6: Journeys

Read `references/journey-dimensions.md` and follow its procedure exactly. Write the Journey index and the Journey details. Leave the Journey flows block alone: `sync` generates it from the index, so the diagrams can never disagree with the table.

## Step 7: Finish

1. Run `ux.py sync`. This draws one Mermaid flowchart per user-type and updates each type's "Mapped features" in User_Types.md.
2. Run `ux.py check <slug>`.
   - Fix every ERROR and re-run until there are none.
   - Fix WARNINGs where you can, and mention any that remain.
3. Set Status in the Summary to `Reviewed: journeys mapped (YYYY-MM-DD)`.
4. Report briefly:
   - the file path;
   - the number of features and user-types;
   - the number of journeys, split into main journeys and variants;
   - any Open coverage gaps.

## Updating an existing tool doc

- Keep existing IDs.
- New features and journeys take the next free numbers from `status`.
- Delete removed features and journeys, along with every reference to them. Their IDs are never reused.
- Re-run Steps 3–7 for the parts that changed, keeping the checkpoint before journeys change.
- When a user-type was edited or dropped (user-types will have pointed you here), run `ux.py refs <ID>` first. It shows exactly which features, journeys and coverage rows are affected.
