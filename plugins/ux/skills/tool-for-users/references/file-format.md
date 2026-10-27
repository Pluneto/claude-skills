# UX file format

Shared by the **user-types** and **tool-for-users** skills. `scripts/ux.py` parses exactly this format, so keep headings, IDs, table columns and `ux:` markers as shown. Wording inside cells is free.

```
UX/
├── User_Types.md          owned by user-types
└── tools/<slug>.md        one per tool, owned by tool-for-users
```

## IDs

| Thing | Format | Example | Notes |
|---|---|---|---|
| User-type | `UT-NN` | `UT-03` | Next free ID from `ux.py status`. Never reused. |
| Requirement | `UT-NN-<M/S/C/W><n>` | `UT-03-M2` | Letter = MoSCoW priority; numbered per type and priority. |
| Baseline requirement | `BL-<M/S/C/W><n>` | `BL-M1` | Only in the Baseline section. |
| Feature | `F-NN` | `F-07` | Per tool doc. Next free ID from `ux.py status`. |
| Journey | `J-NN` | `J-12` | Per tool doc. Next free ID from `ux.py status`. |

Lists inside a cell are separated by `;`. Paths use `>` between feature IDs.

## UX/User_Types.md

Create it with `ux.py init` (writes the header, ID tracker, Index block and Baseline section). Then add one section per user-type, in ID order:

```markdown
## UT-03 · Organiser

**Description:** A committee member who plans events and needs to know who is coming.
**Goals:**
- Publish an event with all practical details
- Know numbers in time to book the room and food
**Access level:** Elevated
**Contexts:** Desktop; Returning
**Based on:** G-COM-03 Organiser
**Evidence:** supabase/migrations/001_roles.sql:3; README.md:4

### Requirements

| ID | Priority | Requirement |
|---|---|---|
| UT-03-M1 | Must | Can publish an event without help from a developer. |
| UT-03-M2 | Must | Can see an up-to-date attendee count at any time. |
| UT-03-S1 | Should | Can message everyone who signed up. |
| UT-03-C1 | Could | Can copy last year's event as a starting point. |
| UT-03-W1 | Won't | Handle payments for tickets. |

### Mapped features

<!-- ux:mapped:UT-03:start -->
_Not mapped to any tool yet._
<!-- ux:mapped:UT-03:end -->
```

Field rules:

- Heading: `## UT-NN · Name`. The name is what this product calls them.
- **Access level:** exactly one of `Anonymous`, `Signed-in`, `Elevated`, `Admin`, `System`.
- **Contexts:** situational contexts from this list that apply: Mobile; Desktop; Assistive tech; Slow/offline network; Language; Low digital confidence; First time; Returning.
- **Based on:** a glossary ID and name, or `None (written fresh)`.
- **Evidence:** `path:line` references, or `User-specified`, or `Glossary only`.
- Requirement priority words: `Must`, `Should`, `Could`, `Won't`, matching the ID letter.
- Everything between `<!-- ux:…:start -->` and `<!-- ux:…:end -->` is written by `ux.py sync`. Don't edit it by hand; the next sync overwrites it. A missing Mapped features block is added by sync.

## UX/tools/<slug>.md

Create it with `ux.py init-tool <slug> "<Name>"`. The slug is kebab-case. Section headings are fixed (numbers optional): Summary, Features, Feature map, Coverage, Journeys.

### Features

```markdown
| ID | Feature | What it does | Serves |
|---|---|---|---|
| F-01 | Browse events | Lists upcoming events with places left | UT-02-M1 |
| F-02 | RSVP to an event | Member says they're coming; gets confirmation | UT-02-M2; UT-02-S1 |
```

**Serves** lists the requirement IDs this feature satisfies, or is left empty.

### Feature map

One column per mapped user-type, header `UT-NN Name`. Cells: `P` (primary user), `S` (secondary/occasional), blank (doesn't use it). First cell of each row starts with the feature ID.

```markdown
| Feature | UT-02 Member | UT-03 Organiser |
|---|---|---|
| F-01 Browse events | P | S |
| F-02 RSVP to an event | P | |
```

### Coverage

One row per Must-requirement of a mapped user-type that no feature serves. Decision is exactly one of `Served elsewhere`, `Out of scope`, `Open`.

```markdown
| Requirement | Decision | Note |
|---|---|---|
| UT-02-M3 Can update their profile | Served elsewhere | Account settings page (UX/tools/account.md) |
```

### Journeys

Three sub-sections, in this order: `### Journey index`, `### Journey flows`, `### Journey details`.

Journey index, one row per journey:

```markdown
| ID | User type | Intent | Entry | Path | Outcome | After | Variant of | Context |
|---|---|---|---|---|---|---|---|---|
| J-01 | UT-02 Member | Wants a spot at Friday's event | Notification; Direct | F-01 > F-02 | Success | Gets a confirmation; returns on the day for the address | | |
| J-02 | UT-02 Member | Wants a spot at Friday's event | Shared link | F-02 | Blocked | Event is full; joins the waitlist and waits for a message | J-01 | |
```

- **Outcome:** exactly one of `Success`, `Partial`, `Abandoned`, `Error`, `Blocked`.
- **Path:** empty (`—`) only for a Blocked journey that ends before any feature.
- **Variant of:** blank for a main journey; the main journey's ID for a variant.
- **Context:** blank unless the context changes the path or outcome.

Journey flows: only the generated block. `ux.py sync` draws one Mermaid flowchart per user-type from the index.

```markdown
<!-- ux:flows:start -->
<!-- ux:flows:end -->
```

Journey details: one section per main journey. Variants get no section of their own.

```markdown
#### J-01 · UT-02 Member · RSVP to Friday's event

| Stage | What happens | Feature |
|---|---|---|
| Intent | Wants to be sure of a spot at Friday's event. | — |
| Arrival | Taps the event reminder in Discord; lands on the events list, already signed in. | — |
| Use 1 | Scans the list, sees Friday has 6 places left, opens it. | F-01 |
| Use 2 | Taps "I'm going", sees the confirmation. | F-02 |
| After | Gets a confirmation message; comes back on the day to check the address. | — |

Variants: J-02 (Blocked: event full → waitlist), J-03 (Error: RSVP fails to save).
```
