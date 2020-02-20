import fractions
from typing import Callable

import mpl_toolkits.mplot3d
import matplotlib.pyplot as plt

from dice_stats import Dice, Range, from_results


def sa_reroll(rerolls, damage: Dice):
    for reroll in rerolls:
        new_damage = damage.apply_chances(
            {
                Range.from_range(f'[,{reroll}]'): lambda _: damage,
            },
            lambda dice: dice,
        )
        yield reroll, new_damage


COLOURS = [
    'tab:blue',
    'tab:orange',
]


def main():
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': '3d'})
    NUMBERS = range(0, 13)
    results = [
        sa_reroll(
            NUMBERS,
            Dice.from_dice(12)
        ),
        sa_reroll(
            NUMBERS,
            2*Dice.from_dice(6)
        ),
    ][1:]
    for result, colour in zip(from_results(results, only_positive=True), COLOURS):
        ax.plot_wireframe(*result, color=colour, alpha=0.5, cstride=0)
    ax.set_xlabel('Damage')
    ax.set_ylabel('Reroll from')
    ax.set_zlabel('Chance')
    ax.set_title(f'SA damage')

    plt.show()
