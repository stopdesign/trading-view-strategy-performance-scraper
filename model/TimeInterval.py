from enum import Enum


class TimeInterval(Enum):
    M1 = "1"
    M3 = "3"
    M5 = "5"
    M15 = "15"
    M30 = "30"
    M45 = "45"
    H1 = "60"
    H2 = "120"
    H3 = "180"
    H4 = "240"
    D = "1D"
    W = "1W"
