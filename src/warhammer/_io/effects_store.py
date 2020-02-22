from __future__ import annotations

import collections
import functools
import pathlib
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ChainMap,
    Mapping,
    Optional,
    Type,
    Union,
)

if TYPE_CHECKING:
    from .. import models

    Effect = Union[Type[models.Effect], Callable[..., models.Effect]]

_PATH = pathlib.Path(__file__).parent


class EffectsStore:
    _effects: ChainMap[str, Effect]

    def __init__(self, effects: Optional[Mapping[str, Effect]] = None):
        self._effects = collections.ChainMap({} if effects is None else effects)

    def __getitem__(self, item: str) -> Effect:
        effect = self._effects[item]
        effect.__name__ = item
        return effect

    def _set_item(self, name: str, value: Effect) -> None:
        if name in self._effects:
            raise ValueError("Effect name, {name}, already taken.")
        self._effects[name] = value

    def register(self, effect: Type[Effect]) -> Type[Effect]:
        self._set_item(effect.__name__, effect)
        return effect

    def alias(self, name: str, base: str, *args: Any, **kwargs: Any) -> None:
        self._set_item(name, functools.partial(self[base], name, *args, **kwargs))

    def new_child(self) -> EffectsStore:
        return type(self)(self._effects.new_child())
