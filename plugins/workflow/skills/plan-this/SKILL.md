---
name: "plan-this"
description: Turn any goal into a deep, agreed implementation plan. First deepens the goal the way a top professional in that field would, then interviews the user in rounds over a tree of design decisions until nothing is left assumed, then confirms the plan and hands off to /build-this or saves a Markdown plan. Planning only, it never builds. Use whenever the user says "plan this", "/plan-this", "help me plan", "make a plan for", or asks for an implementation plan for any kind of goal. If the user describes a large, multi-step or high-stakes goal without asking for a plan, do not start the interview; offer this skill in one line instead.
compatibility: Requires the research-this skill. The use-available-skills skill is optional.
---

# Plan this

Turn a goal into a plan that is **deeper, not bigger**, researched before anything is decided, and agreed to by the user decision by decision.

This skill only plans: don't act on the goal (write code, create files, book things). Read-only exploration to find facts is fine, and the only file written is the saved plan.

## 0. Check requirements first

Confirm the **research-this** skill is available (it may be listed with a plugin prefix such as `workflow:`). If it is missing, do nothing else: cancel and tell the user that research-this is missing and must be installed before /plan-this can run. Planning without its research would skip the step that keeps plans from reinventing what already exists.

## 1. Deepen the goal

A top professional's version of a task is usually *not* more features. It's a sharper target, better starting material, proper methods, and an outside way to check the result. That's what this step finds.

**Research before you deepen.** If the goal involves third-party software, a service, or a field with current practice, run **research-this** once, at quick depth (standard only when the goal is costly or hard to undo: money, a migration, a large build), on the goal's core question ("what already does <the goal>?") with every constraint the user gave and the decision it feeds. Name the facts the plan needs rather than asking for everything: when the goal installs third-party software, its installer prompts and defaults that affect privacy, exposure or performance, and known problems with the user's exact setup. A narrow brief keeps the run short and on topic. Skip this only for goals that need no outside facts. Fold its verdict and facts into the deepened goal and the interview, so none of it surfaces first during the build. Treat its verdict as a recommendation, not a decision: if the user hasn't chosen the tool or approach themselves, it stays an open question for round 1, with the verdict as the recommended option. If a sub-agent can run it, start it there so the rest of your preparation continues meanwhile.

Then work out four things:

1. **What a top professional would do here that the user didn't ask for.** The step an amateur skips: talking to real users first, measuring a baseline, checking legal requirements, designing the data model before the UI.
2. **The rawest material they'd start from**, instead of what has already been digested. Raw data instead of a summary, the source code instead of a tutorial, actual customers instead of a persona template, the official regulation instead of a blog post about it.
3. **The specific methods and tools they'd use**, by name. Not "test it" but "Playwright end-to-end tests"; not "train more" but "an 80/20 easy/hard split with a long run each week".
4. **What, other than the user or Claude, would show the result is right.** Something outside the conversation: an automated test, a measurement, a real-world outcome, a third-party review, a standard it can be checked against.

Rewrite the goal as a short paragraph that asks for exactly that, keeping every restriction the user set. Deepening never overrides a stated constraint. If a constraint blocks the professional approach, that becomes a trade-off question in the interview rather than something you quietly decide.

**Keep it short: about 200 words in total.** One line per point, then the rewritten goal. The user has to read and approve this before any question, so a wall of text here slows everything down. Offer more detail if they want it; don't front-load it.

**Commit or mark as open.** Everything the rewritten goal states is settled once the user approves it, so it must not come back as a question in round 1. If something is genuinely undecided (which race, which scope), don't half-pick it ("most likely X"); mark it plainly as open, e.g. *"(race: open, first question)"*, and ask it in round 1.

