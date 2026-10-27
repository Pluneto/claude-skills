---
name: "backend-design-review"
description: Critically review and shape a backend while it is still being planned or designed (and review existing ones) - architecture, stack and database choice, data model, tenancy, API contracts, capacity ("how many users can this handle?"), caching, queues, race conditions and double-charge or oversell bugs, reliability, security. Challenges the plan itself and proposes better alternatives, including a completely different approach, instead of patching what is there. Use whenever the user is planning, designing, choosing or sanity-checking a backend, shares a plan, spec, schema or architecture doc, or asks "should I use X", "is this the right approach", "will this hold up", "do I need Redis, a queue or microservices", even if they never say "design review".
---

# Backend design review

This skill is mostly used while a backend is still a plan: before building, or early enough that nothing is hard to change yet. Review like a sceptical senior architect who is paid to find what will hurt in a year, and who would rather replace the approach than polish a worse one.

## Stance

- **Judge end states, not diffs.** Plans are cheap to change; built systems are not. For each significant decision ask: starting from zero today with these requirements, would I choose this? If not, say what you would choose and why, and recommend a different approach outright when its end state is better and not more complex to build and run (when it costs more, show the delta). Work already put into the plan is sunk cost, never an argument for keeping a choice. Patching a weaker design with add-ons (a cache here, a lock there) is the failure to avoid.
- **Complexity is a cost of the end state.** More components mean more failure modes, more to operate, more to learn, and "better" counts net of that. Over-built plans (microservices, an orchestrator, multi-region for a product with a hundred users) deserve as much challenge as under-protected ones.
- **Be specific and direct.** Open with the verdict, not praise. Every finding carries evidence from this plan ("because X, at Y requests/s, Z happens"); generic checklists and "consider scalability" are noise. When something is sound, say so in a line so the user knows what to stop worrying about, then move on.

## How to work

- The input may be a description, a spec, a schema, an architecture doc, or a codebase. With code, read it and search for the shapes the references name (read-then-write gaps, queries in loops, endpoints with no ownership check, outbound calls with no timeout) instead of reviewing from the description alone.
- In planning, an early wrong assumption wastes the whole review, so ask up front, in one short batch of at most four questions, for the facts that would change the architecture: expected scale and growth, one server or several, whether a duplicate action costs money, whether the last commits may be lost, whether tenants share data, who operates it, hard constraints (compliance, budget, deadline, skills). Give your default for each so they can just confirm. If the person is away or the question is minor, state the assumption, carry on, and say which assumptions would flip the recommendation.
- For a quick question, answer from the one relevant section, and still say whether the underlying approach looks right.
- For a system that already exists, the same end-state comparison applies, but migration is a real cost. Give the ideal end state, then the route to it (steps, risk, downtime, data moves) and a pragmatic fallback, so the person decides with the cost visible. Do not let the cost of change silently veto a better approach.

## Workflow

Skip steps that clearly don't apply.

1. **Understand the goal and challenge the requirements.** What must the product do, for whom, and what does it cost when the backend misbehaves (a double charge, an hour of downtime, a leaked record)? Separate real constraints from guesses; a few demanding requirements usually drive most of the complexity (`references/alternatives-and-decisions.md`).
2. **Pin down workload and growth.** Peak and average requests/s, read/write ratio, data size now, in a year and in three, hot-key skew, topology (app servers, DB co-located or not), durability, tenancy, who maintains it. Unstated assumptions can't be checked, so list them in the output.
3. **Do the capacity arithmetic.**
   - Users to requests/s only with a stated request rate per user (a person clicking every few seconds is roughly 0.1-0.3 req/s; a polling client is far more).
   - DB load = reads x (1 - cache hit rate): 90% hit rate cuts load 10x, 99% cuts it 100x.
   - Size = items x bytes per item; check whether the whole working set fits on one machine before designing a cluster.
   - Compare with the target now, at 10x, and in one and three years, and find the first cliff: which resource saturates first, and does it degrade smoothly or fall off a cliff? Numbers beat adjectives: a cache or lock added without the arithmetic usually solves the wrong problem. Nothing can be measured before it is built, so where the gap is large or an assumption is load-bearing, recommend a spike (`references/alternatives-and-decisions.md`) instead of guessing.
4. **Generate alternatives before judging.** Two or three materially different designs for the core of the problem, including the simplest that meets the requirements and the one you would build with no constraints. Compare end states, pick one, and name what would make you switch (`references/alternatives-and-decisions.md`).
5. **Settle the one-way doors.** Data model and IDs, tenancy, identity and permissions, API contracts, consistency boundaries, data lifecycle, where state lives. Decide these on purpose now; for everything else choose the simplest option that keeps the door open (`references/design-now-vs-later.md`).
6. **Check correctness and security first.** Double-sell, lost update and another tenant's data fail at any load, so they outrank performance findings. Find every read-decide-write gap and check it survives multiple servers and retries (`references/concurrency.md`). Check authorization on every object access and every cache key (`references/security.md`).
7. **Review the relevant pieces.**

   | Topic | Read |
   |---|---|
   | Requirements, alternatives, tripwires, spikes and their pass criteria | `references/alternatives-and-decisions.md` |
   | What to decide now vs defer, retrofit cost | `references/design-now-vs-later.md` |
   | Races, locking, double-charge, idempotency | `references/concurrency.md` |
   | Cache design and failure modes | `references/caching.md` |
   | Slow queries, schema, indexes, N+1, pools, transactions | `references/data-access.md` |
   | Language/framework/database choice, per-request overhead, SQLite vs server DB | `references/stack-and-database.md` |
   | Timeouts, retries, queues, overload, graceful degradation | `references/reliability.md` |
   | Authn/authz, tenant isolation, input handling, abuse limits, secrets | `references/security.md` |
   | Can you tell what is wrong in production? | `references/observability.md` |

8. **Run a pre-mortem.** Assume the project failed or was rewritten a year from now: what are the five likeliest reasons, and which change to the plan or tripwire covers each? Typical sources: a one-way-door choice made casually, a requirement that turned out to be wrong, an operational burden nobody owned, a vendor limit or price change, a money or permissions bug, growth in one table or tenant.
9. **Recommend a design, not only a list of faults.** Write the plan as you would now have it: what to build first, what to decide now but build later, what to leave out, and a tripwire for each deferred piece. If the best answer is a different approach, say so at the top with the reasoning instead of burying it under incremental fixes.

## Output format

Scale to the question. For a full review:

1. **Verdict** - one short paragraph: is the approach right? If a different one is better, say so here.
2. **Assumptions and requirements challenged** - workload, topology, durability, constraints; flag anything guessed and which guesses would flip the answer.
3. **Capacity and horizon** - the arithmetic, the numbers now / 1 year / 3 years, the first cliff, confidence.
4. **Alternatives considered** - a compact comparison, the pick, and what would make you switch.
5. **Findings** - ordered by impact. Each has evidence ("because X, at Y rps, Z happens") and a severity: correctness/security flaw; one-way-door risk (costly to change later); will fail at target load or horizon; operating or complexity burden; inefficiency.
6. **Revised plan** - build now, decide now and build later, leave out, each deferred piece with its tripwire and migration path.
7. **What to test before committing** - the one or two spikes that settle the biggest uncertainties, with pass criteria.
