# Baseline: always-on skill context outside any project

Measured 2026-10-27 with `scripts/measure-context` (before migration).

```
user skill  codebase-design                                    ~70 tok
user skill  dashboard-design                                   ~154 tok
user skill  find-skills                                        ~79 tok
user skill  frontend-design                                    ~55 tok
user skill  grill-me                                           ~0 tok
user skill  grilling                                           ~40 tok
user skill  handoff                                            ~0 tok
user skill  higgsfield-brandkit                                ~235 tok
user skill  higgsfield-generate                                ~254 tok
user skill  higgsfield-marketplace-cards                       ~183 tok
user skill  higgsfield-product-photoshoot                      ~262 tok
user skill  higgsfield-soul-id                                 ~167 tok
user skill  higgsfield-video-explainer                         ~189 tok
user skill  higgsfield-websites                                ~259 tok
user skill  higgsfield-youtube-thumbnail                       ~184 tok
user skill  improve-codebase-architecture                      ~0 tok
user skill  pr                                                 ~8 tok
claude.ai   artifact-emulator                                  ~176 tok
claude.ai   backend-design-review                              ~196 tok
claude.ai   build-this                                         ~95 tok
claude.ai   built-in-browser                                   ~210 tok
claude.ai   chrome-browser                                     ~192 tok
claude.ai   computer-use                                       ~238 tok
claude.ai   deep-research                                      ~146 tok
claude.ai   docs                                               ~253 tok
claude.ai   docx                                               ~235 tok
claude.ai   google-workspace                                   ~241 tok
claude.ai   import-memory                                      ~38 tok
claude.ai   pdf                                                ~110 tok
claude.ai   plan-this                                          ~162 tok
claude.ai   pptx                                               ~242 tok
claude.ai   reflect                                            ~96 tok
claude.ai   research-this                                      ~206 tok
claude.ai   skill-creator                                      ~83 tok
claude.ai   skill-ozempic                                      ~118 tok
claude.ai   skill-updater                                      ~147 tok
claude.ai   solve-this                                         ~140 tok
claude.ai   use-available-skills                               ~181 tok
claude.ai   xlsx                                               ~239 tok
plugin      frontend-design@claude-plugins-official            ~80 tok
plugin      mattpocock-skills@claude-plugins-official          ~1651 tok

41 entries, ~7614 tokens always-on
```

## After cutover (2026-10-27, before the claude.ai copies are deleted)

```
23 entries, ~3794 tokens always-on
```

Baseline ~7614 → ~3794 tokens (−50%). The 9 migrated skills still synced from claude.ai account for ~1341 of the remainder; once they are deleted in claude.ai, expect ~2450 tokens (−68%). Re-run `scripts/measure-context` to confirm.

## After claude.ai deletions (2026-10-27)

```
16 entries, ~2724 tokens always-on
```

Baseline ~7614 → ~2724 tokens (−64%). user-types and tool-for-users still sync from claude.ai (now also in the `ux` plugin); deleting them there removes a few hundred more.

## Merge with mattpocock-skills: before (2026-10-28)

Measured with `scripts/measure-skills` (plugin folders, same formula) before the `merge-mattpocock` branch changed anything. mattpocock-skills counts only the 27 skills its `plugin.json` ships.

```
workflow             build-this                       ~95 tok
workflow             handoff                          ~0 tok
workflow             plan-this                        ~162 tok
workflow             research-this                    ~210 tok
workflow             solve-this                       ~140 tok
workflow             use-available-skills             ~181 tok
skill-tools          reflect                          ~96 tok
skill-tools          skill-ozempic                    ~118 tok
skill-tools          skill-updater                    ~173 tok
ux                   tool-for-users                   ~130 tok
ux                   user-types                       ~110 tok
design               backend-design-review            ~196 tok
design               dashboard-design                 ~155 tok
setup                setup-pluneto-skills             ~0 tok
mattpocock-skills    code-review                      ~108 tok
mattpocock-skills    codebase-design                  ~70 tok
mattpocock-skills    diagnosing-bugs                  ~43 tok
mattpocock-skills    domain-modeling                  ~42 tok
mattpocock-skills    pr                               ~8 tok
mattpocock-skills    prototype                        ~47 tok
mattpocock-skills    research                         ~62 tok
mattpocock-skills    tdd                              ~38 tok
mattpocock-skills    wizard                           ~80 tok
mattpocock-skills    grilling                         ~40 tok
mattpocock-skills    writing-for-agents               ~30 tok
mattpocock-skills    (16 user-invoked skills)         ~0 tok
```

pluneto-skills: 14 skills, ~1766 tokens. mattpocock-skills 1.3.1: 27 skills, ~568 tokens. **Total ~2334 tokens always-on** with every content plugin installed.
