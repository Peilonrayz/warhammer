from __future__ import annotations, annotations

import dataclasses
import enum
from typing import Any, Dict, Tuple, Optional

from . import item_amount
from ._io.effects_store import EffectsStore

store = EffectsStore()


class EffectType(enum.Enum):
    OFFENCIVE = 'Offencive'
    DEFENSIVE = 'Defensive'


@store.register
@dataclasses.dataclass(frozen=True)
class Effect:
    name: str
    type: EffectType = None
    aura_range: Optional[int] = None
    attacker_range: Optional[int] = None


@dataclasses.dataclass
class EffectJSON:
    name: str
    base: str
    type: Optional[EffectType] = None
    aura_range: Optional[int] = None
    attacker_range: Optional[int] = None
    args: Tuple[Any, ...] = dataclasses.field(default_factory=tuple)
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)


class WeaponType(enum.Enum):
    MELEE = 'Melee'


@dataclasses.dataclass(frozen=True)
class Weapon:
    name: str
    range: int
    type: WeaponType
    attacks: int
    strength: int
    armour_penetration: int
    damage: int
    effects: Tuple[Effect, ...]


class WeaponAmount(item_amount.ItemAmount[Weapon]):
    def __repr__(self):
        return ' + '.join(
            f'{amount}*{weapon.name}'
            for weapon, amount in self._items.items()
        )


@dataclasses.dataclass(frozen=True)
class Model:
    name: str
    power: int
    movement: int
    weapon_skill: int
    ballistic_skill: int
    strength: int
    toughness: int
    wounds: int
    attacks: int
    leadership: int
    save: int
    invulnerable: int
    feel_no_pain: int
    weapons: WeaponAmount
    effects: Tuple[Effect, ...]


@dataclasses.dataclass(frozen=True)
class ModelWrapper:
    model: Model
    weapons: WeaponAmount
    effects: Tuple[Effect, ...]


@dataclasses.dataclass
class Attack:
    attack_skill: int
    attacks: int
    armour_penetration: int
    damage: int
    strength: int
    toughness: int
    wounds: int
    save: int
    invulnerable: int
    feel_no_pain: int

    @classmethod
    def from_models(
        cls,
        model: Model,
        weapon: Weapon,
        target: Model,
    ):
        return cls(
            (
                model.weapon_skill
                if weapon.type is WeaponType.MELEE else
                model.ballistic_skill
            ),
            weapon.attacks,
            weapon.armour_penetration,
            weapon.damage,
            weapon.strength,
            target.toughness,
            target.wounds,
            target.save,
            target.invulnerable,
            target.feel_no_pain,
        )
