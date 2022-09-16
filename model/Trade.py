import datetime
from dataclasses import dataclass


@dataclass
class Trade:
    trade_number: int
    date: datetime
    profit_percentage: float
    drawdown_percentage: float

    @property
    def id(self) -> int:
        return self.trade_number

    def to_json(self):
        return {
            "id": self.id,
            "date": self.date.timestamp() * 1000,
            "profit_percentage": self.profit_percentage,
            "drawdown_percentage": self.drawdown_percentage,
        }
