from __future__ import annotations

import functools
import numbers
import operator
from typing import Optional, Union

from . import item_amount, models, unit_attack

TModel = Union[models.Model, models.ModelWrapper]
Number = numbers.Real


class Unit(item_amount.ItemAmount[TModel]):
    def __str__(self) -> str:
        return "Unit:\n" + "\n".join(
            f"| {amount}*{item}" for item, amount in self._items.items()
        )

    def __call__(self, *args: Union[models.WeaponAmount, models.Effect]) -> Unit:
        if len(self._items) != 1:
            raise ValueError("Can only add items to units with one model in them.")
        _weapons = []
        _effects = []
        for arg in args:
            if isinstance(arg, models.WeaponAmount):
                _weapons.append(arg)
            elif isinstance(arg, models.Effect):
                _effects.append(arg)
            else:
                raise TypeError(f"Cannot process object of type {type(arg)}")

        model, amount = self._items.popitem()
        new_model = models.ModelWrapper(
            model,
            functools.reduce(operator.add, [model.weapons] + _weapons),
            model.effects + tuple(_effects),
        )
        self._items[new_model] = amount
        return self

    def _sanitize(self) -> item_amount.ItemAmount[models.ModelWrapper]:
        return item_amount.ItemAmount(
            {
                (
                    model
                    if isinstance(model, models.ModelWrapper)
                    else models.ModelWrapper(model, model.weapons, model.effects)
                ): amount
                for model, amount in self.iter_amount()
            }
        )

    def auras(self, *units: Unit, distance=float("inf")) -> unit_attack.UnitAttack:
        return unit_attack.UnitAttack(self._sanitize()).auras(*units, distance=distance)

    def effects(self, *effects: models.Effect) -> unit_attack.UnitAttack:
        return unit_attack.UnitAttack(self._sanitize()).effects(*effects)

    def weapons(
        self, weapons: Optional[models.WeaponAmount] = None
    ) -> unit_attack.UnitAttack:
        return unit_attack.UnitAttack(self._sanitize()).weapons(weapons)

    def attack(self, target: Unit) -> unit_attack.UnitAttack:
        return unit_attack.UnitAttack(self._sanitize()).attack(target)
