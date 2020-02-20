from __future__ import annotations

import json
import pathlib
from typing import Any, Iterator, TypeVar, Generic, Type, Dict

import marshmallow
import typing_json

from .effects_store import EffectsStore
from .. import models

_PATH = pathlib.Path(__file__).parent.parent
T = TypeVar('T')


class Store(Generic[T]):
    path: pathlib.Path
    Model: Type[T]
    _data: Dict[str, T]

    def __init__(
        self,
        name: str,
        type_: str,
        model: Type[T],
        converter: typing_json.Converter
    ) -> None:
        self.path = _PATH / 'data' / name / f'{type_}.json'
        self.Model = typing_json.dataclass_json(model, converter=converter)
        self._data = {}

    def __getitem__(self, item: str) -> T:
        return self._data[item]

    def __setitem__(self, item: str, value: T) -> None:
        self._data[item] = value

    def __delitem__(self, item: str) -> None:
        del self._data[item]

    @classmethod
    def load(cls, *args: Any, **kwargs: Any) -> Store[T]:
        store = cls(*args, **kwargs)
        with store.path.open() as f:
            for w in store.Model.schema.load(json.load(f), many=True):
                store[w.name] = w
        return store

    def save(self) -> None:
        raw_json = list(self._data.values())
        items = self.Model.schema.dump(list(raw_json), many=True)
        with self.path.open('w') as f:
            json.dump(items, f)


class EffectStore(Store[models.EffectJSON]):
    _effects_data: EffectsStore

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._effects_data = models.store.new_child()

    def get_effect(self, item: str) -> Type[models.Effect]:
        return self._effects_data[item]

    def __setitem__(self, item: str, value: models.EffectJSON) -> None:
        super().__setitem__(item, value)
        self._effects_data.alias(
            value.name,
            value.base,
            value.type,
            value.aura_range,
            value.attacker_range,
            *value.args,
            **value.kwargs,
        )

    def __delitem__(self, item: str) -> None:
        super().__delitem__(item)
        try:
            self._effects_data._effects.maps[0].pop(item)
        except KeyError:
            pass


class StoreCollection:
    converter: typing_json.Converter
    effects: EffectStore
    weapons: Store[models.Weapon]
    models: Store[models.Model]

    def __init__(self, converter, effects_store, models_store, weapons_store):
        self.converter = converter
        self.effects = effects_store
        self.models = models_store
        self.weapons = weapons_store


def stores(store_name: str) -> StoreCollection:
    class EffectField(marshmallow.fields.Field):
        def _serialize(self, value, attr, obj, **kwargs):
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            return effects_store.get_effect(value)

        @classmethod
        def from_typing(cls, _converter, _arguments, **kwargs):
            return cls(**kwargs)

    class WeaponAmountField(marshmallow.fields.Field):
        def _serialize(self, value, attr, obj, **kwargs):
            return [
                {
                    'model': model.name,
                    'amount': amount,
                }
                for model, amount in value.iter_amount()
            ]

        def _deserialize(self, value, attr, data, **kwargs):
            return models.WeaponAmount({
                weapons_store[item['model']]: item['amount']
                for item in value
            })

        @classmethod
        def from_typing(
            cls,
            _converter: typing_json.Converter,
            _arguments: Iterator[marshmallow.fields.Field],
            **kwargs: Any,
        ):
            return cls(**kwargs)

    _converter = typing_json.Converter({
        models.Effect: EffectField,
        models.WeaponAmount: WeaponAmountField,
    })
    effects_store = EffectStore.load(
        store_name,
        'effects',
        models.EffectJSON,
        _converter,
    )
    models_store = Store.load(
        store_name,
        'units',
        models.Model,
        _converter,
    )
    weapons_store = Store.load(
        store_name,
        'weapons',
        models.Weapon,
        _converter,
    )
    return StoreCollection(
        _converter,
        effects_store,
        models_store,
        weapons_store,
    )
