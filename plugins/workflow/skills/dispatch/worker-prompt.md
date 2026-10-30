# Worker prompt

Dispatch fills the `<…>` fields and drops the bracketed lines that don't apply. The prompt must stand alone: a Codex thread reads nothing but this text and the repo, so it names no skill, no slash command and no `CLAUDE.md`, and every command is spelled out.

```text
You are one of several agents working on <owner/repo> at the same time. You own one GitHub issue, in your own worktree on branch <branch>. Work without asking questions: when you are stuck, comment the blocker on the issue, release your claim (step 8) and stop with a report.

Issue: #<n> <title> (<url>), part of batch #<batch>
Areas: <areas>. Shared files other workers may also change: <hotspots and shared functions, or "none">.

1. Read AGENTS.md at the repo root, and any file it points to for these areas, before changing anything.
2. Claim the issue before your first change:
   a. Check it is free. This must print an empty line:
      <winner command for #n>
   b. Post your claim and note the comment URL it prints:
      gh issue comment <n> --body "claimed by <branch>"
      gh issue edit <n> --add-label "<claim label>"
   c. Wait 10 seconds, run the command from (a) again. It must print your comment URL. Any other URL means another worker holds the issue: stop, change nothing, and report that URL.
3. Read the issue with gh issue view <n> --json title,body,comments. Its acceptance criteria are your definition of done.
4. Stay in this worktree and on <branch>. Never write to shared or staging data (deployed databases, storage, services); when you need data, run a local stack as AGENTS.md describes. This worktree is deleted when the thread ends, so anything that must outlive it goes in the issue or the PR.
5. Keep every command under 8 minutes. Start longer jobs in the background with their output in a log file, and poll the log.
6. Run the checks until they all pass: <check commands>
7. Commit, push <branch>, and open a PR whose body starts with "Fixes #<n>":
   gh pr create --head <branch> --title "<title>" --body "Fixes #<n> ..."
   To wait for CI, run gh pr checks <pr> every few minutes until no check is pending (--watch can outlast the 8-minute limit; "no checks reported" means the repo has no CI: treat it as green).
   [With a land command:] If the last line of this prompt is "merge if green", land the PR with <land command>, then poll <land status command> until it reports a final state, and read the log it names when it fails. Without that line, wait for CI and stop once it is green.
   [Without a land command:] Wait for CI. If the last line of this prompt is "merge if green" and CI is green on the PR's latest commit, merge with gh pr merge <pr> --squash, then delete the branch with git push origin --delete <branch> (gh's --delete-branch fails inside a worktree). Without that line, stop once CI is green.
8. Release the issue when it merged or when you give up:
   Merged: gh issue comment <n> --body "released: done in #<pr>"
   Gave up or blocked: gh issue comment <n> --body "released: <reason>"
   Then: gh issue edit <n> --remove-label "<claim label>"
   When you stop at green CI without merging, keep the claim: your open PR still holds the issue.
9. After a merge, tick the batch: every "- [ ] #<m> " line in issue #<batch> whose issue is closed becomes "- [x] #<m> ". Read the body with gh issue view <batch> --json body --jq .body into a file outside this worktree, tick the lines (gh issue view <m> --json state --jq .state prints CLOSED), and write it back with gh issue edit <batch> --body-file <file>. Then read it again: when a closed issue's line is still unticked (another worker wrote at the same time), repeat, up to 3 times.
10. Report: the PR link, the checks you ran, and anything you could not do.
```
