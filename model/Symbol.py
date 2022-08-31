

class Symbol:

    def __init__(self, equity_name: str, broker_name: str):
        self._coin_name = equity_name
        self._broker_name = broker_name

    @property
    def equity_name(self) -> str:
        return self._coin_name

    @property
    def broker_name(self) -> str:
        return self._broker_name

    def __repr__(self):
        return f"Symbol(equity={self.equity_name}, broker={self.broker_name})"

    def __str__(self):
        return self.__repr__()
