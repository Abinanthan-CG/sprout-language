from dataclasses import dataclass, field
from typing import Any, List, Optional


@dataclass
class Program:
    body: List

@dataclass
class BloomStmt:
    value: Any
    line: int = 0

@dataclass
class GrowStmt:
    name: str
    value: Any
    line: int = 0

@dataclass
class AssignStmt:
    name: str
    value: Any
    line: int = 0

@dataclass
class HarvestStmt:
    name: str
    prompt: Any
    line: int = 0

@dataclass
class WhenStmt:
    condition: Any
    then_block: List
    else_block: Optional[List]
    line: int = 0

@dataclass
class WaterStmt:
    count: Any
    body: List
    line: int = 0

@dataclass
class WhilstStmt:
    condition: Any
    body: List
    line: int = 0

@dataclass
class EachStmt:
    var_name: str
    iterable: Any
    body: List
    line: int = 0

@dataclass
class PlantStmt:
    name: str
    params: List
    body: List
    line: int = 0

@dataclass
class BearStmt:
    value: Any
    line: int = 0

@dataclass
class ExprStmt:
    expr: Any
    line: int = 0

@dataclass
class BinOp:
    left: Any
    op: str
    right: Any
    line: int = 0

@dataclass
class UnaryOp:
    op: str
    operand: Any
    line: int = 0

@dataclass
class NumberLiteral:
    value: Any
    line: int = 0

@dataclass
class StringLiteral:
    value: str
    line: int = 0

@dataclass
class BoolLiteral:
    value: bool
    line: int = 0

@dataclass
class Identifier:
    name: str
    line: int = 0

@dataclass
class FuncCall:
    name: str
    args: List
    line: int = 0

@dataclass
class IndexExpr:
    obj: Any
    index: Any
    line: int = 0

@dataclass
class ListLiteral:
    elements: List
    line: int = 0

@dataclass
class StopStmt:
    """Break out of the current loop."""
    line: int = 0

@dataclass
class SkipStmt:
    """Skip to the next iteration of the current loop."""
    line: int = 0

