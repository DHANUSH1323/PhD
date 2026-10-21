"""Generate drich for the 16 real tools and for every fake tool.

Prompt: descriptions/drich_prompt.md = Guo et al. 2026 (arXiv 2602.20426) Appendix B.3
trace-free prompt, plus four added rules (last four bullets before the output line).
Real tools are generated one at a time from their own dorig only: the generator never
sees any fake tool. drich.params = dorig.params (parameter text is unchanged; the new
description carries the added constraints).

Usage: python scripts/generate_drich.py --model <litellm model id> --which real|lookalike|indomain|unrelated [--force]
Fakes that already have drich are skipped unless --force, so a re-selected unrelated.json
only generates the new entries. The file is saved after every tool.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPT = (ROOT / "descriptions" / "drich_prompt.md").read_text()
SYSTEM, USER = PROMPT.split("USER:", 1)
SYSTEM = SYSTEM.replace("SYSTEM:", "").strip()


JSON_TYPES = {"str": "string", "int": "integer", "float": "number", "bool": "boolean",
              "list[str]": "array", "dict": "object"}


def call_model(model: str, system: str, user: str) -> str:
    import litellm
    r = litellm.completion(model=model, temperature=0,
                           messages=[{"role": "system", "content": system},
                                     {"role": "user", "content": user}])
    return r.choices[0].message.content


def parse_json(raw: str) -> dict:
    """Tolerate a ```json fence around the output; otherwise require plain JSON."""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


def rewrite(model, name, params_schema, dorig_desc):
    user = USER.strip().format(tool_name=name, parameter_json=json.dumps(params_schema),
                               original_description=dorig_desc)
    raw = call_model(model, SYSTEM, user)
    desc = parse_json(raw)["description"]
    assert isinstance(desc, str) and desc.strip(), f"{name}: empty description"
    return desc, raw


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


def fakes(model, kind, force=False):
    """Fills drich for every fake that lacks it (all of them with --force). Saves after each tool."""
    path = ROOT / "fake_tools" / f"{kind}.json"
    specs = json.loads(path.read_text())
    for s in specs:
        if "drich" in s["desc"] and not force:
            continue
        # same JSON-schema vocabulary the real tools are sent with (string, array, ...)
        props = {p["name"]: {"type": JSON_TYPES[p["type"]]} for p in s["params"]}
        for p in s["params"]:
            if p["type"] == "list[str]":
                props[p["name"]]["items"] = {"type": "string"}
        schema = {"type": "object", "properties": props,
                  "required": [p["name"] for p in s["params"] if p.get("required", True)]}
        desc, _ = rewrite(model, s["name"], schema, s["desc"]["dorig"]["desc"])
        s["desc"]["drich"] = {"desc": desc, "params": s["desc"]["dorig"]["params"]}
        path.write_text(json.dumps(specs, indent=2) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--which", choices=["real", "lookalike", "indomain", "unrelated"], required=True)
    ap.add_argument("--force", action="store_true", help="regenerate fakes that already have drich")
    a = ap.parse_args()
    real_tools(a.model) if a.which == "real" else fakes(a.model, a.which, a.force)


if __name__ == "__main__":
    main()
