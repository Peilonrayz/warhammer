from .object_loader import model
from .objects.values import Constant, Dice, Relative, Combination
from .objects.objects import Model


builder = model.Models([
    Constant,
    Dice,
    Relative,
    Combination,
    Model,
])
