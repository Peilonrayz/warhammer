from dice_stats import Dice


def crits():
    return Dice.max(*2*[Dice.from_dice(20)])
