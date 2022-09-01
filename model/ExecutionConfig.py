from typing import List

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


class ExecutionConfig:

    def __init__(self,
                 symbols: List[Symbol],
                 intervals: List[TimeInterval],
                 strategies: List[Strategy],
                 output_file_name: str):
        self._intervals = intervals
        self._symbols = symbols
        self._strategies = strategies
        self._output_file_name = output_file_name

    @property
    def intervals(self) -> List[TimeInterval]:
        return self._intervals

    @property
    def symbols(self) -> List[Symbol]:
        return self._symbols

    @property
    def strategies(self) -> List[Strategy]:
        return self._strategies

    @property
    def output_file_name(self) -> str:
        return self._output_file_name
