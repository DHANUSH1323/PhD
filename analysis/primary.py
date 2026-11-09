"""Pre-registered analysis of the block-1 results (RESEARCH_PLAN.md, Pre-registration Section 8).

Reads results/raw/main__exp_C*/results.json and results/main_runs.csv, writes
results/primary_results.md and results/primary_contrasts.csv.
"""
import csv
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
ORDER = ["C1", "C2", "C3", "C4", "C10", "C11", "C5", "C6", "C7", "C8", "C9"]
FAKE = set()
for _k in ("lookalike", "indomain", "unrelated"):
    FAKE |= {t["name"] for t in json.load(open(Path(__file__).resolve().parent.parent / f"fake_tools/{_k}.json"))}
LABEL = {"C1": "16 real, short", "C2": "16 real, rich", "C3": "+48 cross-domain, short",
         "C4": "+48 cross-domain, rich", "C10": "+48 in-domain, short", "C11": "+48 in-domain, rich",
         "C5": "+48 look-alike, short", "C6": "+48 look-alike, rich", "C7": "retriever top-16, short",
         "C8": "retriever top-16, rich", "C9": "+54 look-alike, short, token-matched to C2"}
B = 10000
SEED = 300


def load():
    R = {}
    for c in ORDER:
        path = glob.glob(str(ROOT / f"results/raw/main__exp_{c}__*/results.json"))[0]
        sims = json.load(open(path))["simulations"]
        R[c] = {s["task_id"]: float(s["reward_info"]["reward"]) for s in sims}
    tasks = sorted(R["C1"])
    for c in ORDER:
        assert set(R[c]) == set(tasks), c
    return tasks, {c: np.array([R[c][t] for t in tasks]) for c in ORDER}


def boot(d, rng):
    idx = rng.integers(0, len(d), (B, len(d)))
    b = d[idx].mean(1)
    lo, hi = np.percentile(b, [2.5, 97.5])
    p = min(1.0, 2 * min((b <= 0).mean(), (b >= 0).mean()))
    return d.mean(), lo, hi, p


def holm(ps):
    from statsmodels.stats.multitest import multipletests
    return multipletests(ps, method="holm")[1]


