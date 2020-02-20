from __future__ import annotations

import dataclasses

from .values import Value


@dataclasses.dataclass(frozen=True)
class Model:
    name: str
    move: Value
    weapon_skill: Value
    ballistic_skill: Value
    strength: Value
    toughness: Value
    wounds: Value
    attacks: Value
    leadership: Value
    save: Value
    invulnerable_save: Value
    feel_no_pain: Value

    def __str__(self):
        return (
            f'{self.name} '
            f'{self.move}" '
            f'{self.weapon_skill}+ '
            f'{self.ballistic_skill}+ '
            f'{self.strength} '
            f'{self.toughness} '
            f'{self.wounds} '
            f'{self.attacks} '
            f'{self.leadership} '
            f'{self.save}+ '
            f'{self.invulnerable_save}++ '
            f'{self.feel_no_pain}+++ '
        )


@dataclasses.dataclass(frozen=True)
class Weapon:
    name: str
    codex: str
    price: int
    range: Value
    type: Value
    strength: Value
    armour_penetration: Value
    damage: Value

    def __str__(self):
        return (
            f'{self.name} '
            f'{self.range}" '
            f'{self.type} '
            f'{self.strength} '
            f'{self.armour_penetration} '
            f'{self.damage} '
        )

