from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


class RuntimeConfig:

    def __init__(self, obj_id: str, symbol: Symbol,
                 strategy: Strategy, time_interval: TimeInterval):
        self._obj_id = obj_id
        self._symbol = symbol
        self._strategy = strategy
        self._time_interval = time_interval

    @property
    def id(self) -> str:
        return self._obj_id

    @property
    def symbol(self) -> Symbol:
        return self._symbol

    @property
    def strategy(self) -> Strategy:
        return self._strategy

    @property
    def time_interval(self) -> TimeInterval:
        return self._time_interval

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            obj_id=data["id"],
            strategy=Strategy.from_mongo_server_response(data["strategy"]),
            symbol=Symbol.from_mongo_server_response(data["symbol"]),
            time_interval=TimeInterval[data["timeInterval"]]
        )
