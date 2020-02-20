import mpl_toolkits.mplot3d
import matplotlib.pyplot as plt

from dice_stats import Dice, Range, display


def dice_up(dice, number, callback):
    return (
        dice.apply_functions(
                {Range.from_range(f'[{number},]'): callback},
                lambda d: Dice.from_empty()
            )
    )


def dice_down(dice, number, callback):
    return (
        dice.apply_functions(
                {Range.from_range(f'[,{number})'): callback},
                lambda d: Dice.from_empty()
            )
    )


def misses_standard(hit, wound, save, damage):
    return dice_up(
        Dice.from_dice(6),
        hit,
        lambda d: dice_up(
            Dice.from_dice(6),
            wound,
            lambda d: dice_down(
                Dice.from_dice(6),
                save,
                lambda d: damage,
            ),
        ),
    )


def misses_leadership(hit, wound, save, damage, wound_dice=3):
    return dice_up(
        Dice.from_dice(6),
        hit,
        lambda d: dice_up(
            wound_dice*Dice.from_dice(6),
            wound,
            lambda d: dice_down(
                Dice.from_dice(6),
                save,
                lambda d: damage,
            ),
        ),
    )


def wound(strength, toughness):
    if strength >= 2*toughness:
        return 2
    if strength > toughness:
        return 3
    if strength == toughness:
        return 4
    if 2*strength <= toughness:
        return 6
    return 5


TOUGHNESS_LIMIT = 9


def mbl_c_beam(leadership, armour, inv=7):
    for toughness in range(6, TOUGHNESS_LIMIT):
        yield (
            toughness,
            misses_leadership(
                3,
                leadership,
                min(armour + 5, inv),
                2*Dice.from_dice(6),
            )
        )


def c_beam(level, armour, inv=7):
    for toughness in range(6, TOUGHNESS_LIMIT):
        yield (
            toughness,
            2 * misses_standard(
                2,
                wound(6 + 2*level, toughness),
                min(armour + 3, inv),
                (1 + level)*Dice.from_dice(3),
            )
        )


def plot_cbeam(save):
    results = [
        c_beam(0, save),
        c_beam(1, save),
        c_beam(2, save),
        c_beam(3, save),
        mbl_c_beam(6, save),
        mbl_c_beam(8, save),
        mbl_c_beam(10, save),
    ]
    labels = [
        f'Base',
        f'24"',
        f'48"',
        f'72"',
        f'MBL ld 6',
        f'MBL ld 8',
        f'MBL ld 10',
    ]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': '3d'})
    for result, colour in zip(display.plot_wireframes(results), display.COLOURS):
        ax.plot_wireframe(*result, color=colour, alpha=0.5, cstride=0)

    ax.set_xlabel('Damage')
    ax.set_ylabel('Enemy Toughness')
    ax.set_zlabel('Chance')
    ax.set_title(f'C-beam Cannon on HCD against {save}+')
    ax.legend(labels)

    plt.show()

def mbl(armour, inv=7):
    for leadership in range(1, 12, 2):
        yield (
            leadership,
            misses_leadership(
                3,
                leadership,
                min(armour + 5, inv),
                2*Dice.from_dice(6),
            )
        )


def plot_mbl(save):
    results = [
        mbl(save),
    ]
    labels = [
        f'Base',
    ]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': '3d'})
    for result, colour in zip(display.plot_wireframes(results), display.COLOURS):
        ax.plot_wireframe(*result, color=colour, alpha=0.5, cstride=0)

    ax.set_xlabel('Damage')
    ax.set_ylabel('Enemy Leadership')
    ax.set_zlabel('Chance')
    ax.set_title(f'Malignatas Beam Laser on HSV against {save}+')
    ax.legend(labels)

    plt.show()


def main():
    plot_cbeam(3)
    # plot_mbl(3)


if __name__ == '__main__':
    main()
