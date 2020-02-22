from __future__ import annotations

import fractions
import numbers
from typing import Tuple

from dice_stats import Dice as Damage

from . import item_amount, models

Number = numbers.Real
Unit = item_amount.ItemAmount[models.ModelWrapper]


def fnp_damage(damage, fnp):
    return Damage.sum(
        amount - (fnp.non_repeat * amount).as_chance(chance)
        for amount, chance in damage.items()
    )


class Attack:
    def __init__(self, effects: Tuple[models.Effect, ...]):
        self.effects = effects

    def wound_skill(self, attack: models.Attack):
        if attack.strength >= 2 * attack.toughness:
            return 2
        if attack.strength > attack.toughness:
            return 3
        if attack.strength == attack.toughness:
            return 4
        if 2 * attack.strength <= attack.toughness:
            return 6
        return 5

    def attack(self, attack: models.Attack):
        print(attack)
        print(self.effects)
        _save = min([attack.save - attack.armour_penetration, attack.invulnerable, 7,])

        damages = [
            Damage({1: fractions.Fraction(7 - attack.attack_skill, 6)}),
            Damage({1: fractions.Fraction(7 - self.wound_skill(attack), 6)}),
            Damage({1: fractions.Fraction(_save - 1, 6)}),
            fnp_damage(
                Damage({attack.damage: fractions.Fraction(1, 1)}),
                Damage({1: fractions.Fraction(7 - attack.feel_no_pain, 6)}),
            ),
        ]

        damages = iter(damages)
        result = next(damages)
        for damage in damages:
            result *= damage
        return result
