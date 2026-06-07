import re

# Wordier or ambiguous course strings that can't be resolved by digit extraction alone
_OVERRIDES = {
    "CALC1": "20100",
    "CAL1": "20100",
    "CALC2": "20200",
    "CAL2": "20200",
    "CALC3": "20300",
    "CAL3": "20300",
    "CALCBC": "20200",
    "APCALC": "20100",
    "CALCMATH": "20100",
    "ALGEBRA": "32800",
    "LINEARALGEBRA": "32800",
    "BRIDGETOMATH212": "21200",
}


def normalize_course(raw: str) -> str:
    """
    Convert a messy course string into a canonical MATH##### code.

    Examples:
        "201"          -> "MATH20100"
        "CALC201"      -> "MATH20100"
        "MATH201 Calc" -> "MATH20100"
        "MATH20100"    -> "MATH20100"
        "ALGEBRA"      -> "MATH32800"
        "CALC1"        -> "MATH20100"
    """
    if not raw or not raw.strip():
        return "MATH_UNKNOWN"

    # Uppercase, strip spaces / dashes / underscores
    cleaned = re.sub(r"[\s\-_]", "", raw.upper())

    # Override dict handles named courses and CALC1/CALC2/CALC3 shorthands
    if cleaned in _OVERRIDES:
        return f"MATH{_OVERRIDES[cleaned]}"

    # Extract the first run of digits
    match = re.search(r"\d+", cleaned)
    if not match:
        return "MATH_UNKNOWN"

    digits = match.group()

    if len(digits) == 3:
        # 201 -> 20100, 202 -> 20200, etc.
        digits = digits + "00"
    elif len(digits) > 5:
        # 6+ digit strings are data entry noise (e.g. "195201")
        return "MATH_UNKNOWN"
    # 4-digit and 5-digit pass through unchanged

    return f"MATH{digits}"
