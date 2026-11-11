# Amendment 2 results: the benchmark's own descriptions (114 tasks, 1 trial per cell)

Follow-up cells run 2026-11-10 after block-1 results were viewed (RESEARCH_PLAN.md, Amendment 2).

## pass^1 per cell

| cell | setup | pass^1 | passed/114 |
|---|---|---|---|
| C1 | 16 real, short (no parameter text) | 0.526 | 60 |
| C2 | 16 real, rich | 0.667 | 76 |
| C12 | 16 real, benchmark's own (dorig) | 0.667 | 76 |
| C13 | +48 look-alike, dorig | 0.632 | 72 |
| C14 | +40 look-alike, dorig, token-matched to C2 (8,227 vs 8,232) | 0.623 | 71 |
| C15 | +48 cross-domain, dorig | 0.614 | 70 |
| C5 | +48 look-alike, short | 0.474 | 54 |
| C6 | +48 look-alike, rich | 0.570 | 65 |
| C3 | +48 cross-domain, short | 0.544 | 62 |
| C4 | +48 cross-domain, rich | 0.658 | 75 |
| C9 | +54 look-alike, short (5,043 tokens, not matched) | 0.412 | 47 |

## Contrasts (paired bootstrap over tasks, 10,000 resamples, two-sided p, Holm over F1 to F5)

| contrast | definition | estimate | 95% CI | p | p (Holm) | what it measures |
|---|---|---|---|---|---|---|
| F1 | P(C12) - P(C1) | +0.140 | [+0.035, +0.246] | 0.010 | 0.050 | cost of deleting the benchmark's parameter text |
| F2 | P(C2) - P(C12) | +0.000 | [-0.096, +0.096] | 1.000 | 1.000 | gain of enrichment over the benchmark's own text |
| F3 | P(C13) - P(C12) | -0.035 | [-0.140, +0.070] | 0.584 | 1.000 | look-alike damage under the benchmark's own text |
| F4 | P(C2) - P(C14) | +0.044 | [-0.053, +0.140] | 0.424 | 1.000 | equal provider tokens: 16 rich vs 16 + 40 look-alike dorig |
| F5 | P(C15) - P(C12) | -0.053 | [-0.158, +0.053] | 0.364 | 1.000 | cross-domain damage under the benchmark's own text |

## Order ids passed without '#', failed conversations

| cell | failed | failed with a '#'-less order_id |
|---|---|---|
| C1 | 54 | 19 |
| C12 | 38 | 0 |
| C2 | 38 | 0 |
| C13 | 42 | 0 |
| C14 | 43 | 0 |
| C15 | 44 | 0 |
