from __future__ import annotations

import numbers
import operator
from typing import Generic, Iterator, Tuple, TypeVar, Union, Dict, Callable

T = TypeVar('T')
Number = numbers.Real


class ItemAmount(Generic[T]):
    _items: Dict[T, Number]

    def __init__(self, items: Dict[T, Number] = None):
        self._items = {} if items is None else items

    @classmethod
    def from_item(cls, item: T, amount: Number = 1) -> ItemAmount[T]:
        return cls({item: amount})

    def __copy__(self) -> ItemAmount[T]:
        return type(self)(self._items.copy())

    def copy(self) -> ItemAmount[T]:
        return self.__copy__()

    def iter_all(self) -> Iterator[T]:
        for item, amount in self._items.items():
            yield from [item] * amount

    def iter_amount(self) -> Iterator[Tuple[T, int]]:
        for item, amount in self._items.items():
            yield item, amount

    def iter_unique(self) -> Iterator[T]:
        yield from self._items.keys()

    def __add__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.add)

    def __radd__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.add)

    def __sub__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.sub)

    def __rsub__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.sub)

    def __mul__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.mul)

    def __rmul__(self, other: Union[Number, ItemAmount[T]]) -> ItemAmount[T]:
        return _item_amount_operator(self, other, operator.mul)


def _item_amount_operator(
    self: ItemAmount[T],
    other: ItemAmount[T],
    op: Callable[[Number, Number], Number],
) -> ItemAmount[T]:
    if isinstance(other, ItemAmount):
        items = other._items
    elif isinstance(other, numbers.Real):
        if other % 1:
            raise ValueError('Numbers can only be real.')
        items = dict.fromkeys(self._items, other)
    else:
        raise TypeError(
            f'Must perform operations with ItemAmount or real numbers, '
            f'not {type(other)}.'
        )

    item = self.copy()
    _items = item._items
    for item_, amount in items.items():
        _items[item_] = op(_items.get(item_, 0), amount)
        if _items[item_] <= 0:
            _items.pop(item_)
    return item
