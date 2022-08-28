

class Symbol:

    def __init__(self, coin_name: str, broker_name: str):
        self._coin_name = coin_name
        self._broker_name = broker_name

    @property
    def coin_name(self) -> str:
        return self._coin_name

    @property
    def broker_name(self) -> str:
        return self._broker_name

    def to_json(self) -> dict:
        return {
            "symbol": self.coin_name,
            "broker": self.broker_name
        }

    def __repr__(self):
        return f"Symbol(coin={self.coin_name}, broker={self.broker_name})"

    def __str__(self):
        return self.__repr__()