**Show it before you ask.** Text written between tool calls is summarised in the interface, so a question card can appear over a plan the user never read. Send the four points and the rewritten goal with `SendUserMessage` (or as the reply text if that tool isn't available), then ask *"Shall we plan for this deeper version?"* (Recommended: yes) with the question tool, putting the rewritten goal paragraph inside the question text so the user approves something visible right there. If the only way to show the plan is plain text, end the turn after it and ask in plain text. If they adjust, revise and repeat.

## 2. Interview in rounds

Map the plan as a **design tree**. The root is the deepened goal. Every decision branches into the decisions that hang off it: choosing *"online ordering"* opens *"which payment provider"*; choosing *"no ordering"* closes that whole branch.

The **frontier** is every decision whose prerequisites are already settled: the questions you can ask now without guessing at answers you haven't heard yet.

### Skills that fit

Before the first round, run the **use-available-skills** skill on the approved goal for the planning phase. It loads only the skills that pass its written reason test (the need in this goal, what the skill provides, what goes wrong without it), and "none" is a normal result. Use whatever it loads while you map the tree and write the options, so recommendations are sharper (a design-review skill for a backend plan, say). A skill's advice shapes your recommendations only; the user still decides. The skill is optional: if it can't be found (look in ~/.claude/skills, .claude/skills and plugin skill folders too, since the listing can drop entries), skip this and write "not checked" as the Skills line of every milestone. Once the milestones are known (just before step 3, and again if they change at the confirmation), run it for the build phase in record-only mode, passing the milestone list, so it returns, per milestone, the skills that pass its reason test (usually fewer than 3) with their reason lines, without loading them, because /build-this loads them when each milestone starts. Copy the reason lines into the plan as they are, including any "(description only)" mark. Never ask the user which skills to use, and don't spend an interview question on them. Sub-agents often can't see skills, so paste any guidance a sub-agent needs into its brief.

### Each round

1. **Separate facts from decisions.** Facts (what's in the project, what a tool supports, what something costs, what the rules say, what date an event is) are your job, never the user's. Look them up. Where you can dispatch a sub-agent, do so, so the lookup runs while you ask the rest. A running lookup is an unsettled prerequisite: only the questions that depend on it wait; ask everything else now. Without sub-agents, look things up yourself before the round.
   - **Verify before you ask.** Never put a choice to the user that rests on a fact you haven't confirmed ("I'll double-check these dates later"). Check it first, or hold that question until the check is done.
   - **Where to look.** Read freely from whatever is already available: the working folder, connected tools and apps, the web, the user's attached files. Ask before attaching or connecting anything new (adding a repository, enabling a connector, signing in somewhere), since that reaches into places the user didn't point you to. Never change anything while looking.
   - **Choosing among existing options.** When a decision means picking an existing tool, product, provider or approach (which payment provider, which library), offer the options and recommendation from the first research run when it already covers them; only if it doesn't, run research-this at quick depth on that one choice before asking. Plain facts (a price, a date, what a tool supports) stay ordinary lookups.
   - Some facts only the user knows (their current fitness, whether they've already asked their employer). Ask those plainly, without a recommendation or pros and cons, since there's nothing to weigh.
2. **Ask the whole frontier in one round** with the question tool (AskUserQuestion). It holds at most 4 questions per call, so use as many consecutive calls as the round needs, most foundational questions first. If a question depends on another question still open in this round, it belongs to a later round.
3. **Format every question the same way:**
   - Word it so **"yes" accepts your recommendation** ("Should the site use Stripe for payments?").
   - Put the recommended option **first**, labelled "(Recommended)".
   - Give 2–4 options, each, plain ones like "No, adjust it" included, with a **one-line pro and con** in plain language: `Pro: … Con: …`. Avoid jargon; if a term is unavoidable, explain it in a few words.
   - Every con must be real: "Con: none" means it isn't a decision (bundle it as a default or look it up), and even the recommended option costs something.
   - The user can always type their own answer, so no "Other" option is needed.
4. **Read the answers carefully.** A typed answer can open new branches, close others, or even change the goal. Recompute the frontier from what they actually said.
5. **Show one short progress line** before the next round, e.g. *"Round 2 done: 7 decided, 3 open, about 1 round left."*

### Keeping rounds light

Nothing is silently assumed, but not every choice needs its own question: bundle decisions that have a conventional default and no real trade-off into one *"Use these defaults: A, B, C?"* question (Recommended: yes). A "no" turns them back into separate questions next round.

### Plan code simply

If the plan involves code, plan it to follow **KISS**, and **SOLID** for object-oriented code; KISS wins when they conflict. These are standing constraints, so don't spend an interview question on them; record them once under **Constraints** in the plan.

### Needs from you

Keep a running list of what only the user can supply (accounts, keys, real content, sign-offs, physical-world actions) for the plan's **Needs from you** section, tagged *needed early* or *can wait*.

### When the tree is done

The interview ends when the frontier is empty: every branch visited, every decision either answered by the user or listed as an accepted default.

If the question tool isn't available, ask the same way in plain text: numbered, with your recommendation and a one-line pro and con per option, the whole frontier at once, then wait.

## 3. Confirm shared understanding

Summarise in plain language: the deepened goal, every decision with its choice, the milestones with their "done when" checks and skills (each with its one-line reason), how success will be checked overall, and the main risks. Keep it scannable. Then ask: *"Does this match what you want?"* If not, the answer reshapes the tree; go back to step 2 for the affected branches only.

## 4. Next step

Ask with the question tool what to do next, recommending by situation: **Build it now** (recommended when you're working inside a project or workspace where the work can actually be done), **Save a Markdown plan** (recommended when the work happens elsewhere or later), or **Save the plan, then build**.

If they choose to build (with or without saving first), invoke the **build-this** skill with the Skill tool and let it take over; pass the saved plan's path as the argument if you saved one, otherwise it picks the plan up from the conversation. Don't build inside this skill, and don't ask build-this's questions (how to build, which model) yourself. If build-this isn't available, say so in one line, save the plan file, and tell the user to attach it in a session that has build-this.

### Saving

Write `plan-<short-topic>.md` (e.g. `plan-bakery-website.md`) and make it self-contained so a fresh Claude with no other context can act on it; save it in the project's `plans/` folder (create it if missing), never the project root, so plans don't clutter it and /build-this has a place to archive them when done; if there is no project, send it as a file. Start with a title and the line *"Created <date> with /plan-this. Attach this file to a Claude chat and run /build-this (or say "build this plan") to continue."* Then these sections, in order:

- **Goal:** the original request in the user's words, the approved deepened goal, and **Constraints** (everything the user restricted or required; for plans that involve code also "Code follows KISS, and SOLID for object-oriented code"), plus a line **Skills used while planning:** the skills loaded in step 2, each with its reason line, or "none" (with any near-miss notes the helper returned), or "not checked (helper not found)".
- **How we'll know it worked:** the outside checks (test, measurement, outcome, review).
- **Decisions:** a table with #, Decision, Choice and Why (reason or trade-off accepted), followed by any accepted defaults.
- **Needs from you:** *needed early* items (with the milestone that needs each) and *can wait until the end* items (with the placeholder used until then).
- **Steps:** milestones, each with checkbox steps, a **Done when** check and a **Skills:** line giving each build-phase skill for that milestone (exact name, plus the path for one that exists only on disk) followed by its reason line (Need / Provides / Without it), or "none fit", or "not checked" when the helper was unavailable.
- **Risks and assumptions:** each risk with its mitigation, plus any assumption still to confirm in the real world.
