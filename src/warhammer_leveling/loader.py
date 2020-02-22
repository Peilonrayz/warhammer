from dataclasses import dataclass, fields
from enum import Enum
from typing import Dict, Generic, List, Optional, TypeVar

from dataclasses_json import dataclass_json

from .converters import Converter, Converters

T = TypeVar("T")


class Op(Enum):
    SET = ""
    ADD = "+"
    MINUS = "-"


@dataclass
class Value(Generic[T]):
    op: Op
    value: T

    @classmethod
    def from_str(cls, value: str):
        ops = {o.value: o for o in Op}
        op = ops.get(value[0], Op.SET)
        fn = getattr(cls, "__args__", [str])[0]
        return cls(op, fn(value[op is not Op.SET :]))

    def to_str(self):
        return self.op.value + self.value


@dataclass
class Bonus:
    movement: Optional[Value[int]]
    weapon_skill: Optional[Value[int]]
    ballistic_skill: Optional[Value[int]]
    strength: Optional[Value[int]]
    toughness: Optional[Value[int]]
    wounds: Optional[Value[int]]
    attacks: Optional[Value[int]]
    leadership: Optional[Value[int]]
    save: Optional[Value[int]]
    invulnerable: Optional[Value[int]]
    feel_no_pain: Optional[Value[int]]
    psychic_casts: Optional[Value[int]]
    psychic_defense: Optional[Value[int]]
    psychic_knowledge: Optional[Value[int]]

    @classmethod
    def from_str(cls, value: str):
        output = []
        for g in value.strip().split():
            if g.startswith("."):
                output += [None] * g.count(".")
            else:
                output += [Value[int].from_str(g)]
        return cls(*output)

    def to_str(self) -> str:
        output = ""
        for field in fields(self):
            value = getattr(self, field.name)
            value = "." if value is None else value.to_str()
            output += "" if output[-1] == value and value == "." else " " + value
        return output


@dataclass_json
@dataclass
class Requirements:
    rank: int
    upgrades: List[str]


@dataclass_json
@dataclass
class Equipment:
    this: List[str]
    merge: Dict[str, List[str]]


@dataclass_json
@dataclass
class Upgrade:
    name: str
    requirements: Requirements
    bonus: str
    equipment: Equipment
    abilities: List[str]
    keywords: List[str]


@dataclass_json
@dataclass(init=False)
class ExtRequirements(Converter[Requirements]):
    rank: int = Converters.property("rank")
    upgrades: List[str] = Converters.property("upgrades")


@dataclass_json
@dataclass(init=False)
class ExtEquipment(Converter[Equipment]):
    this: List[str] = Converters.property("this")
    merge: Dict[str, List[str]] = Converters.property("merge")


@dataclass_json
@dataclass(init=False)
class ExtUpgrade(Converter[Upgrade]):
    name: str = Converters.property("name")
    requirements: ExtRequirements = Converters.property("requirements")
    bonus: str = Converters.property(
        "bonus", get_fn=Bonus.to_str, set_fn=Bonus.from_str
    )
    equipment: ExtEquipment = Converters.property("equipment")
    abilities: List[str] = Converters.property("abilities")
    keywords: List[str] = Converters.property("keywords")
