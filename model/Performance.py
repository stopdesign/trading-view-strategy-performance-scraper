from dataclasses import dataclass


@dataclass
class Performance:
    netProfit: float
    totalTrades: int
    profitable: float
    profitFactor: float
    maxDrawdown: float
    avgTrade: float
    avgBarsInTrade: int

    def to_json(self) -> dict:
        return {
            "netProfit": self.netProfit,
            "totalTrades": self.totalTrades,
            "profitable": self.profitable,
            "profitFactor": self.profitFactor,
            "maxDrawdown": self.maxDrawdown,
            "avgTrade": self.avgTrade,
            "avgBarsInTrade": self.avgBarsInTrade,
        }

    @classmethod
    def empty(cls):
        return cls(0, 0, 0, 0, 0, 0, 0)
