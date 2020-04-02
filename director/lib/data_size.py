import enum


class Units(enum.Enum):
    B = ""
    KB = "kilo"
    MB = "mega"
    GB = "giga"
    TB = "tera"
    PB = "peta"
    EB = "exa"


UNITS_LIST = list(Units)


def to_bytes(size: int, units: Units) -> int:
    return size * (1024 ** (UNITS_LIST.index(units)))


def to_human(size: int) -> str:
    assert len(UNITS_LIST)
    for i, units in enumerate(UNITS_LIST):
        h_size = size / (1024 ** i)
        if h_size < 1024:
            break

    if units == Units.B:
        float_format = ":.0f"
    else:
        float_format = ":.1f"

    format_str = "{" + float_format + "} {}"

    return format_str.format(h_size, units.name)


if __name__ == "__main__":
    print(to_bytes(2, Units.MB))
    print(to_human(1073741824))
    print(to_human(4398046511200))
    print(to_human(10))
