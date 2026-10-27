# Research Plan: Fewer Tools or Better Descriptions?

Locked: 2026-10-06. Author: Dhanush Babu Ramadoss.
Any change after this date is recorded at the bottom with a date and reason.

## 1. Question
When an LLM agent sees many tools, including tools that look like the right one,
what helps more: showing fewer tools, or writing better tool descriptions?
At the same prompt size, which choice gives higher task success?

## 2. Motivation
In production, an agent exposed to about 58 tools made out-of-scope calls and
invalid arguments. Cutting tools and rewriting descriptions fixed it, but both
changed at once, so the cause is unknown. This study separates the two.

## 3. Gap in prior work
Better descriptions, tested alone:
- Guo et al. 2026 (arXiv 2602.20426): rewrote descriptions as tool count grew
  to 150+; 90% of added tools were random; single query, no simulated user.
- Hasan et al. 2026 (arXiv 2602.14878): augmented MCP descriptions on 202 tools;
  never varied tool count; no simulated user.
Fewer tools, tested alone:
- ToolMenuBench 2026 (arXiv 2606.15508): varied menu size (25/100/250) and
  distractor type, including near-duplicates; compared filtering methods only;
  synthetic mocked environment, no simulated user, descriptions never improved.
Confusing tools, tested as robustness:
- ToolSandbox 2024 (arXiv 2408.04682): multi-turn with simulated user; added
  0/3/10/all distraction tools, prioritizing domain overlap and textual
  similarity; removed descriptions (scrambling) but never improved them.
- Rabinovich and Anaby-Tavor 2025 (arXiv 2504.00914): BFCL single-turn,
  toolkit expanded with semantically related tools.
- When Simulation Lies / RobustBench-TC 2026 (arXiv 2605.11928): single-turn,
  same-name and functionally similar distractors.
Both levers touched, but never compared:
- SkillsInjector 2026 (arXiv 2605.29794) varies the number of injected
  skills and rewrites their descriptions on tau2-bench, but the objects are
  procedural skills rather than tool schemas, and the two levers are
  ablated inside one system rather than tested against each other.
- WorkSurface-Bench 2026 (arXiv 2607.25765) compares removing irrelevant
  tools against a prompt hint; the second arm is not a description change,
  and the setting is single-turn.
- Action-Space Shaping 2026 (arXiv 2609.34971) merges, splits and strips
  tool schemas with tasks fixed and finds success ranging from 0 to 97
  percent from the interface alone. It degrades descriptions but never
  improves them.
- ToolScope 2025 (arXiv 2510.20036) places a description merger beside a
  retriever in one ablation, measured on selection accuracy in single-turn
  settings.

This study is the first to test tool-set reduction and description
improvement as competing remedies for the same failure, in one factorial
design on end-to-end task success, with prompt tokens held equal across
arms, against both look-alike and unrelated distractor tools, on
executable tool definitions in a multi-turn benchmark with a simulated
user. The nearest prior work degrades rather than improves descriptions
with a simulated user (ToolSandbox), rewrites injected skills rather than
tool schemas without a fewer-versus-better comparison (SkillsInjector),
rewrites descriptions under distractors without a reduction arm
(Trace-Free+), or compares tool removal against a prompt hint rather than
a description change (WorkSurface-Bench). None of them controls prompt
size.

