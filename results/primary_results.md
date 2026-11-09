# Primary results, block 1 (114 tasks, 1 trial per cell)

## pass^1 per cell

| cell | setup | pass^1 | passed/114 |
|---|---|---|---|
| C1 | 16 real, short | 0.526 | 60 |
| C2 | 16 real, rich | 0.667 | 76 |
| C3 | +48 cross-domain, short | 0.544 | 62 |
| C4 | +48 cross-domain, rich | 0.658 | 75 |
| C10 | +48 in-domain, short | 0.570 | 65 |
| C11 | +48 in-domain, rich | 0.693 | 79 |
| C5 | +48 look-alike, short | 0.474 | 54 |
| C6 | +48 look-alike, rich | 0.570 | 65 |
| C7 | retriever top-16, short | 0.044 | 5 |
| C8 | retriever top-16, rich | 0.175 | 20 |
| C9 | +54 look-alike, short, token-matched to C2 | 0.412 | 47 |

## Contrasts (paired bootstrap over tasks, 10,000 resamples, two-sided p, Holm within family)

| family | contrast | estimate | 95% CI | p | p (Holm) |
|---|---|---|---|---|---|
| H1 | P(C3) - P(C1) | +0.018 | [-0.070, +0.105] | 0.779 | 1.000 |
| H1 | P(C10) - P(C1) | +0.044 | [-0.035, +0.132] | 0.362 | 1.000 |
| H1 | P(C5) - P(C1) | -0.053 | [-0.149, +0.044] | 0.346 | 1.000 |
| H1 | P(C10) - P(C3) | +0.026 | [-0.070, +0.123] | 0.690 | 1.000 |
| H1 | P(C5) - P(C10) | -0.096 | [-0.202, +0.018] | 0.102 | 0.508 |
| H3 | P(C9) - P(C2) | -0.254 | [-0.360, -0.149] | 0.000 | 0.000 |
| H5 | P(C7) - P(C1) | -0.482 | [-0.570, -0.395] | 0.000 | 0.000 |
| H5 | P(C7) - P(C6) | -0.526 | [-0.623, -0.430] | 0.000 | 0.000 |
| H5 | P(C8) - P(C7) | +0.132 | [+0.061, +0.211] | 0.001 | 0.001 |
| G | G(none) = P(C2) - P(C1) | +0.140 | [+0.035, +0.254] | 0.013 |  |
| G | G(cross-domain) = P(C4) - P(C3) | +0.114 | [+0.009, +0.219] | 0.033 |  |
| G | G(in-domain) = P(C11) - P(C10) | +0.123 | [+0.018, +0.228] | 0.020 |  |
| G | G(look-alike) = P(C6) - P(C5) | +0.096 | [-0.018, +0.202] | 0.095 |  |
| H2 | G(in-domain) - G(cross-domain) | +0.009 | [-0.114, +0.132] | 0.946 | 1.000 |
| H2 | G(look-alike) - G(in-domain) | -0.026 | [-0.167, +0.114] | 0.762 | 1.000 |

## Ladder trend model (cells C3, C4, C10, C11, C5, C6; rung 0, 1, 2; variant 0 = short, 1 = rich)

Mixed logistic with a task random intercept (variational fit) and, as robustness, a task-clustered GEE logistic.

| term | mixed: log-odds ± sd | GEE: log-odds (p) |
|---|---|---|
| Intercept | +0.379 ± 0.094 | +0.259 (0.157) |
| variant | +0.738 ± 0.135 | +0.513 (0.022) |
| rung | -0.209 ± 0.072 | -0.141 (0.193) |
| variant:rung | -0.062 ± 0.103 | -0.050 (0.750) |
| (conditional logit, ML, task-stratified) | | |
| variant | | +0.745 (0.015) |
| rung | | -0.206 (0.201) |
| variant:rung | | -0.072 (0.755) |

H1 predicts a negative `rung` slope; H2 a positive `variant:rung` interaction. No R installation is available, so the pre-registered mixed model is fitted two ways: the variational Bayes fit (random intercept per task) and a maximum-likelihood conditional logit that conditions on task; the GEE is the robustness fit. Reading for H1: no rung lowered success detectably against C1; the only rung pointing down is the look-alike rung (about 5 points below C1 and 10 below the in-domain rung, intervals include zero); the ordering D(cross-domain) < D(in-domain) < D(look-alike) was not supported, since the in-domain cells scored slightly above the cross-domain cells; the rung slope has the predicted sign and is significant only in the variational fit. Reading for H2: the gain from rich text does not grow with similarity.

