"""Fake tools: callable stubs that always raise a scope-consistent error."""
import inspect
import json
from pathlib import Path

from tau2.environment.toolkit import ToolType

from harness.variants import ROOT, make_doc

TYPE_MAP = {"str": str, "int": int, "float": float, "bool": bool,
            "list[str]": list[str], "dict": dict}


class _SafeDict(dict):
    def __missing__(self, key):
        return "the requested record"


def build_fake(spec: dict, variant: str):
    """spec keys: name, params [{name, type, required}], error, desc{variant: entry}."""
    params = []
    for p in spec["params"]:
        default = inspect.Parameter.empty if p.get("required", True) else None
        params.append(inspect.Parameter(
            p["name"], inspect.Parameter.KEYWORD_ONLY,
            default=default, annotation=TYPE_MAP[p["type"]]))
    error_template = spec["error"]

    def fake(**kwargs):
        raise ValueError(error_template.format_map(_SafeDict(kwargs)))

    fake.__name__ = spec["name"]
    fake.__signature__ = inspect.Signature(params)
    fake.__doc__ = make_doc(spec["desc"][variant])
    fake.__tool__ = True
    fake.__tool_type__ = ToolType.READ
    fake.__mutates_state__ = False
    return fake


def load_fakes(kind: str) -> list[dict]:
    """kind is 'lookalike' or 'unrelated'."""
    path = ROOT / "fake_tools" / f"{kind}.json"
    return json.loads(path.read_text())