## 4. Benchmark
Primary: tau2-bench retail. 16 native tools, 3,188 schema tokens, 1,402 policy
tokens (o200k_base), 114 tasks, graded on final database state.
Version: tau2-bench 1.0.1. The upstream base is Sierra's commit
5bfa7e37b36656b37dc6d022156be6563c1007f3. All runs use my fork at
https://github.com/DHANUSH1323/tau2-bench on the research branch, pinned
at commit 5e311652bbce2a1fc6ada8fe7a8e7f08a1cf43a4 and included in this
repo as the submodule benchmarks/tau2-bench. The fork differs from
upstream only by adding the websockets dependency; no tool or task code
is changed, so results remain comparable with other work on v1.0.1. The
tau3 release fixed 26 retail tasks, so scores are only comparable within
one version.
Secondary: BFCL multiple (selection-only sanity check, single call per query).
BFCL look-alikes may reuse ibm-research/BFCL-FC-robustness where it fits.
BFCL runs use my fork at https://github.com/DHANUSH1323/gorilla on the
research branch, pinned at commit 0fd3d3a4da9e8eb0c9df592a9b2c85a40264ebe8
and included as the submodule benchmarks/gorilla. The fork carries the
claude.py handler patch from Step 1 and nothing else. Exact package
versions are in bfcl-lock.txt.
Airline only if budget remains. Telecom excluded (5,160-token policy dominates
context; user-side tools add a confound).
Descriptions come from tool docstrings via docstring_parser in
src/tau2/environment/tool.py.
Parameter descriptions come from the docstring Args: section (verified
2026-10-13). Tool schemas are sent via LiteLLM in the standard
function-calling format. Pydantic adds a "title" field per parameter;
schema token counts include it.

## 5. Conditions
Description (tool names and parameter schemas never change):
- D-min: one-line purpose; parameter names and types only.
- D-orig: benchmark original.
- D-rich: original plus when to use and when not to use, parameter constraints,
  output, cross-tool and cross-parameter dependencies. Generated from the schema
  only with Guo et al.'s trace-free prompt (Appendix B.3), by a model family
  different from the agent. No policy content. No examples (Hasan et al. found
  examples add tokens without significant benefit). Hand-checked, then frozen.
- D-long (BFCL only): D-orig padded to D-rich length, no new information.
Tool count: 16, 32, 64, 128 (0, 16, 48, 112 fake tools added).
Fake tool type (taxonomy follows ToolMenuBench):
- Unrelated: cross-domain tools from other tau2 domains.
- Look-alike: near-duplicates of real retail tools (similar name and
  description, different scope such as legacy, admin, bulk, other entity) and
  schema-compatible wrong tools (same arguments, wrong effect). All return an
  error when called.
Tool order shuffled per trial with a logged seed.

## 6. Minimum grid (never cut)
tau2 retail, one agent model, 3 trials per task:
1. D-min, 16 tools, none
2. D-rich, 16 tools, none
3. D-min, 64 tools, unrelated
4. D-rich, 64 tools, unrelated
5. D-min, 64 tools, look-alike
6. D-rich, 64 tools, look-alike
Extensions in order if budget allows: 32 and 128 levels; D-orig; second agent
model on cells 5 and 6; airline.
Cut order if over budget: 128 level; D-orig; second model; trials 3 to 2;
tasks to a seeded 40-task subset.

## 7. Cost and time (from Step 1 runs)
- BFCL: cost per task ~$0.0013, time per task ~1 s
  (multiple_0-4, Claude Haiku 4.5, Oct 4 2026).
- tau2 retail: not run in Step 1. Airline proxy, same model and trial count
  (5 tasks, Claude Haiku 4.5, Oct 4 2026): cost per task ~$0.07, time per
  task ~25 s. Retail has comparable scale (16 vs 14 tools, 3,188 vs 2,972
  schema tokens), so these figures size the budget; measured retail numbers
  will be recorded in the change log at the Oct 18-19 pilot.

## 8. Hypotheses
H1. Success falls as tool count rises, faster with D-min than D-rich.
H2. D-rich helps more against look-alike fake tools than unrelated ones.
H3. At equal schema tokens, fewer tools with D-rich beat more tools with D-min.
H4. D-rich raises turns and tokens per task; cost per success is reported.

## 9. Metrics and analysis
Primary: pass^1 on database state, paired bootstrap 95% CI over tasks.
Secondary: pass^3, fake-tool call rate, invalid-argument rate, turns, tokens,
cost per successful task.
Model: success ~ description x count x fake_type + (1 | task).
Equal-token pairs chosen on Oct 17 from measured D-min and D-rich tokens.
Failure review: 30 failed runs classified by hand.