## Robustness: all 11 cells, success ~ cell + (1 | task), C1 as reference

| cell | conditional logit: log-odds vs C1 (p) | GEE: log-odds vs C1 (p) |
|---|---|---|
| C2 | +0.857 (0.010) | +0.588 (0.015) |
| C3 | +0.102 (0.750) | +0.071 (0.705) |
| C4 | +0.799 (0.016) | +0.549 (0.015) |
| C10 | +0.257 (0.424) | +0.177 (0.316) |
| C11 | +1.037 (0.002) | +0.709 (0.002) |
| C5 | -0.304 (0.340) | -0.211 (0.302) |
| C6 | +0.257 (0.424) | +0.177 (0.445) |
| C7 | -4.142 (0.000) | -3.187 (0.000) |
| C8 | -2.326 (0.000) | -1.653 (0.000) |
| C9 | -0.664 (0.039) | -0.460 (0.014) |

## Robustness: similarity score in place of rung (mean max-cosine of the cell's fakes to the real tools under S: 0.226, 0.372, 0.683)

| term | conditional logit (p) | GEE (p) |
|---|---|---|
| variant | +0.831 (0.077) | +0.571 (0.092) |
| score | -1.044 (0.131) | -0.716 (0.130) |
| variant:score | -0.364 (0.714) | -0.250 (0.714) |

## Secondary metrics per cell

| cell | fake-call share of tool calls | conversations with a fake call | of which recovered | mean agent turn of first fake call | tool errors per conv | agent turns | agent input tokens per conv | cost per conv (tau2 tally, $) | cost per success ($) | hit error limit | truncated replies |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 | 0.000 | 0 | 0 |  | 1.04 | 13.9 | 51,297 | 0.027 | 0.051 | 0 | 0 |
| C2 | 0.000 | 0 | 0 |  | 0.54 | 13.6 | 127,334 | 0.042 | 0.063 | 0 | 0 |
| C3 | 0.000 | 0 | 0 |  | 1.11 | 13.4 | 78,431 | 0.032 | 0.058 | 1 | 0 |
| C4 | 0.000 | 0 | 0 |  | 0.55 | 13.5 | 405,708 | 0.077 | 0.117 | 0 | 0 |
| C10 | 0.002 | 2 | 1 | 12.0 | 1.07 | 13.5 | 74,538 | 0.031 | 0.054 | 0 | 0 |
| C11 | 0.007 | 5 | 3 | 12.4 | 0.64 | 14.0 | 366,436 | 0.073 | 0.106 | 0 | 0 |
| C5 | 0.058 | 31 | 25 | 9.9 | 1.51 | 14.1 | 82,727 | 0.033 | 0.069 | 0 | 0 |
| C6 | 0.060 | 33 | 27 | 10.6 | 0.95 | 14.1 | 398,261 | 0.067 | 0.118 | 0 | 0 |
| C7 | 0.574 | 97 | 48 | 4.4 | 5.35 | 12.5 | 36,697 | 0.023 | 0.521 | 40 | 0 |
| C8 | 0.173 | 79 | 51 | 5.9 | 3.81 | 18.5 | 252,665 | 0.061 | 0.347 | 20 | 0 |
| C9 | 0.091 | 47 | 40 | 10.3 | 1.55 | 14.0 | 87,140 | 0.034 | 0.083 | 0 | 0 |

## Retriever recall in C7 and C8 (analysis/retriever_recall.py, offline replay of the top-16 selection)

| cell | agent turns | mean share of the task's needed tools among the 16 shown | real tools among the 16, mean | conversations where all needed tools were shown together in at least one turn | pass rate then | pass rate otherwise |
|---|---|---|---|---|---|---|
| C7 | 1401 | 0.47 | 3.6 | 37 of 112 | 0.08 | 0.03 |
| C8 | 2092 | 0.63 | 5.2 | 50 of 112 | 0.16 | 0.16 |
