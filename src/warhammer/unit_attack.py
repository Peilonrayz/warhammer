from __future__ import annotations

import dataclasses
import fractions
import numbers
from typing import Dict, List, Optional, Tuple, Union

from . import attacks, item_amount, models

Number = numbers.Real
Unit = item_amount.ItemAmount[models.ModelWrapper]


class UnitAttack:
    unit: Unit
    _auras: List[models.Effect]
    _attacks: List
    _weapons: Dict[models.Weapon, List[models.ModelWrapper]]
    _next_attack: Optional

    def __init__(self, unit: Unit) -> None:
        self.unit = unit
        self._auras = []
        self._attacks = []
        self._weapons = weapons = {}
        self._next_attack = None
        for model in unit.iter_all():
            for weapon in model.weapons.iter_all():
                weapons.setdefault(weapon, []).append(model)

    def auras(self, *units: Unit, distance=float("inf")) -> UnitAttack:
        self._auras.extend(
            [
                effect
                for unit in units
                for model in unit.iter_unique()
                for effect in model.effects
                if isinstance(effect, models.AuraEffect) and effect.range < distance
            ]
        )
        return self

    def effects(self, *effects: models.Effect) -> UnitAttack:
        self._auras.extend(effects)
        return self

    def weapons(self, weapons: Optional[models.WeaponAmount] = None) -> UnitAttack:
        if weapons is None:
            return self
        self._next_attack = next_attack = {}
        for weapon, amount in weapons.iter_amount():
            _weapons = self._weapons.get(weapon, [])
            if len(_weapons) < amount:
                self._weapons = {}
                self._next_attack = None
                raise ValueError(f"Not enough {weapon}.")
            next_attack[weapon] = _weapons[:amount]
            del _weapons[:amount]
        return self

    def attack(self, target: Unit, distance: Number = 0) -> UnitAttack:
        if self._next_attack is None:
            weapons = self._weapons
            self._weapons = {}
        else:
            weapons = self._next_attack
            self._next_attack = None
        self._attacks.append(attack(weapons, target, self._auras, distance))
        return self

    def sanitize(self) -> Sanitized:
        return Sanitized(self)


def get_damages(
    weapons: Dict[models.Weapon, List[models.ModelWrapper]], distance: Number, damages
):
    for weapon, models_ in weapons.items():
        if weapon.range < distance:
            continue
        for model in models_:
            yield next(iter(damages[weapon, model].values()))


def attack(
    weapons: Dict[models.Weapon, List[models.ModelWrapper]],
    targets: Unit,
    auras: List[models.Effect],
    distance: Number,
):
    damages = {}
    for weapon, models_ in weapons.items():
        if weapon.range < distance:
            continue
        for model in set(models_):
            for target in targets.iter_unique():
                effects = extract_effects(model, weapon, target, auras, distance)
                damage = attacks.Attack(effects).attack(
                    models.Attack.from_models(model.model, weapon, target.model)
                )
                damages.setdefault((weapon, model), {})[target] = damage

    damages_ = get_damages(weapons, distance, damages)
    damage = next(damages_)
    for d in damages_:
        damage += d
    return damage


def extract_effects(
    model: models.ModelWrapper,
    weapon: models.Weapon,
    target: models.ModelWrapper,
    auras: List[models.Effect],
    distance: numbers.Real,
) -> Tuple[models.Effect, ...]:
    effects = [
        effect
        for type_, effects in [
            (models.EffectType.OFFENCIVE, model.effects),
            (models.EffectType.OFFENCIVE, auras),
            (models.EffectType.OFFENCIVE, weapon.effects),
            (models.EffectType.DEFENSIVE, target.effects),
        ]
        for effect in effects
        if effect.type == type_
        and (effect.attacker_range is None or effect.attacker_range >= distance)
    ]
    return tuple(sorted(effects, key=lambda i: i.name))


class Sanitized:
    def __init__(self, unit_attack: UnitAttack) -> None:
        self._unit_attack = unit_attack

    def graph(self) -> None:
        print("Graph!")
        for attack in self._unit_attack._attacks:
            print(attack)
