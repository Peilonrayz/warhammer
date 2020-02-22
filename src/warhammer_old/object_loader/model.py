from __future__ import annotations

import dataclasses
import enum
import typing

from . import converters

CONVERTERS = {
    str: converters.String,
    int: converters.Integer,
    typing.Union: converters.Union,
}


def get_origin(type_):
    return getattr(type_, "__origin__", type_)


def get_args(type_):
    return getattr(type_, "__args__", ())


@dataclasses.dataclass
class ModelReference:
    models: Models
    model: str

    def load_valid(self, value):
        return self.models.models[self.model].load_valid(value)

    def load(self, value):
        return self.models.models[self.model].load(value)

    def dump(self, value):
        return self.models.models[self.model].dump(value)


class Models:
    def __init__(self, models, *, converts=CONVERTERS):
        self._converters = converts
        self.models = {}
        for model in models:
            self.add_model(model)

    def add_model(self, model) -> converters.Converter:
        model_name = model.__name__
        if model_name not in self.models:
            self.models[model_name] = ...
            resolved_types = typing.get_type_hints(model)
            fields = ()
            for field in dataclasses.fields(model):
                fields += (
                    converters.ModelField(
                        field.name, field.name, self._build(resolved_types[field.name])
                    ),
                )
            self.models[model_name] = converters.ModelBuilder(model, fields)
        elif self.models[model_name] is ...:
            return ModelReference(self, model_name)
        elif model is not self.models[model_name].model:
            raise ValueError(f"Duplicate model name {model_name}.")
        return self.models[model_name]

    def _build(self, type_) -> converters.Converter:
        if dataclasses.is_dataclass(type_):
            return self.add_model(type_)
        origin = get_origin(type_)
        if origin in self._converters:
            return self._converters[origin](*[self._build(a) for a in get_args(type_)])
        if issubclass(type_, enum.Enum):
            return converters.Enum(type_)
        raise ValueError(f"Unknown type {type_!r}({origin!r})")

    def load(self, value):
        return self.models[value["_model"]].load(value)

    def dump(self, value):
        pass
