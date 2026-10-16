import re

from app.domain.periodic_table import ELEMENT_SYMBOLS

def extract_elements(formula: str | None) -> set[str]:
    if not formula:
        return set()

    return set(re.findall(r"[A-Z][a-z]?", formula))


def contains_element(formula: str | None, element: str) -> bool:
    return element in extract_elements(formula)


def is_valid_element_symbol(element: str | None) -> bool:
    if element is None:
        return True

    return element in ELEMENT_SYMBOLS

_STRICT_FORMULA_TOKEN = re.compile(
    r"(?P<symbol>[A-Z][a-z]?)(?:\d+(?:\.\d+)?)?"
    r"|(?P<open>\()"
    r"|(?P<close>\))(?:\d+(?:\.\d+)?)?"
)


def parse_formula_elements_strict(formula: str | None) -> frozenset[str] | None:
    """Return the element symbols of a formula, or None when it cannot be evaluated.

    Unlike ``extract_elements``, the whole string must parse: every symbol must
    be a known element, parentheses must balance, and no other characters may
    appear. ``None`` means "not evaluated"; it must never be read as "absent".
    """
    if not isinstance(formula, str):
        return None

    text = formula.strip()
    if not text:
        return None

    position = 0
    depth = 0
    previous_was_open = False
    symbols: set[str] = set()

    while position < len(text):
        match = _STRICT_FORMULA_TOKEN.match(text, position)
        if match is None or match.end() == position:
            return None

        symbol = match.group("symbol")
        if symbol is not None:
            if symbol not in ELEMENT_SYMBOLS:
                return None
            symbols.add(symbol)
            previous_was_open = False
        elif match.group("open") is not None:
            depth += 1
            previous_was_open = True
        else:
            depth -= 1
            if depth < 0 or previous_was_open:
                return None
            previous_was_open = False

        position = match.end()

    if depth != 0 or not symbols:
        return None

    return frozenset(symbols)
