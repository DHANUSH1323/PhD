# Papers

## Scoop check, 13 October 2026

Before starting the build I checked whether anyone had already run this
study. I went through the recent citations of the four papers closest to
my question (ToolSandbox, Rabinovich and Anaby-Tavor, Guo et al., and
ToolMenuBench), searched arXiv for work on tool descriptions, tool
selection, and distractor tools, looked through OpenReview submissions
for ICLR, NeurIPS, ICML, COLM and ACL, and read what the model providers
and a few engineering teams have published. In all, about 150 papers and
30 practitioner sources from 2024 to today.

Nobody has compared reducing the tool set against improving the
descriptions as two competing fixes in the same experiment, and nobody
has held prompt size equal while doing either. The field has split into
two lines of work that cite each other but never test each other: one
line rewrites descriptions, the other shrinks or filters the tool set.

Several papers come close enough that I need to cite them and say how
mine differs. SkillsInjector (2605.29794) works on tau2-bench and varies
both how many skills are injected and how their descriptions are written,
but the objects are procedural skills rather than executable tool
schemas, and it never frames the two levers as alternatives.
WorkSurface-Bench (2607.25765) is the only paper that pits removing
irrelevant tools against a second fix, but that second fix is a prompt
hint, not a rewritten description. Action-Space Shaping (2609.34971)
merges, splits and strips tool schemas with tasks held fixed and finds
success ranging from 0 to 97 percent from the interface alone, which
supports my premise, though it only ever degrades descriptions.
ToolScope (2510.20036) has a description merger and a retriever in the
same ablation table, but measures selection accuracy in single-turn
settings. RobustBench-TC (2605.11928) perturbs both descriptions and
tool sets, again single-turn and as perturbations rather than remedies.
BiasBusters (2510.00307) states in an appendix that the composition of
the tool set matters more than its size, measured on selection bias.
Agent-Facing Information Design (2605.23916) is the only paper I found
that length-matches description variants; it uses two tools and a single
call, but its matching method is worth borrowing.

Two papers on the reliability of tau2-bench itself should also be cited:
TRACE (2610.11678) reports that identical reruns flip 15 to 36 percent of
task outcomes, and a validity audit (2607.02577) finds 18.5 percent
disagreement between the automatic evaluator and humans. Both argue for
running several trials per cell and using paired statistics. Separately,
tau2-bench pull request 602 on 8 October 2026 changed the airline tool
docstrings in a way that may make scores non-comparable; my pinned
commit from 28 September predates it.

I will repeat this check around 9 November, before writing the SOP, and
will look specifically at anything new from the SkillsInjector and
ToolMenuBench groups, since either could add the missing arm.
