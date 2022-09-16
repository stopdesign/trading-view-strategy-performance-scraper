from dataclasses import dataclass
from enum import Enum


class SymbolType(Enum):
    FOREX = "FOREX"
    COMMODITY = "COMMODITY"
    INDEX = "INDEX"
    STOCK = "STOCK"
    CRYPTO = "CRYPTO"


@dataclass
class Symbol:
    equity_name: str
    broker_name: str
    type: SymbolType

    @classmethod
    def from_mongo_server_response(cls, data: dict):
        return cls(
            equity_name=data["name"],
            broker_name=data["broker"],
            type=SymbolType[data["type"]]
        )

    def to_json(self) -> dict:
        return {
            "name": self.equity_name,
            "broker": self.broker_name,
            "type": self.type.value
        }