def main():
    tasks, P = load()
    rng = np.random.default_rng(SEED)
    out = ["# Primary results, block 1 (114 tasks, 1 trial per cell)\n"]
    out.append("## pass^1 per cell\n\n| cell | setup | pass^1 | passed/114 |\n|---|---|---|---|")
    for c in ORDER:
        out.append(f"| {c} | {LABEL[c]} | {P[c].mean():.3f} | {int(P[c].sum())} |")

    rows = []
    fam = {"H1": [("C1", "C3"), ("C1", "C10"), ("C1", "C5"), ("C3", "C10"), ("C10", "C5")],
           "H3": [("C2", "C9")],
           "H5": [("C1", "C7"), ("C6", "C7"), ("C7", "C8")]}
    for h, pairs in fam.items():
        res = [(a, b) + boot(P[b] - P[a], rng) for a, b in pairs]
        adj = holm([r[5] for r in res])
        for (a, b, m, lo, hi, p), pa in zip(res, adj):
            rows.append(dict(family=h, contrast=f"P({b}) - P({a})", estimate=m, ci_low=lo, ci_high=hi, p=p, p_holm=pa))
    G = {}
    for rung, (a, b) in {"none": ("C1", "C2"), "cross-domain": ("C3", "C4"),
                         "in-domain": ("C10", "C11"), "look-alike": ("C5", "C6")}.items():
        G[rung] = P[b] - P[a]
        m, lo, hi, p = boot(G[rung], rng)
        rows.append(dict(family="G", contrast=f"G({rung}) = P({b}) - P({a})", estimate=m, ci_low=lo, ci_high=hi, p=p, p_holm=np.nan))
    res = [boot(G[y] - G[x], rng) for x, y in (("cross-domain", "in-domain"), ("in-domain", "look-alike"))]
    adj = holm([r[3] for r in res])
    for (x, y), (m, lo, hi, p), pa in zip((("cross-domain", "in-domain"), ("in-domain", "look-alike")), res, adj):
        rows.append(dict(family="H2", contrast=f"G({y}) - G({x})", estimate=m, ci_low=lo, ci_high=hi, p=p, p_holm=pa))

    out.append("\n## Contrasts (paired bootstrap over tasks, 10,000 resamples, two-sided p, Holm within family)\n")
    out.append("| family | contrast | estimate | 95% CI | p | p (Holm) |\n|---|---|---|---|---|---|")
    for r in rows:
        ph = "" if np.isnan(r["p_holm"]) else f"{r['p_holm']:.3f}"
        out.append(f"| {r['family']} | {r['contrast']} | {r['estimate']:+.3f} | [{r['ci_low']:+.3f}, {r['ci_high']:+.3f}] | {r['p']:.3f} | {ph} |")
    with open(ROOT / "results/primary_contrasts.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # ladder trend model: success ~ variant * rung + (1 | task) on C3, C4, C10, C11, C5, C6
    import statsmodels.api as sm
    from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
    rung = {"C3": 0, "C4": 0, "C10": 1, "C11": 1, "C5": 2, "C6": 2}
    variant = {"C3": 0, "C4": 1, "C10": 0, "C11": 1, "C5": 0, "C6": 1}
    df = pd.DataFrame([dict(task=t, success=int(P[c][i] > 0.5), rung=rung[c], variant=variant[c])
                       for c in rung for i, t in enumerate(tasks)])
    mm = BinomialBayesMixedGLM.from_formula("success ~ variant * rung", {"task": "0 + C(task)"}, df).fit_vb()
    gee = sm.GEE.from_formula("success ~ variant * rung", groups="task", data=df,
                              family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
    out.append("\n## Ladder trend model (cells C3, C4, C10, C11, C5, C6; rung 0, 1, 2; variant 0 = short, 1 = rich)\n")
    out.append("Mixed logistic with a task random intercept (variational fit) and, as robustness, a task-clustered GEE logistic.\n")
    out.append("| term | mixed: log-odds ± sd | GEE: log-odds (p) |\n|---|---|---|")
    for name, b, s in zip(mm.model.exog_names, mm.fe_mean, mm.fe_sd):
        out.append(f"| {name} | {b:+.3f} ± {s:.3f} | {gee.params[name]:+.3f} ({gee.pvalues[name]:.3f}) |")
    from statsmodels.discrete.conditional_models import ConditionalLogit
    cl = ConditionalLogit(df["success"], df[["variant", "rung"]].assign(vr=df["variant"] * df["rung"]), groups=df["task"]).fit(disp=0)
    out.append("| (conditional logit, ML, task-stratified) | | |")
    for name, key in (("variant", "variant"), ("rung", "rung"), ("variant:rung", "vr")):
        out.append(f"| {name} | | {cl.params[key]:+.3f} ({cl.pvalues[key]:.3f}) |")
    out.append("\nH1 predicts a negative `rung` slope; H2 a positive `variant:rung` interaction. "
               "No R installation is available, so the pre-registered mixed model is fitted two ways: the variational "
               "Bayes fit (random intercept per task) and a maximum-likelihood conditional logit that conditions on task; "
               "the GEE is the robustness fit. Reading for H1: no rung lowered success detectably against C1; the only "
               "rung pointing down is the look-alike rung (about 5 points below C1 and 10 below the in-domain rung, intervals "
               "include zero); the ordering D(cross-domain) < D(in-domain) < D(look-alike) was not supported, since the "
               "in-domain cells scored slightly above the cross-domain cells; the rung slope has the predicted sign and is "
               "significant only in the variational fit. Reading for H2: the gain from rich text does not grow with similarity.")

    # robustness: all 11 cells, and the similarity-score version of the ladder
    allc = pd.DataFrame([dict(task=t, success=int(P[c][i] > 0.5), cell=c) for c in ORDER for i, t in enumerate(tasks)])
    X = pd.get_dummies(allc["cell"], drop_first=False).drop(columns=["C1"]).astype(float)
    cl11 = ConditionalLogit(allc["success"], X, groups=allc["task"]).fit(disp=0)
    gee11 = sm.GEE.from_formula("success ~ C(cell, Treatment('C1'))", groups="task", data=allc, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
    out.append("\n## Robustness: all 11 cells, success ~ cell + (1 | task), C1 as reference\n")
    out.append("| cell | conditional logit: log-odds vs C1 (p) | GEE: log-odds vs C1 (p) |\n|---|---|---|")
    for c in ORDER[1:]:
        g = f"C(cell, Treatment('C1'))[T.{c}]"
        out.append(f"| {c} | {cl11.params[c]:+.3f} ({cl11.pvalues[c]:.3f}) | {gee11.params[g]:+.3f} ({gee11.pvalues[g]:.3f}) |")
    sim = {"C3": 0.226, "C4": 0.226, "C10": 0.372, "C11": 0.372, "C5": 0.683, "C6": 0.683}
    df["score"] = df.apply(lambda r: sim[{0: "C3", 1: "C10", 2: "C5"}[int(r["rung"])]], axis=1)
    cls = ConditionalLogit(df["success"], df[["variant", "score"]].assign(vs=df["variant"] * df["score"]), groups=df["task"]).fit(disp=0)
    gees = sm.GEE.from_formula("success ~ variant * score", groups="task", data=df, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
    out.append("\n## Robustness: similarity score in place of rung (mean max-cosine of the cell's fakes to the real tools under S: 0.226, 0.372, 0.683)\n")
    out.append("| term | conditional logit (p) | GEE (p) |\n|---|---|---|")
    for name, k1, k2 in (("variant", "variant", "variant"), ("score", "score", "score"), ("variant:score", "vs", "variant:score")):
        out.append(f"| {name} | {cls.params[k1]:+.3f} ({cls.pvalues[k1]:.3f}) | {gees.params[k2]:+.3f} ({gees.pvalues[k2]:.3f}) |")

    # secondary metrics from the extractor
    runs = list(csv.DictReader(open(ROOT / "results/main_runs.csv")))
    by = {c: [r for r in runs if r["cell"].replace("exp_", "") == c] for c in ORDER}
    fl = lambda x: float(x) if x not in ("", None) else 0.0
    out.append("\n## Secondary metrics per cell\n")
    first_turn = {}
    for c in ORDER:
        path = glob.glob(str(ROOT / f"results/raw/main__exp_{c}__*/results.json"))[0]
        turns = []
        for sim in json.load(open(path))["simulations"]:
            t = 0
            for m in sim["messages"]:
                if m.get("role") == "assistant":
                    t += 1
                    if any(tc["name"] in FAKE for tc in (m.get("tool_calls") or [])):
                        turns.append(t)
                        break
        first_turn[c] = (np.mean(turns) if turns else float("nan"), len(turns))
    trunc = {}
    for c in ORDER:
        p = ROOT / f"logs/{c}_T1.log"
        trunc[c] = open(p, errors="replace").read().count("Output might be incomplete due to token limit!") if p.exists() else -1
    out.append("| cell | fake-call share of tool calls | conversations with a fake call | of which recovered | mean agent turn of first fake call | tool errors per conv | agent turns | agent input tokens per conv | cost per conv (tau2 tally, $) | cost per success ($) | hit error limit | truncated replies |\n|---|---|---|---|---|---|---|---|---|---|---|---|")
    for c in ORDER:
        rs = by[c]; n = len(rs)
        fake = sum(fl(r["n_fake_calls"]) for r in rs); calls = sum(fl(r["n_tool_calls"]) for r in rs)
        wf = [r for r in rs if fl(r["n_fake_calls"]) > 0]
        rec = sum(1 for r in wf if str(r["real_tool_after_fake"]).lower() in ("true", "1"))
        cost = sum(fl(r['agent_cost']) + fl(r['user_cost']) for r in rs)
        succ = sum(1 for r in rs if fl(r['reward']) > 0.5)
        ft = first_turn[c][0]
        out.append(f"| {c} | {fake / max(calls, 1):.3f} | {len(wf)} | {rec} | {'' if np.isnan(ft) else f'{ft:.1f}'} | {sum(fl(r['n_tool_errors']) for r in rs) / n:.2f} | "
                   f"{sum(fl(r['n_agent_turns']) for r in rs) / n:.1f} | {sum(fl(r['agent_input_tokens']) for r in rs) / n:,.0f} | "
                   f"{cost / n:.3f} | {cost / succ if succ else float('nan'):.3f} | {sum(1 for r in rs if r['termination'] == 'too_many_errors')} | {trunc[c]} |")
    rr = ROOT / "results/retriever_recall.csv"
    if rr.exists():
        rows_rr = list(csv.DictReader(open(rr)))
        out.append("\n## Retriever recall in C7 and C8 (analysis/retriever_recall.py, offline replay of the top-16 selection)\n")
        out.append("| cell | agent turns | mean share of the task's needed tools among the 16 shown | real tools among the 16, mean | conversations where all needed tools were shown together in at least one turn | pass rate then | pass rate otherwise |\n|---|---|---|---|---|---|---|")
        for c in ("C7", "C8"):
            rs = [r for r in rows_rr if r["cell"] == c]
            bt = {}
            for r in rs:
                bt.setdefault(r["task_id"], []).append(r)
            full = {t: any(int(r["gold_shown"]) == int(r["n_gold"]) for r in v) for t, v in bt.items()}
            pr = lambda sel: np.mean([float(bt[t][0]["reward"]) for t in bt if full[t] == sel]) if any(full[t] == sel for t in bt) else float("nan")
            out.append(f"| {c} | {len(rs)} | {np.mean([float(r['recall']) for r in rs]):.2f} | {np.mean([float(r['real_shown']) for r in rs]):.1f} | "
                       f"{sum(full.values())} of {len(bt)} | {pr(True):.2f} | {pr(False):.2f} |")
    (ROOT / "results/primary_results.md").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
