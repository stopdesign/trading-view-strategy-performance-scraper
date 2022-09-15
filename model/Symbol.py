
from enum import Enum


class SymbolType(Enum):
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"
    INDEX = "INDEX"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"


class Symbol:

    def __init__(self, equity_name: str, broker_name: str, _type: SymbolType):
        self._coin_name = equity_name
        self._broker_name = broker_name
        self._type = _type

    @property
    def equity_name(self) -> str:
        return self._coin_name

    @property
    def broker_name(self) -> str:
        return self._broker_name

    @property
    def type(self) -> SymbolType:
        return self._type

    def __repr__(self):
        return f"Symbol(equity={self.equity_name}, broker={self.broker_name}, type={self.type.value})"

    def __str__(self):
        return self.__repr__()
