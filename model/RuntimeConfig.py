from dataclasses import dataclass

from model.Strategy import Strategy
from model.Symbol import Symbol
from model.TimeInterval import TimeInterval


@dataclass
class RuntimeConfig:
    id: str
    symbol: Symbol
    strategy: Strategy
    time_interval: TimeInterval

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            id=data["id"],
            strategy=Strategy.from_mongo_server_response(data["strategy"]),
            symbol=Symbol.from_mongo_server_response(data["symbol"]),
            time_interval=TimeInterval.from_value(data["timeInterval"])
        )
