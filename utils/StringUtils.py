
def to_two_digits(_number: float) -> str:
    return str(round(_number, 2))


def to_short_string(_number: int) -> str:
    thousand = 1_000
    million = 1_000_000
    billion = 1_000_000_000
    trillion = 1_000_000_000_000

    rest = int(_number / trillion)
    if rest > 0:
        return to_two_digits(_number/trillion) + "T"

    rest = int(_number / billion)
    if rest > 0:
        return to_two_digits(_number/billion) + "B"

    rest = int(_number / million)
    if rest > 0:
        return to_two_digits(_number/million) + "M"

    rest = int(_number / thousand)
    if rest > 0:
        return to_two_digits(_number/thousand) + "K"

    return to_two_digits(_number)


