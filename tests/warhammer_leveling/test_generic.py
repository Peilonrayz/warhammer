from typing import Generic, Type, TypeVar

T = TypeVar("T")


class Obj(Generic[T]):
    value: T

    def __init__(self, value: T):
        self.value = value

    def __str__(self):
        name = getattr(self, "__orig_class__", type(self).__name__)
        return f"{name}(value={self.value!r})"

    @classmethod
    def from_str(cls, value: str):
        fn = getattr(cls, "__args__", [str])[0]
        return cls(fn(value))


def from_str(cls: Type[Obj[T]], value) -> Obj[T]:
    fn = getattr(cls, "__args__", [str])[0]
    return cls(fn(value))


if __name__ == "__main__":
    # untyped
    print(Obj.from_str("1"))
    print(from_str(Obj, "1"))

    # typed
    print(Obj[int].from_str("1"))
    print(from_str(Obj[int], "1"))
