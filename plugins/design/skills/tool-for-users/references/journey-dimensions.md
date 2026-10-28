# Journey dimensions

A journey is one way a user-type moves through the tool: **Intent → Arrival → Use → After**. "Every variation" means every journey that differs in what actually happens, not every combination of attributes. These rules keep the list finite and make it come out the same each time.

## Dimensions

| Stage | Column | Values |
|---|---|---|
| Intent | Intent | Why the user comes, taken from the type's goals. 1–3 per type for this tool, written as "Wants to …". |
| Arrival | Entry | Fixed vocabulary, in this order: Direct (URL, bookmark, app icon) · Search engine · In-product navigation · Notification (email, push, chat message) · Shared link · Redirect (after sign-in, sign-up or payment) · External integration · Offline (QR code, print, word of mouth). |
| Use | Path | Feature IDs in order: `F-01 > F-03`. Leave it empty (`—`) only for a Blocked journey that ends before any feature. |
| After | Outcome | Success · Partial · Abandoned · Error · Blocked. |
| After | After | One sentence on what happens next: the user leaves, comes back later (and what brings them back), gets notified, moves on to another tool, or someone else acts (organiser, support). |
| (any) | Context | Blank unless a context changes the path or the outcome. Values come from the type's **Contexts** line: Mobile · Desktop · Assistive tech · Slow/offline network · Language · Low digital confidence · First time · Returning. |

Outcomes:

- **Success**: the intent is met.
- **Partial**: the user made progress but isn't done and will come back (saved draft, waitlist, pending approval).
- **Abandoned**: the user leaves by choice (too long, unclear, changed their mind).
- **Error**: a system or validation failure stops them.
- **Blocked**: the user isn't allowed or isn't eligible (not signed in, wrong role, event full, deadline passed).

## Procedure

Work through the mapped user-types in ID order. For each type, take its intents in the order you listed them, and for each intent:

1. **Main journey.** Take the most common entry and the shortest path to Success. Leave Variant of blank.
2. **Entry variants.** For every other plausible entry, ask: does it change the path or the start state? For example, a shared link might land on a detail page and skip browsing, or a user might arrive signed out and have to sign in first.
   - If yes, give it its own row with outcome Success and Variant of set to the main journey.
   - If no, add the entry to the main row's Entry cell, separated by `;`.
3. **Outcome variants.** For each of Partial, Abandoned, Error and Blocked that can realistically happen for this intent, add one row at the point where it is most likely or most costly. Add a second row for the same outcome only when a different point leads to a different After.
4. **Context variants.** For each context on the type's profile, ask: does it change the path or outcome? An example is an assistive-tech user who can't complete a drag-and-drop step.
   - If yes, give it its own row with Context filled in.
   - If no, add nothing. The Baseline requirements already cover it.

**Merge rule:** two rows with the same user-type, intent, path, outcome and context are one row. Combine their Entry and After cells. `ux.py check` reports duplicates as errors.

**Numbering:** J-01 upward, in the order the procedure produced the rows, continuing from the next free ID that `ux.py status` reports. Never reuse a number.

## Journey details

Write a details section for each main journey, in the format shown in file-format.md. Variants get no section of their own; their index row is their full description.
