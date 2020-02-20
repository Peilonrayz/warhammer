from __future__ import annotations

import dataclasses
import itertools
import enum

from typing import Union


@dataclasses.dataclass(frozen=True)
class Constant:
    value: int

    def __str__(self):
        return f'{self.value}'

    def values(self, parent):
        return [self.value]


@dataclasses.dataclass(frozen=True)
class Relative:
    stat: str

    def __str__(self):
        return ''

    def values(self, parent):
        return getattr(parent, self.stat).values(parent)


@dataclasses.dataclass(frozen=True)
class Dice:
    amount: int
    range: int

    def __str__(self):
        return f'{self.amount if self.amount > 1 else ""}D{self.range}'

    def values(self, parent):
        return [
            sum(values)
            for values in itertools.product(
                range(1, self.range + 1),
                repeat=self.amount
            )
        ]


BasicValue = Union[Constant, Relative, Dice]


class Operators(enum.Enum):
    ADD = '+'
    SUB = '-'


@dataclasses.dataclass(frozen=True)
class Combination:
    lhs: Union[BasicValue, Combination]
    rhs: Union[BasicValue, Combination]
    operator: Operators

    def __str__(self):
        return f'{self.lhs}{self.operator.value}{self.rhs}'

    def values(self, parent):
        return [
            left + right
            for left in self.lhs.values(parent)
            for right in self.rhs.values(parent)
        ]


Value = Union[BasicValue, Combination]
