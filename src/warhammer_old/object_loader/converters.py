from __future__ import annotations

import dataclasses

from typing import Tuple, Dict, Any
from typing_extensions import Protocol


class Converter(Protocol):
    def load_valid(self, value):
        ...

    def load(self, value):
        ...

    def dump(self, value):
        ...


class String:
    def load_valid(self, value):
        return isinstance(value, str)

    def load(self, value):
        return str(value)

    def dump(self, value):
        return str(value)


class Integer:
    def load_valid(self, value):
        return isinstance(value, int)

    def load(self, value):
        return int(value)

    def dump(self, value):
        return int(value)


class Union:
    def __init__(self, *converters):
        self.converters = converters

    def load_valid(self, value):
        return 1 == sum(conv.load_valid(value) for conv in self.converters)

    def load(self, value):
        for converter in self.converters:
            if converter.load_valid(value):
                return converter.load(value)

    def dump(self, value):
        pass


class Enum:
    def __init__(self, enum):
        self.enum = enum
        self._from_values = {item.value: item for item in self.enum}

    def load_valid(self, value):
        return value in self._from_values

    def load(self, value):
        return self._from_values[value]

    def dump(self, value):
        pass


@dataclasses.dataclass(frozen=True)
class ModelField:
    internal_name: str
    external_name: str
    converter: Converter


@dataclasses.dataclass
class ModelBuilder:
    model: Any
    fields: Tuple[ModelField, ...]

    def load_valid(self, value):
        return value['_model'] == self.model.__name__

    def load(self, value):
        value.pop('_model', None)
        return self.model(**{
            field.internal_name: field.converter.load(value[field.external_name])
            for field in self.fields
        })

    def dump(self, value):
        pass