## Change log
- 2026-10-13. Check A (long descriptions). Prediction from reading
  src/tau2/environment/tool.py (_get_description joins short and long
  description with a blank line unless use_short_desc is set; same
  convention as the OpenAI Agents SDK and FastMCP converters): text after
  the first paragraph reaches the model. Test: added a second docstring
  paragraph containing MARKER to get_order_details, generated
  openai_schema. Result: MARKER present in "description". D-rich
  descriptions may be multi-paragraph. Probe reverted; no code change kept.
- 2026-10-13. Check B (parameter descriptions). In the same schema, the
  order_id description equals the docstring Args: text. Parameter
  descriptions come from Args: and appear under
  parameters.properties.<name>.description.
- 2026-10-13. Ran the scoop check planned for Part C. Across roughly
  150 papers, no prior work compares the two fixes in one setup. Added four
  near-misses to Section 3 and reworded the gap statement so it names what
  is actually new: the two remedies compared head to head, in one factorial
  design, at equal prompt size, on executable tool definitions, with a
  simulated user. Details in notes/papers.md.
- 2026-10-19. Step 4 build (STEP4_SPEC.md) departs from the locked plan in
  four places. (a) Grid: three cells added to the six in Section 6. Two
  retriever cells show the agent only the 16 of 64 look-alike-cell tools
  closest to the user's messages so far, under D-min and D-rich; this is
  the practical form of "fewer tools" and gives H5 (retriever vs
  perfect removal vs rich descriptions). One token-matched cell shows
  D-min with 16 real plus N look-alikes, N chosen so that its schema
  tokens equal the D-rich 16-tool cell within 5%; this is the direct test
  of H3. Nine cells, 3,078 conversations. (b) Tool order: fixed per task
  (sorted by name, shuffled with the task id as seed) rather than per
  trial, so the three trials of a task are paired across cells and order
  varies across tasks. (c) Budget cut: a seeded half of base (57 tasks,
  random.Random(57).sample) replaces the 40-task subset, to keep the
  paired bootstrap's power. (d) Unrelated fakes: tau2 airline and telecom
  give only 23 usable tools after removing name collisions, so BFCL v4
  multiple functions were added to the candidate pool (461 candidates).
  Selection: maximum cosine similarity of each fake's name, description
  and parameter names to the 16 real tools under
  sentence-transformers/all-mpnet-base-v2; 48 drawn with seed 2026 from
  candidates scoring below the lowest look-alike. Measured: look-alikes
  0.50 to 0.87 (median 0.70), selected unrelated 0.10 to 0.41 (median
  0.25); no overlap. results/similarity.csv and similarity.png.
- 2026-10-19. Stimuli built. D-orig and D-min exported from the retail
  docstrings by scripts/export_dorig.py (D-min = first sentence, no
  parameter text). 64 look-alikes (4 per real tool: two near-duplicates,
  one schema-compatible wrong tool, one reserve) built by
  scripts/build_lookalike.py from the real signatures; every fake's
  parameter schema is identical to its sibling's (tests/test_lookalike_file.py).
  Fakes are READ type, never mutate state, and return a scoped error that
  names no real tool. Harness recount of the 16-tool D-orig schema: 3,187
  tokens (Step 1: 3,188); D-min: 1,722; policy 1,402. Pilot tasks
  (seed 17): 38, 46, 53, 66, 103. Schedule: D-rich, hand-check,
  manipulation check and pilot follow; the pre-registration is appended
  before any main run.
