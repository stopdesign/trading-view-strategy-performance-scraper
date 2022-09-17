from dataclasses import dataclass
from typing import List

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval
from enum import Enum


class OnExecutionEndStrategy(Enum):
    FINISH_EXECUTION = "Finish"
    SELECT_NEW_RANDOM_STRATEGY = "NewStrategy"


@dataclass
class ExecutionConfig:
    symbols: List[Symbol]
    intervals: List[TimeInterval]
    strategy: Strategy
    onExecutionEndedStrategy: OnExecutionEndStrategy
