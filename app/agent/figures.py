"""Amounts as reports print them in running text, read as values (1 Nov 2026).

A plan prints "NGN1.94 billion out of the total N29.62 billion (or 6.5 percent)"; its table prints
"29,617,906,608.4"; an answer may write "₦1.94 bn", "₦1,940,000,000" or "29,617,906,608.45". The digit check
compared the digits only and refused the answer. Here every printed form is a value with its own rounding:

- currency marks: ₦, N, NGN, naira (before or after); scale words: trillion, billion, bn, b, million, mn, m,
  thousand, k (and the Hausa biliyan, miliyan, dubu);
- a decimal comma before a scale word ("NGN29,6 billion" is 29.6 billion, a common slip in these reports);
- percentages: "6.5%", "6.5 percent", "6.5 per cent", "kashi 6.5".

Two amounts agree when they differ by no more than the coarser of their two roundings (half a unit in the last
printed place, times the scale): "₦29.62 billion" agrees with "29,617,906,608.4", and so does "29,617,906,608.45".
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

SCALES = {"trillion": Decimal(10) ** 12, "tn": Decimal(10) ** 12, "billion": Decimal(10) ** 9, "bn": Decimal(10) ** 9,
          "b": Decimal(10) ** 9, "biliyan": Decimal(10) ** 9, "million": Decimal(10) ** 6, "mn": Decimal(10) ** 6,
          "m": Decimal(10) ** 6, "miliyan": Decimal(10) ** 6, "thousand": Decimal(10) ** 3, "k": Decimal(10) ** 3,
          "dubu": Decimal(10) ** 3}

AMOUNT = re.compile(
    r"(?P<cur>₦|\bNGN|\bN(?=\s?\d)|\bnaira\b)?\s?"
    r"(?<![\d.,])(?P<num>\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:[.,]\d+)?)"
    r"(?:\s?(?P<scale>trillion|billion|biliyan|million|miliyan|thousand|dubu|tn|bn|mn|b|m|k)\b)?"
    r"(?P<pct>\s?(?:%|percent\b|per\s?cent\b))?",
    re.I)
KASHI = re.compile(r"(?i)\bkashi\s+(\d+(?:[.,]\d+)?)")


@dataclass
class Amount:
    printed: str
    value: Decimal
    tol: Decimal              # half a unit in the last printed place, times the scale
    percent: bool = False
    money: bool = False       # written with a currency mark or a scale word
    start: int = 0
    end: int = 0


BIG = ("billion", "bn", "b", "biliyan", "trillion", "tn")


def _number(num: str, scale: str) -> tuple[Decimal, Decimal] | None:
    """(value, half-unit of the last place). '29,6' before 'billion' is 29.6; '1,290' is 1290. Before 'million'
    or alone, '23,11' is ambiguous (the DSA's 'N23,11 million' sits beside 'N23,762 million': a thousands slip),
    so it is no amount at all and verifies nothing."""
    if re.fullmatch(r"\d+,\d{1,2}", num):
        if scale not in BIG:
            return None
        num = num.replace(",", ".")                       # a decimal comma: 'NGN29,6 billion'
    clean = num.replace(",", "")
    try:
        v = Decimal(clean)
    except InvalidOperation:
        return None
    places = len(clean.split(".")[1]) if "." in clean else 0
    return v, Decimal(5) * Decimal(10) ** -(places + 1)


def amounts(text: str) -> list[Amount]:
    out: list[Amount] = []
    for m in AMOUNT.finditer(text or ""):
        scale = (m.group("scale") or "").lower()
        if scale in ("b", "m", "k") and not m.group("cur"):
            scale = ""                                    # '5 m' without ₦ may be metres; '12 k' a footnote
        got = _number(m.group("num"), scale)
        if got is None:
            continue
        v, half = got
        mult = SCALES.get(scale, Decimal(1))
        out.append(Amount(m.group(0).strip(), v * mult, half * mult, bool(m.group("pct")),
                          bool(m.group("cur") or scale), m.start("num"), m.end()))
    for m in KASHI.finditer(text or ""):
        got = _number(m.group(1), "")
        if got:
            out.append(Amount(m.group(0), got[0], got[1], True, False, m.start(1), m.end()))
    return out


def agree(a: Amount, b: Amount) -> bool:
    """The same figure printed at two roundings (and both percentages, or neither)."""
    if a.percent != b.percent:
        return False
    return abs(a.value - b.value) <= max(a.tol, b.tol)


def found_in(a: Amount, pool: list[Amount]) -> bool:
    return any(agree(a, b) for b in pool)
