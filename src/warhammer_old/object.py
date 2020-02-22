from .object_loader import model
from .objects.objects import Model
from .objects.values import Combination, Constant, Dice, Relative

builder = model.Models([Constant, Dice, Relative, Combination, Model,])