- 2026-10-20. Spec v2: a third fake-tool kind. Reading the distractor
  literature again (ToolMenuBench's "semantic distractor"; Rabinovich and
  Anaby-Tavor's related-tool expansion; "When Tools Get in the Way", where
  damage tracked how close a tool's function sat to the query; DynamicMCPBench,
  where cross-domain distractors had no measurable effect on capable models)
  showed the grid jumped from cross-domain fakes straight to near-copies and
  skipped the middle: plausible functions of the same store that no task
  needs. Added kind "indomain": 48 tools (coupons, wishlist, cart, store
  pickup, gifts, product content, account settings, subscriptions,
  warranties, financing, shipping, feedback), own parameters, none copying a
  real tool's parameter set or job, one error for all. Cells C10 (D-min) and
  C11 (D-rich). Grid: 11 cells, 3,762 conversations. H1 and H2 become
  three-rung ladders with a trend test. Cross-domain set re-selected: eligible
  below the lowest look-alike and below the in-domain median, then a keyword
  filter removes shopping-flavoured candidates (the embedding cut alone kept
  two); 48 drawn with seed 2026; the Oct 19 set is kept at
  fake_tools/old/unrelated_v1.json. Measured under all-mpnet-base-v2, max
  cosine to a real tool, medians: look-alike 0.69, in-domain 0.37,
  cross-domain 0.21; one-sided Mann-Whitney p < 1e-13 for both steps;
  confirmed under all-MiniLM-L6-v2 (0.69, 0.42, 0.24; both p < 1e-14).
  The middle rung is defined by domain, not by text distance; on the
  embedding axis it sits nearer the cross-domain rung. Runs will go in trial
  blocks (trial 1 of every cell, then 2, then 3) so a cut removes a trial,
  never a cell. Agent chosen by rule before any fake-cell result: the
  cheapest model with a published retail pass^1 between 0.55 and 0.80.
  Temperature 0 is kept; the Claude 5.5 models reject it, so Anthropic roles
  use the 4.6 generation.

## Pre-registration (locked 2026-10-26, before any main run)

This section fixes the experiment before the first main-run conversation.
Everything below was decided and written down with only the pilot (five tasks per
cell, never reused) having run. Changes after this point go into a dated
amendment, never into this text.

### 1. Versions
- tau2-bench v1.0.1, submodule at commit 5e31165 (`git describe`: v1.0.1-51-g5e31165),
  unmodified. Retail domain: 16 tools, 114 tasks in the `base` split.
- PhD repo: fake tools and descriptions frozen at commit 41c7ca5 (`freeze fake tools v2`,
  2026-10-21). Models fixed at fb94022 (`models.env`, 2026-10-22). Harness fix and judge
  scores at 91871ed (2026-10-23).

### 2. Models
All at temperature 0.

| Role | Model | Why |
|---|---|---|
| A, agent | gpt-4.1-mini-2025-04-14 | Rule: the cheapest model whose published tau2 retail pass^1 lies in [0.55, 0.80]. Published 0.66 (tau2-bench paper, gpt-4.1 user). Pilot C1 result on the five pilot tasks: 1 of 5 at concurrency 3, 3 of 5 at concurrency 5 (same tasks; the two runs are separate conversations). |
| U, user simulator | gpt-4.1-2025-04-14 | tau2's default, identical in every cell. |
| G, rich-description generator | anthropic/claude-opus-4-6 | Run once on 2026-10-20, frozen. A different family from A, J1 and J2. |
| J1, J2, checklist judges | gpt-4.1-2025-04-14 and gemini/gemini-3.6-flash | Two families, neither the generator's: the generator is a Claude model, so no Claude model judges. |
| S, similarity embedding | st:sentence-transformers/all-mpnet-base-v2 | Used for the fake-tool ladder check and the cross-domain selection. |
| R, retriever embedding | st:sentence-transformers/all-MiniLM-L6-v2 | Used in cells C7 and C8 and for the confirmation run of the ladder check. Differs from S. |
| NL-assertion grader | gpt-4.1-2025-04-14 | Fixed by tau2. |

A is not changed after any main-run result of a fake cell has been seen. A second agent
model, if ever run, is an extension on C1, C3, C10 and C5 only.

