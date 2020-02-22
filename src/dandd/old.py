import fractions

import matplotlib
from dice_stats import Dice

if __name__ == "__main__":
    d = Dice.from_dice(6) + Dice.from_dice(6)
    print(d)
    d = 2 * Dice.from_dice(6)
    print(d)

    print(
        Dice.sum(
            [
                (1 * Dice.from_dice(6)).as_chance(fractions.Fraction(2, 6)),
                (2 * Dice.from_dice(6)).as_chance(fractions.Fraction(3, 6)),
                (3 * Dice.from_dice(6)).as_chance(fractions.Fraction(1, 6)),
            ]
        )
    )

    print(
        Dice.from_dice(6).chances(
            {
                (1, 2): (1 * Dice.from_dice(6)),
                (3, 4, 5): (2 * Dice.from_dice(6)),
                (6,): (3 * Dice.from_dice(6)),
            }
        )
    )

    print(Dice.from_dice(6).removes([1, 2]))

    print(Dice.from_dice(6).reroll([]))
    print(Dice.from_dice(6).reroll([1]))
    print(Dice.from_dice(6).reroll([1, 2]))
    print(Dice.from_dice(6).reroll([1, 2, 3]))
    print(Dice.from_dice(6).reroll([1, 2, 3, 4]))
    print(Dice.from_dice(6).reroll([1, 2, 3, 4, 5]))
    print(Dice.from_dice(6).reroll([1, 2, 3, 4, 5, 6]))

    print(Dice.max(*[Dice.from_dice(6)] * 2))

    print(Dice.max(*[2 * Dice.from_dice(6).reroll([1, 2])] * 2))
    print(Dice.max(*[2 * Dice.from_dice(6)] * 2))

    print(Dice.max(*[4 * Dice.from_dice(6).reroll([1, 2])] * 2))
    print(Dice.max(*[4 * Dice.from_dice(6)] * 2))
