from dataclasses import dataclass
from typing import List

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


@dataclass
class ExecutionConfig:
    symbols: List[Symbol]
    intervals: List[TimeInterval]
    strategy: Strategy