### 3. Run settings
`seed=300` (identical in every cell, which pairs the cells), `max_steps=200`,
`max_errors=10`, `hallucination_retries=0`, 3 trials, `base` split, 5 conversations at a
time (the pilot showed no rate-limit errors at 3 or at 5). Runs go in trial blocks: trial 1
of all 11 cells, then trial 2, then trial 3; cell order inside a block C1, C5, C10, C3, C6,
C11, C4, C2, C9, C7, C8. Every run is logged to `logs/<cell>_T<trial>.log`; tau2's warning
for a reply cut off by the output-token limit is counted per cell afterwards
(`scripts/count_truncation.py`). Pilot tasks 38, 46, 53, 66, 103 (seed 17); pilot runs are
never reused. Spending cap at the start: 100 dollars on the OpenAI account against a pilot
projection of about 164 dollars for three trials; the cap is raised after block 1 once the
real per-block cost is known, or rule 17 applies.

### 4. Grid
Eleven cells. Every fake cell adds 48 tools to the 16 real ones.

| Cell | Description | Extra tools | Note |
|---|---|---|---|
| C1 | D-min | none | |
| C2 | D-rich | none | |
| C3 | D-min | 48 cross-domain (`unrelated`) | count control |
| C4 | D-rich | 48 cross-domain | |
| C10 | D-min | 48 in-domain, other functions of the same store | middle rung |
| C11 | D-rich | 48 in-domain | |
| C5 | D-min | 48 look-alikes | near rung |
| C6 | D-rich | 48 look-alikes | |
| C7 | D-min | 48 look-alikes, agent sees the 16 most similar to the user's messages | retriever |
| C8 | D-rich | same | retriever |
| C9 | D-min | 54 look-alikes | token-matched to C2 |

### 5. Measurements already taken
- Manipulation check (`checklist/judge_scores.csv`): 16 real tools times three variants,
  plus 10 fake tools (seed 2026) times three variants, scored by J1 and J2 on 15 yes/no
  questions. Krippendorff alpha between judges 0.774 (needed 0.6). Mean share of yes on the
  real tools: D-min 0.062, D-orig 0.229, D-rich 0.498. One-sided paired Wilcoxon over the
  16 tools: D-orig > D-min p = 4.8e-4, D-rich > D-orig p = 2.2e-4. PASS. Fakes, secondary:
  0.057, 0.147, 0.513. Human ratings (30 blind items, `checklist/human_sheet.csv`) were
  not required for the pass and are reported separately if filled in.
- Hand-check of the real tools' D-rich against the retail `tools.py`: 274 sentences read
  one by one; 16 removed because they stated a constraint the code does not enforce, or
  contradicted the original description or the policy (`descriptions/drich_check.md`
  records every verdict). Two minor inaccuracies were left in on purpose: the calculate
  example "2 ++ 3", which Python accepts, and "stock levels" in get_item_details, where
  availability is only a yes/no. The in-domain fakes were checked against rule 7 twice: their
  D-orig by script, and their D-rich (841 sentences across 48 tools) by a word screen for
  every real-tool job, followed by a reading of the 72 flagged sentences in context and of
  the opening sentences of all 48. No sentence claims a real tool's job; nothing was removed.
- Fake-tool ladder (`results/similarity.csv`, `results/similarity_confirm.csv`): score =
  max cosine of `name + D-orig + parameter names` to any real tool. Under S, medians
  look-alike 0.688, in-domain 0.373, cross-domain 0.211; look-alike > in-domain p = 1.8e-17,
  in-domain > cross-domain p = 5.0e-14 (one-sided Mann-Whitney); overlaps: 2 in-domain
  scores at or above the lowest look-alike, 22 cross-domain at or above the lowest
  in-domain. Under R, with no selection: medians 0.688, 0.418, 0.238; p = 4.7e-16 and
  8.2e-15; overlaps 15 and 24. PASS under both. The middle rung is defined by domain, not
  by text distance; on the embedding axis it sits nearer the far rung.
