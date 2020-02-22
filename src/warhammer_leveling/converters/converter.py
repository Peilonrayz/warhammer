from datetime import datetime
from typing import (
    Any,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

__all__ = ["ron", "Converter", "Converters"]


T = TypeVar("T")


class BuilderObject:
    def __init__(self):
        super().__setattr__("__values", {})

    def __getattr__(self, name):
        return super().__getattribute__("__values").setdefault(name, BuilderObject())

    def __setattr__(self, name, value):
        super().__getattribute__("__values")[name] = value

    def __delattr__(self, name):
        del super().__getattribute__("__values")[name]


def _build(base: Type[T], values: Union[BuilderObject, dict], exists_ok) -> T:
    """Build the object recursively, utilizes the type hints to create the correct types"""
    types = get_type_hints(base)
    if isinstance(values, BuilderObject):
        values = super(BuilderObject, values).__getattribute__("__values")
    for name, value in values.items():
        if isinstance(value, Converter):
            values[name] = value.build(exists_ok=exists_ok)
        elif isinstance(value, BuilderObject) and name in types:
            values[name] = _build(types[name], value, exists_ok)
    return base(**values)


def _get_args(obj: object, orig: Type) -> Optional[Tuple[Type]]:
    """Get args from obj, filtering by orig type"""
    bases = getattr(type(obj), "__orig_bases__", [])
    for b in bases:
        if b.__origin__ is orig:
            return b.__args__
    return None


class Converter(Generic[T]):
    _obj: T

    def __init__(self, **kwargs) -> None:
        self._obj = BuilderObject()
        for name, value in kwargs.items():
            setattr(self, name, value)

    def build(self, exists_ok: bool = False) -> T:
        """Build base object"""
        t = _get_args(self, Converter)
        if t is None:
            raise ValueError("No base")
        base_cls = t[0]
        if isinstance(self._obj, base_cls):
            if not exists_ok:
                raise TypeError("Base type has been built already.")
            return self._obj
        self._obj = _build(base_cls, self._obj, exists_ok)
        return self._obj

    @classmethod
    def from_(cls, b: T):
        """Build function from base object"""
        c = cls()
        c._obj = b
        return c


def ron(obj: T) -> T:
    """Error on null result"""
    if isinstance(obj, BuilderObject):
        raise AttributeError()
    return obj


TPath = Union[str, List[str]]


class Converters:
    @staticmethod
    def _read_path(path: TPath) -> List[str]:
        """Convert from public path formats to internal one"""
        if isinstance(path, list):
            return path
        return path.split(".")

    @staticmethod
    def _get(obj: Any, path: List[str]) -> Any:
        """Helper for nested `getattr`s"""
        for segment in path:
            obj = getattr(obj, segment)
        return obj

    @classmethod
    def property(cls, path: TPath, *, get_fn=None, set_fn=None):
        """
        Allows getting data to and from `path`.

        You can convert/type check the data using `get_fn` and `set_fn`. Both take and return one value.
        """
        p = ["_obj"] + cls._read_path(path)

        def get(self):
            value = ron(cls._get(self, p))
            if get_fn is not None:
                return get_fn(value)
            return value

        def set(self, value: Any) -> Any:
            if set_fn is not None:
                value = set_fn(value)
            setattr(cls._get(self, p[:-1]), p[-1], value)

        def delete(self: Any) -> Any:
            delattr(cls._get(self, p[:-1]), p[-1])

        return property(get, set, delete)

    @classmethod
    def to_datetime(cls, path: TPath, format: str):
        """Convert to and from the date format specified"""

        def get_fn(value: datetime) -> str:
            return value.strftime(format)

        def set_fn(value: str) -> datetime:
            return datetime.strptime(value, format)

        return cls.property(path, get_fn=get_fn, set_fn=set_fn)

    @classmethod
    def from_datetime(cls, path: TPath, format: str):
        """Convert to and from the date format specified"""

        def get_fn(value: str) -> datetime:
            return datetime.strptime(value, format)

        def set_fn(value: datetime) -> str:
            return value.strftime(format)

        return cls.property(path, get_fn=get_fn, set_fn=set_fn)
