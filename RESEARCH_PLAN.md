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
This study: compares the two fixes head to head, at equal prompt size, against
look-alike and unrelated fake tools, in a multi-turn benchmark with a
simulated user.

## 4. Benchmark
Primary: tau2-bench retail. 16 native tools, 3,188 schema tokens, 1,402 policy
tokens (o200k_base), 114 tasks, graded on final database state.
Version: tau2-bench 1.0.1, commit 5bfa7e37b36656b37dc6d022156be6563c1007f3.
Pinned for the whole study. The tau3
release fixed 26 retail tasks, so scores are only comparable within one version.
Secondary: BFCL multiple (selection-only sanity check, single call per query).
BFCL look-alikes may reuse ibm-research/BFCL-FC-robustness where it fits.
Airline only if budget remains. Telecom excluded (5,160-token policy dominates
context; user-side tools add a confound).
Descriptions come from tool docstrings via docstring_parser in
src/tau2/environment/tool.py.

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
(none yet)
