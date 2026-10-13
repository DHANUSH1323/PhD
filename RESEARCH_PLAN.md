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