- Schema tokens (`results/tokens.csv`, tiktoken, after the hand-check deletions): C1 1,722;
  C2 8,021; C3 7,268; C4 34,544; C5 7,189; C6 32,135; C10 6,391; C11 29,616; the 16 real
  tools with D-orig 3,187. C9 uses N = 54 look-alikes, 7,993 tokens, within 0.3% of C2.
  The three rungs differ in schema tokens because the tools differ; results are also
  reported per 1,000 schema tokens as a secondary view.
- Pilot (55 conversations, 2.40 dollars, mean 26 s per conversation): every cell ran its
  five tasks, no crash, no truncated reply, tool counts as in the grid (verified offline:
  16, 64, and 70 for C9). Fake tools were
  called in C5 (2 calls), C6 (1), C7 (27), C8 (8), C9 (2) and never in C3, C4, C10, C11
  across five tasks. In C7 the retriever's 16 tools changed from turn to turn, as
  specified; replaying it offline showed only 3 to 5 real tools among the 16 and the task's
  needed tools often absent, so C7 is expected to score low. Pass counts on five tasks are
  not read as results.

### 6. Rules
1. Fakes are READ type and always raise an error. Errors fit their scope and never name or
   hint at the correct tool.
2. Each fake has its own D-min, D-orig and D-rich, built by the same rules as the real tools.
   A fake's D-rich may name a real tool.
3. Tool order: sorted by name, then shuffled with `random.Random(str(task.id))`. Same task,
   same order in every trial and every cell; each task a different order.
4. Which fakes are used when fewer than the pool are needed: look-alikes by `rank` (all of
   rank 1, then 2, then 3), names sorted and shuffled with `random.Random(2026)` inside each
   rank. In-domain and cross-domain cells use all 48. The look-alike pool is 64 (16 per rank).
5. The real tools' D-rich was generated once, without knowledge of any fake, and is identical
   in every cell.
6. D-rich keeps all content of D-orig and adds only interface facts. It adds nothing from
   `policy.md` that is not already in D-orig. Every constraint it states is enforced by the
   code in `tools.py`.
7. In-domain fakes are plausible features of the same store that no retail task needs. No
   D-orig or D-rich claims a job that a real tool does: looking up users, orders, items or
   products; cancelling, returning, exchanging or modifying an order; changing an address or
   payment; transferring to a human.
8. In-domain fakes have their own parameters; none has exactly the parameter set of a real
   tool. All parameters required. One error for all: "This service is currently unavailable."
9. Excluded on purpose from the in-domain set: `track_shipment` and `check_gift_card_balance`,
   because real tools already return that information.
10. Cross-domain candidates: tau2 airline and telecom tools (names colliding with retail
    removed) plus BFCL v4 `multiple` functions. banking_knowledge is not used.
11. Cross-domain selection: eligible if the similarity score is below the lowest look-alike
    score and below the in-domain median; 48 drawn from the eligible set, sorted by name,
    with `random.Random(2026).sample`, after a keyword filter removed shopping-flavoured
    candidates.
12. Similarity score of a tool: maximum cosine similarity of `name + D-orig description +
    parameter names` to the same text of any of the 16 real tools, under S.
13. Ladder pass: look-alikes (ranks 1 to 3) > in-domain and in-domain > selected cross-domain,
    each by one-sided Mann-Whitney U at p < 0.05. Overlap counts are reported, not required
    to be zero.
14. Confirmation: the same check, no selection, under R. A failure under R is reported as a
    limit, not fixed by changing files.
15. Retriever (C7, C8): query = all user messages so far, joined, last 2,000 characters; tool
    text = name + description + parameter names in the cell's variant; cosine similarity,
    top 16, recomputed before every agent response; model R.
16. Trial blocks as in Section 3. A provider change or an outage then hits every cell alike,
    and a time cut removes a whole trial, never a cell.
