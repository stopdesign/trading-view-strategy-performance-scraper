from typing import List

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


class ExecutionConfig:

    def __init__(self,
                 symbols: List[Symbol],
                 intervals: List[TimeInterval],
                 strategy: Strategy):
        self._intervals = intervals
        self._symbols = symbols
        self._strategy = strategy

    @property
    def intervals(self) -> List[TimeInterval]:
        return self._intervals

    @property
    def symbols(self) -> List[Symbol]:
        return self._symbols

    @property
    def strategy(self) -> Strategy:
        return self._strategy
