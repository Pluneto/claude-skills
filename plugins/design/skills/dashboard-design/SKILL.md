---
name: dashboard-design
description: "Design principles for building or reviewing dashboards, admin panels, data tables, and analytics views. Use when asked to build, design, mock up, or critique a dashboard or data-dense UI, in any framework. Covers letting data drive the UI, progressive disclosure, the invisible UI (hover actions, tooltips, menus, states) that beginner dashboards miss, and how to fix the tells of AI-generated (vibecoded) SaaS UIs: emojis, clashing colors, repeated KPIs, cluttered sidebars/rows, messy pricing and settings pages, and landing pages. Use it whenever someone wants a vibecoded app to look professional."
argument-hint: "[path or description of the dashboard]"
---

# Dashboard Design

Dashboards are easy to style and hard to orchestrate. Apply these rules in any stack. `$ARGUMENTS` may be a path to existing UI or a description of what to build.

## Mode
- **Review**: existing code, a file path, or a screenshot is given. Audit it against the rules and `references/checklist.md`, and report gaps by priority with concrete fixes.
- **Build**: otherwise. Ask only for what is missing (what data, who uses it, main action), then design and write it with the rules applied.
Either way, finish by running `references/checklist.md` and stating what is covered and what is intentionally left out.

## 1. Let the data drive the form
Start from the data: its types, cardinality, and dimensions. Do not start from a generic table.
- **Finite categories** (department, status, severity) become chips or pills. Color-code only when color carries meaning.
- **Numbers** are right-aligned with tabular figures so digits line up by place value (`text-align: right; font-variant-numeric: tabular-nums`).
- **Long text** is truncated with ellipsis and a full-value tooltip, giving other columns room.
- **Inactive or deactivated rows** are dimmed, not hidden.
- **People** get avatars next to or in place of names; the eye matches faces faster than text.
- **Time-based data** (logs, activity, history) should be a timeline, not a time-sorted table. Put it in a sidebar or a second column. Roll time data up into a chart so trends show without hunting timestamps.
- **Color is information**: urgent or critical gets the loudest color (red); everything else stays quiet. Never sprinkle color for decoration.
- Use type icons in column headers to signal data type.

## 2. Progressive disclosure
Hierarchy covers what is shown and what is hidden. Place each action on the **spectrum of explicitness**:
1. Always visible with full label (global primary actions: Add, Share).
2. Always visible icon only.
3. Revealed on hover/focus with a tooltip (secondary actions: remove, copy cell).
4. Behind a menu, popover, swipe, or drawer (rare actions).
Choose by frequency and importance, and by space. Rules:
- The primary action inside a popover or panel comes first and is visible (e.g. the invite field at the top of a Share popover).
- Secondary and destructive actions are revealed when the user looks for them, not permanently ingrained.
- Prefer a popover or drawer over navigating to a new page for small features.
- **Onboarding is sequenced disclosure**: one tooltip at the key action, then the next, or a small checklist. Never a modal explaining everything on first login.

## 3. Design the invisible UI
A dashboard that works is mostly UI not visible at rest. Plan these as part of the design, not afterwards: hover actions, tooltips for icons and ambiguous labels, comment/notes indicators, row and column context menus, popovers, drawers, sort/filter/group builders, onboarding, empty/loading/error states. The full inventory is in `references/checklist.md`. **Tooltips are the most commonly missing piece.**

## 4. Make it memorable
Clear hierarchy, spacing, and useful charts are table stakes; they will not make a dashboard stick. Gut check: would someone screenshot this, and why? Decide what to leave out first.
- **Insight + next action beside the data.** Pair each key chart with its interpretation (what changed, why it matters) and what to do about it, e.g. a summary panel next to the line chart or a recap card. Don't just show what happened.
- **One signature moment, scaled by audience.** Pick the tier (ask once in Build mode if unclear, otherwise state the assumption):
  - **Consumer**: a distinctive visual encoding and/or a delight moment (playful empty or success state) is welcome.
  - **B2B / SaaS product**: at most one signature visual (map, heat map, custom donut); no playful states.
  - **Internal / ops**: insight + action and restraint only; skip signature flourishes.
- **Bounded delight.** Never on critical data, and the "color is information" rule still governs every data color. Delight lives in hero visuals and low-stakes empty/success states.
Examples and mechanisms: `references/memorable-dashboards.md`.

## 5. Avoid the AI-generated look
Vibecoded dashboards share tells that read as untrustworthy. AI wires up logic well but is weak at layout, color, and information architecture, so make these decisions deliberately. These are principles; choose the form that fits the data, product and audience rather than copying one house style.
- **Real icons, not emojis.** One consistent interface icon set; emojis as icons are the loudest tell. Icons must actually render (prefer inline SVG over fonts or CDNs) and be checked in the output.
- **Deliberate color.** A small, hand-picked palette; no clashing defaults or decorative colored chips. Color carries meaning. Data series and categories need clearly distinguishable hues, and sequential or diverging scales must stay perceptually distinguishable at each step (e.g. interpolate between two distinct colors rather than shades of one hue that blur together).
- **Each view has one job.** Don't repeat the same summary metrics across pages; cut elements that do nothing; every visual must yield an insight, otherwise remove it. Match the visual to the data type and meter (a part-of-whole or capped quantity suits a proportional encoding; an uncapped one needs a clear tell), not a thin stat card.
- **Simplify without losing capability.** Decluttering means moving things behind progressive disclosure, never breaking or dropping core functions. Anything that lists items keeps working search, sort and filter; utility pages (account, settings) stay complete for what users expect of them.
- **Structures must scale.** Collections that can grow (items, series, entries) belong in a searchable, sortable, filterable structure, not a fixed set of cards or tiles that clutter as items are added.
- **Give items glanceable context.** Where rows or entries represent things with performance over time, a small trend and change versus the previous period beat a bare number.
- **Comparisons must really compare.** Items that are compared share aligned rows and a consistent form; absence is shown explicitly (e.g. a muted mark) rather than by omission; things that can't be compared are separated clearly from those that can.
- **Concise narrative.** Summaries and "what changed" text are short, specific, and tied to an action; no paragraphs.
- **Navigation and entry points stay lean.** Core destinations only in primary navigation; secondary and account actions in a popover; create and edit flows sized to their content with advanced options collapsed.
- **Billing and settings** need coherent structure (a tabbed or sectioned layout that new areas can slot into) and coherent pricing (a higher tier is never cheaper than a lower one; show real discounts and what the next tier adds).
- **Landing pages** are where trust is won: same color and layout rules, with real product graphics over generic icons.
Concrete patterns that worked in one case, offered as optional recipes: `references/saas-redesign-lessons.md`.

## Beyond the video
- Hover-only actions need keyboard and touch equivalents: reveal on `:focus-within` too, and provide a menu or long-press/swipe path on touch.
- Every view needs designed empty, loading, and error states.
- Color is never the only signal: pair status colors with an icon or label.
- Check contrast on chips and dimmed rows; dimmed must still be readable.

## Output
- Build: working code plus a short note of which disclosure level each action got, what hidden UI was included, and what the signature moment is (or why none, for internal tools), and which AI tells were removed. Before finishing, click through search/sort/filter and confirm icons render.
- Review: findings ordered by impact, each with the rule it breaks and a specific fix; note whether insight + next action and a signature moment are present or missing for the audience tier.