17. Cut order if over budget or time: drop trial 3 (stop after block 2), then a seeded half of
    `base` (57 tasks, `random.Random(57).sample`). The 11 cells are never cut. Block 3 is
    skipped if it cannot finish by the morning of Wednesday 2026-10-28.

### 7. Hypotheses
P(Cx) is pass^1 of cell Cx, the per-task mean over trials. Damage D(Cx) = P(C1) - P(Cx).
Description gain G(a, b) = P(b) - P(a) for a D-min cell a and its D-rich partner b.

- H1, extra tools hurt, and more as they get closer to the real ones. D(C3) >= 0,
  D(C10) > 0, D(C5) > 0, and D(C3) < D(C10) < D(C5). Primary contrasts: C1 vs C3, C1 vs C10,
  C1 vs C5, C3 vs C10, C10 vs C5.
- H2, rich descriptions help more as the extra tools get closer. G(C3, C4) < G(C10, C11) <
  G(C5, C6). Primary contrasts: G(C10, C11) - G(C3, C4) and G(C5, C6) - G(C10, C11).
- H3, equal token budget. C2 (16 tools, D-rich) vs C9 (16 + 54 look-alikes, D-min, same
  schema tokens within 5%). Two-sided.
- H4, cost. Turns, tool calls, fake calls and tokens per conversation: C6 vs C5 and C11 vs
  C10. Secondary.
- H5, removal by retrieval vs descriptions. C7 vs C1 (how close realistic removal gets to
  perfect removal), C7 vs C6 (retrieval vs descriptions at 64 tools), C8 vs C7 (whether they
  add up).

### 8. Analysis
- pass^1 as the per-task mean over trials; paired bootstrap over the 114 tasks, 10,000
  resamples, 95% CI and two-sided p for every primary contrast.
- Holm correction inside each hypothesis family (H1 five contrasts, H2 two, H3 one, H5
  three); unadjusted values also reported.
- Ladder trend model, one test each for H1 and H2: on cells C3, C4, C10, C11, C5, C6, a
  mixed-effects logistic regression `success ~ variant * rung + (1 | task)` with rung coded
  0, 1, 2. H1 is a negative `rung` slope; H2 a positive `variant:rung` interaction.
- Robustness: `success ~ cell + (1 | task)` over all 11 cells; the same contrasts with each
  fake's measured similarity score in place of rung.
- Secondary metrics: fake-call rate by rung, first fake-call turn, recovery rate (a real tool
  called after a fake), turns, tool calls, tokens, cost per conversation and per success,
  retriever recall of the tools the task needs, truncation count per cell.
- Thirty failures per rung pair, drawn with a seed, classified by hand: fake-tool call, wrong
  real tool, wrong arguments, policy violation, premature end, user-simulator error.

### 9. How the results will be read
Fixed now so that no outcome is reinterpreted later.

| Pattern | Reading |
|---|---|
| D(C3) about 0, D(C10) > 0, D(C5) > 0 | Damage comes from confusion, not count. The cleanest H1 result. |
| All three D about 0 | This agent is robust at 64 tools; the finding is a bound ("48 extra tools cost less than X points"), reported with its CI. Matches DynamicMCPBench for capable models. |
| D(C3), D(C10), D(C5) all about equal and > 0 | Count or prompt length drives the damage, not similarity. |
| G grows with rung | Descriptions matter most where tools are confusable. |
| G flat or negative | Rich descriptions are not a fix for confusable tools; removal is. |
| C9 >= C2 | At equal tokens, more minimal tools is as good as fewer rich ones. |

### 10. Exclusions
Infrastructure or API failures are retried by tau2; conversations still failing are excluded
and counted per cell. User-simulator misbehaviour is not excluded. Truncated replies are
counted per cell and reported, not excluded.

### 11. Limits known in advance
- C1 and C2 are perfect removal, an upper bound for any pruning method.
- Fakes return errors, so the study measures confusion and recovery, not damage from wrong
  actions.
