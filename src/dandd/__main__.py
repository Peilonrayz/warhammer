import fractions
from typing import Callable

import matplotlib.pyplot as plt
import mpl_toolkits.mplot3d
from dice_stats import Dice, Range, from_results
from other import main

# Rage
# Unarmored Defense
# Great Weapon Master
# Reckless Attack


# It would be cool if this could be changed to something like
# (DND(Dice.from_dice(20)) + 2).attack(ac, damage, critical_damage)
class DND:
    _attack: Dice
    _modifiers: Callable[[Dice], Dice]

    def __init__(self, attack, modifiers=lambda dice: dice):
        self._attack = attack
        self._modifiers = modifiers

    def miss(self, dice):
        return Dice.from_empty()

    def nat_attack(self, damage, critical_damage, miss, crit=20):
        return self._attack.apply_chances(
            {
                Range.from_range(f"[,1]"): miss,
                Range.from_range(f"[{crit},]"): critical_damage,
            },
            damage,
            apply=self._modifiers,
        )

    def mod_attack(self, ac, damage, miss):
        def inner(dice):
            return dice.as_chance(fractions.Fraction(1, 1)).chances(
                {Range.from_range(f"[{ac},]"): damage}, miss
            )

        return inner

    def crit_attack(self, damage):
        def inner(dice):
            return damage

        return inner

    def attack(
        self, ac, damage, critical, next_attack=None, next_critical_attack=None, crit=20
    ):
        miss = self.miss
        if next_critical_attack is not None:
            critical += next_critical_attack
        elif next_attack is not None:
            critical += next_attack
        if next_attack is not None:
            miss = lambda _: next_attack
            damage += next_attack
        return self.nat_attack(
            self.mod_attack(ac, damage, miss(None)),
            self.crit_attack(critical),
            miss,
            crit,
        )


class Weapon:
    die: int
    damage: Dice

    def __init__(self):
        self.pre_effects = []
        self.post_effects = []

    def gwf(self):
        self.pre_effects.append(lambda dice: dice.reroll([1, 2]))
        return self

    def sa(self):
        self.post_effects.append(lambda dice: Dice.max(*2 * [dice]))
        return self

    def add_damage(self, damage):
        self.post_effects.append(lambda dice: dice + damage)
        return self

    def brutal_critical(self, amount):
        self.critical_dice = amount
        return self

    @property
    def critical_dice(self):
        return getattr(self, "_critical_dice", self.die)

    @critical_dice.setter
    def critical_dice(self, value):
        self._critical_dice = self.critical_dice + value

    @property
    def attack(self):
        damage = self.damage
        for effect in self.pre_effects:
            damage = effect(damage)
        damage = self.die * damage
        for effect in self.post_effects:
            damage = effect(damage)
        return damage

    @property
    def critical(self):
        damage = self.damage
        for effect in self.pre_effects:
            damage = effect(damage)
        damage = (self.die + self.critical_dice) * damage
        for effect in self.post_effects:
            damage = effect(damage)
        return damage


class Greatsword(Weapon):
    die = 2
    damage = Dice.from_dice(6)


class Greataxe(Weapon):
    die = 1
    damage = Dice.from_dice(12)


def attack(acs, attack, attack_damage, weapon, *, crit=20, mul=2):
    dnd = DND(attack, lambda dice: dice + attack_damage)
    for ac in acs:
        damages = dnd.attack(ac, weapon.attack, weapon.critical, crit=crit,)
        yield ac, mul * damages


def attack_gwm(acs, attack, attack_damage, weapon, *, crit=20):
    dnd = DND(attack, lambda dice: dice + attack_damage)
    for ac in acs:
        base_damages = dnd.attack(ac, weapon.attack, weapon.critical, crit=crit,)
        last_attack = dnd.attack(
            ac,
            weapon.attack,
            weapon.critical,
            next_critical_attack=base_damages,
            crit=crit,
        )
        first_attack = dnd.attack(
            ac,
            weapon.attack,
            weapon.critical,
            next_attack=last_attack,
            next_critical_attack=base_damages + base_damages,
            crit=crit,
        )
        yield ac, first_attack


COLOURS = [
    "tab:blue",
    "tab:orange",
    "tab:green",
    "tab:red",
    "tab:purple",
    "tab:cyan",
    "tab:pink",
    "tab:olive",
    "tab:gray",
    "tab:brown",
]


if __name__ == "__main__":
    main()

    fig, (ax_1, ax_2) = plt.subplots(
        2, 1, figsize=(8, 8), subplot_kw={"projection": "3d"}
    )

    for name, weapon, ax in [("Axe", Greataxe, ax_1), ("Sword", Greatsword, ax_2)]:
        ACS = range(16, 21, 2)
        results = [
            attack_gwm(
                ACS,
                Dice.max(*2 * [Dice.from_dice(20)]),
                10,
                weapon().brutal_critical(3).add_damage(7 + 4),
                crit=20,
            ),
            attack_gwm(
                ACS,
                Dice.max(*2 * [Dice.from_dice(20)]),
                7,
                weapon().brutal_critical(3).gwf().add_damage(5 + 4),
                crit=19,
            ),
            attack_gwm(
                ACS,
                Dice.max(*2 * [Dice.from_dice(20)]),
                10,
                weapon().brutal_critical(3).gwf().add_damage(7 + 4),
                crit=20,
            ),
            attack_gwm(
                ACS,
                Dice.max(*2 * [Dice.from_dice(20)]),
                10,
                weapon().brutal_critical(3).add_damage(7 + 4),
                crit=20,
            ),
        ]
        labels = [
            f"Barb +2Str +UA",
            f"Barb Champion +2Str +UA",
            f"Barb +2Str +UA +GWF",
            f"Barb +2Str +UA +SA",
            f"Barb +2Str +UA +GWF +SA",
            f"Barb Champion +2Str +UA +SA",
        ]

        for result, colour in zip(from_results(results, only_positive=True), COLOURS):
            ax.plot_wireframe(*result, color=colour, alpha=0.5, cstride=0)
        ax.set_xlabel("Damage")
        ax.set_ylabel("Enemy AC")
        ax.set_zlabel("Chance")
        ax.set_title(f"Galrog {name.title()} Upgrades")
        ax.legend(labels)

    plt.show()
