"""Generate drich for the 16 real tools and for every fake tool.

Prompt: descriptions/drich_prompt.md = Guo et al. 2026 (arXiv 2602.20426) Appendix B.3
trace-free prompt, plus four added rules (last four bullets before the output line).
Real tools are generated one at a time from their own dorig only: the generator never
sees any fake tool. drich.params = dorig.params (parameter text is unchanged; the new
description carries the added constraints).

Usage: python scripts/generate_drich.py --model <litellm model id> --which real|lookalike|unrelated
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "descriptions" / "drich_prompt.md").read_text()
SYSTEM, USER = PROMPT.split("USER:", 1)
SYSTEM = SYSTEM.replace("SYSTEM:", "").strip()


def call_model(model: str, system: str, user: str) -> str:
    import litellm
    r = litellm.completion(model=model, temperature=0,
                           messages=[{"role": "system", "content": system},
                                     {"role": "user", "content": user}])
    return r.choices[0].message.content


def rewrite(model, name, params_schema, dorig_desc):
    user = USER.strip().format(tool_name=name, parameter_json=json.dumps(params_schema),
                               original_description=dorig_desc)
    raw = call_model(model, SYSTEM, user)
    return json.loads(raw)["description"], raw


def real_tools(model):
    from tau2.domains.retail.environment import get_environment
    dorig = json.loads((ROOT / "descriptions" / "dorig.json").read_text())
    schemas = {t.name: t.openai_schema["function"]["parameters"] for t in get_environment().get_tools()}
    out, raw = {}, {}
    for name, entry in dorig.items():
        desc, raw[name] = rewrite(model, name, schemas[name], entry["desc"])
        out[name] = {"desc": desc, "params": entry["params"]}
    (ROOT / "descriptions" / "drich.json").write_text(json.dumps(out, indent=2))
    (ROOT / "descriptions" / "drich_raw.json").write_text(json.dumps(raw, indent=2))


def fakes(model, kind):
    path = ROOT / "fake_tools" / f"{kind}.json"
    specs = json.loads(path.read_text())
    for s in specs:
        schema = {"type": "object", "properties": {p["name"]: {"type": p["type"]} for p in s["params"]},
                  "required": [p["name"] for p in s["params"] if p.get("required", True)]}
        desc, _ = rewrite(model, s["name"], schema, s["desc"]["dorig"]["desc"])
        s["desc"]["drich"] = {"desc": desc, "params": s["desc"]["dorig"]["params"]}
    path.write_text(json.dumps(specs, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--which", choices=["real", "lookalike", "unrelated"], required=True)
    a = ap.parse_args()
    real_tools(a.model) if a.which == "real" else fakes(a.model, a.which)


if __name__ == "__main__":
    main()