- One domain, one agent model, one user-simulator model.
- The three rungs differ in schema tokens (reported per 1,000 tokens as well).
- In-domain and look-alike tools were written by the author; cross-domain tools were not.
- Look-alike density (48 of 64 tools) is a stress test, above the 2.8% near-duplicate rate
  reported for a random draw of the MCP registry (citation to be added in the write-up).
- The spending cap starts below the projected cost; if it is not raised, rule 17 applies.
- A tau2 behaviour found during the hand-check (`retail/tools.py:538`): when several different items are
  modified in one `modify_pending_order_items` call, every modified item takes the last
  variant's price and options. It affects every cell alike and is left as is.
- The user simulator's text, not only the agent's, varies between runs of the same task even
  at temperature 0 (the pilot's two C1 runs on the same five tasks passed 1 and 3).

### 12. Related work this design builds on
Guo et al. 2602.20426 (rich descriptions; most added tools random and cross-domain);
ToolSandbox 2408.04682 (similarity-prioritised distractors); Rabinovich and Anaby-Tavor
2504.00914 (related distractors; "related vs non-relevant, same tasks" named as open);
ToolMenuBench 2606.15508 (six distractor types including cross-domain and semantic);
DynamicMCPBench 2607.20531 (cross-domain and same-name distractors flat for capable models,
no description or token control, no simulated user); "When Tools Get in the Way" 2609.14157
(one related unnecessary tool suppresses answers; knowledge questions, not tool choice);
"Which Metadata Matters" 2610.14334 (richer descriptions raise selection share among 2 to 5
candidates; single turn, no execution, no removal arm); Action-Space Shaping 2609.34971
(merging retail tools collapses performance); TRACER 2610.21267 (distractors in tau2,
retrieval vs the full set, no description arm); ToolBottleneckBench 2610.21098 (menu
penalty tracks truncation, no token-matched control).

### 13. Novelty statement
To my knowledge, as of October 2026, no study has compared removing tools against improving
tool descriptions at an equal token budget, or tested how that trade-off changes with
distractor similarity, in a multi-turn, simulated-user benchmark. The ladder itself,
distractors in tau2, and description rewriting crossed with tool count are not claimed as new.

### Amendment 1 (2026-10-26, before any pass rate was viewed)

Block 1 is complete: 1,254 of 1,254 conversations, every one of the 11 cells on all 114
tasks, trial 1. The study stops here, at one trial per task in every cell. The reason is
budget: real charges for block 1 came to about 67 dollars against a ceiling of 100, and a
second full block would cost about 60 more. Rule 17 lists dropping trial 3 and then halving
the task set; it does not list stopping at one trial, so this is a deviation, recorded now,
with no pass rate of any cell having been looked at.

Why one full trial rather than a second trial on half the tasks: the pilot conversations
and their block-1 repeats give 60 pairs of the same task run twice in the same cell, and the
outcome differed in 13 of them (22%). With that much run-to-run variation, roughly half the
per-task variance, the 95% interval on a difference between two cells is about ±12 points
with one trial on 114 tasks, about ±10 with two trials on 114, and about ±14 with two trials
on 57 tasks. The half-task option is worse than stopping. Effects smaller than about 10
points may therefore come out as not distinguishable; that is reported as a bound under
Section 9 of the pre-registration, not reinterpreted.

The analysis plan is unchanged: pass^1 per task is the single trial's outcome, and every
contrast, interval and model in Section 8 applies as written. The seeds are fixed per
trial, so trials 2 and 3 can be added later without rerunning trial 1.

Operational notes that touch inference: the OpenAI balance ran out twice during block 1;
the affected conversations ended as infrastructure errors with no messages, were rerun in
full, and none remain. The rich-text 64-tool cells and C8 ran two conversations at a time
instead of five after C6 hit the provider's tokens-per-minute limit; concurrency does not
enter any conversation's content. No reply was cut off by the output-token limit in any
cell. Charges on the provider's side ran about 20% above tau2's internal cost tally; cost
figures in the write-up use tau2's tally and say so.
