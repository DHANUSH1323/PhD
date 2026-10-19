"""Description variants: build docstrings and wrap real tool methods."""
import inspect
import json
from pathlib import Path

TOOL_ATTRS = ("__tool__", "__tool_type__", "__mutates_state__")
VARIANTS = ("dmin", "dorig", "drich")
ROOT = Path(__file__).resolve().parent.parent


def make_doc(entry: dict) -> str:
    """Google-style docstring that tau2's docstring_parser reads.

    entry = {"desc": str, "params": {arg_name: description}}
    An empty or missing "params" means no parameter descriptions are sent
    (names and types still reach the agent through the signature).
    """
    lines = [entry["desc"].strip()]
    params = entry.get("params") or {}
    if params:
        # continuation lines must be indented deeper than the argument name
        lines += ["", "Args:"] + [f"    {k}: " + v.replace("\n", "\n        ") for k, v in params.items()]
    return "\n".join(lines)


def with_doc(fn, doc: str):
    """Return a callable identical to fn but with a replaced docstring."""
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    wrapper.__signature__ = inspect.signature(fn)
    wrapper.__doc__ = doc
    for attr in TOOL_ATTRS:
        if hasattr(fn, attr):
            setattr(wrapper, attr, getattr(fn, attr))
    return wrapper


def load_descriptions(variant: str) -> dict:
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant {variant}")
    path = ROOT / "descriptions" / f"{variant}.json"
    return json.loads(path.read_text())
