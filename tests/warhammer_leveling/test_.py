from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List, Optional, get_type_hints

from dataclasses_json import DataClassJsonMixin, dataclass_json


@dataclass_json
@dataclass
class Repository:
    name: str
    stargazers: str


@dataclass_json
@dataclass
class Breaks:
    errors_with_trace = ""
    nodes: List[Optional[Repository]]


@dataclass_json
@dataclass
class Works:
    nodes: Optional[List[Repository]]


def show_obj(obj):
    if obj is None:
        return None

    if hasattr(obj, "nested"):
        child = obj.nested
    elif hasattr(obj, "key_container") or hasattr(obj, "value_container"):
        child = [
            show_obj(o)
            for o in (
                getattr(obj, "key_container", None),
                getattr(obj, "value_container", None),
            )
        ]
    else:
        child = show_obj(getattr(obj, "container", None))

    ret = (
        type(obj).__name__,
        # obj.allow_none,
        # obj.default,
        child,
    )
    if child is None:
        ret = ret[:-1]
    return ret


def rec(fields):
    for n, f in fields.items():
        yield n, show_obj(f)


if __name__ == "__main__":
    from pprint import pprint

    try:
        Breaks.schema()
    except AttributeError as exc:
        print(exc)

    Works.schema()

    pprint({f.name: f.type for f in fields(Breaks)})
    pprint(get_type_hints(Breaks))
    if False:
        s = A.schema()
        # pprint(s.declared_fields['c'].__dict__)
        pprint(dict(rec(s.declared_fields)))

        print(A.from_json('{"a": 4, "b": 5}'))
        print(A.from_json('{"a": 4, "b": null}'))
        print(A.schema().loads('{"a": 4, "b": 5}'))
        print(A.schema().loads('{"a": 4, "b": null}'))
