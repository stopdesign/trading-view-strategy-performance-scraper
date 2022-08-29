import datetime


class Trade:

    def __init__(self, trade_number: int, date: datetime, profit_percentage: float, drawdown_percentage: float):
        self._trade_number = trade_number
        self._date = date
        self._profit_percentage = profit_percentage
        self._drawdown_percentage = drawdown_percentage

    @property
    def id(self) -> int:
        return self._trade_number

    @property
    def date(self) -> datetime:
        return self._date

    @property
    def profit_percentage(self) -> float:
        return self._profit_percentage

    @property
    def drawdown_percentage(self) -> float:
        return self._drawdown_percentage

    def __repr__(self):
        return "%s(%d, %s, %.2f, %.2f)" % (self.__class__.__qualname__,
                                           self.id,
                                           self.date,
                                           self.profit_percentage,
                                           self.drawdown_percentage)

    def __str__(self):
        return self.__repr__()

    def to_json(self):
        return {
            "id": self.id,
            "date": self.date.timestamp() * 1000,
            "profit_percentage": self.profit_percentage,
            "drawdown_percentage": self.drawdown_percentage,
        }
