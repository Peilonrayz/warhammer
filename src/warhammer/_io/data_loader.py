from __future__ import annotations

from typing import Type

from .. import models, unit
from . import store


class Effects:
    stores: store.StoreCollection

    def __init__(self, stores: store.StoreCollection) -> None:
        self.stores = stores

    def __getattr__(self, item: str) -> Type[models.Effect]:
        return self.stores.effects.get_effect(item)


class Weapons:
    stores: store.StoreCollection

    def __init__(self, stores: store.StoreCollection):
        self.stores = stores

    def __getattr__(self, item) -> models.WeaponAmount:
        return models.WeaponAmount.from_item(self.stores.weapons[item])


class Models:
    stores: store.StoreCollection

    def __init__(self, stores: store.StoreCollection):
        self.stores = stores

    def __getattr__(self, item) -> unit.Unit:
        return unit.Unit.from_item(self.stores.models[item])


class WarhammerData:
    stores: store.StoreCollection
    effect: Effects
    weapon: Weapons
    model: Models

    def __init__(self, source: str):
        self.stores = stores = store.stores(source)
        self.effect = Effects(stores)
        self.weapon = Weapons(stores)
        self.model = Models(stores)
