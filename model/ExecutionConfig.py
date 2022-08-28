from typing import List, Dict

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


class ExecutionConfig:
    __KEY_SYMBOL = "symbol"
    __KEY_INTERVALS = "intervals"
    __KEY_STRATEGIES = "strategies"

    def __init__(self,
                 symbols: List[Symbol],
                 intervals: List[TimeInterval],
                 strategies: List[Strategy]):
        self._intervals = intervals
        self._symbols = symbols
        self._strategies = strategies

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
    def config(self) -> List[Dict]:
        return [
            {
                self.__KEY_SYMBOL: symbol,
                self.__KEY_INTERVALS: self._intervals,
                self.__KEY_STRATEGIES: self._strategies
            } for symbol in self._symbols
        ]

    def get_symbol_from(self, config: Dict) -> str:
        return config[self.__KEY_SYMBOL]
