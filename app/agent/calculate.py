"""Kasafi's calculations: figures derived from official inputs, never presented as official figures.

When the asked figure isn't published but can be derived exactly from published ones (e.g. a state's
year-on-year CPI rate = (index this September / index last September - 1) x 100), the composer
proposes a calculation: a formula over named inputs, each copied from a cited evidence excerpt.
Nothing is computed by the model. Here we
  - check every input value appears in its cited evidence (as a whole number),
  - read each input's index base period from that evidence ("Base Period: 2024 = 100") and refuse
    to mix bases (NBS rebased the CPI from 2009 = 100 to 2024 = 100 in 2025),
  - evaluate the formula with exact decimal arithmetic (a tiny parser: + - * / and brackets only),
  - and label the result "Kasafi's calculation, not an official figure", with the formula and every
    input cited.
The user is asked first ("Reply Eh to calculate"); the calculation runs when they agree.
"""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass, field
from decimal import ROUND_HALF_UP, Decimal, DivisionByZero, InvalidOperation

MAX_FORMULA = 200
MAX_INPUTS = 6
_NAME = re.compile(r"^[a-z][a-z0-9_]{0,30}$")
# "Base Period: 2024 = 100", "(BASE PERIOD 2024 = 100)", and the older NBS form "(November 2009 = 100)"
_BASE = re.compile(r"(?i)(?:base\s*(?:period|year)?\s*:?\s*\(?\s*|\(\s*(?:[a-z]+\s+)?)((?:19|20)\d\d)\s*=\s*100")
_NUM = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


class CalcError(Exception):
    pass


@dataclass
class Input:
    name: str
    value: str          # exactly as in the document
    label: str
    cited: int          # evidence number
    title: str = ""
    page: int = 0
    base: str = ""      # index base period read from the evidence, e.g. "2024=100"


@dataclass
class Calculation:
    description: str
    formula: str        # over input names, e.g. "(sep26 / sep25 - 1) * 100"
    formula_text: str   # in words, e.g. "(Sept 2026 index ÷ Sept 2025 index − 1) × 100"
    unit: str = ""
    inputs: list[Input] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Calculation:
        return cls(d["description"], d["formula"], d["formula_text"], d.get("unit", ""),
                   [Input(**i) for i in d.get("inputs", [])])


# --- arithmetic --------------------------------------------------------------------------------

def _num(s: str) -> Decimal:
    try:
        return Decimal(s.replace(",", "").strip())
    except InvalidOperation as e:
        raise CalcError(f"not a number: {s!r}") from e


def evaluate(formula: str, values: dict[str, Decimal]) -> Decimal:
    if len(formula) > MAX_FORMULA:
        raise CalcError("formula too long")
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError as e:
        raise CalcError("formula doesn't parse") from e

    def ev(node: ast.AST) -> Decimal:
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
            return Decimal(str(node.value))
        if isinstance(node, ast.Name):
            if node.id not in values:
                raise CalcError(f"unknown input {node.id}")
            return values[node.id]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            v = ev(node.operand)
            return -v if isinstance(node.op, ast.USub) else v
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
            a, b = ev(node.left), ev(node.right)
            if isinstance(node.op, ast.Add):
                return a + b
            if isinstance(node.op, ast.Sub):
                return a - b
            if isinstance(node.op, ast.Mult):
                return a * b
            try:
                return a / b
            except (DivisionByZero, InvalidOperation) as e:
                raise CalcError("division by zero") from e
        raise CalcError(f"not allowed in a formula: {type(node).__name__}")

    return ev(tree)


def compute(calc: Calculation) -> Decimal:
    result = evaluate(calc.formula, {i.name: _num(i.value) for i in calc.inputs})
    return result.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# --- checking a proposed calculation against the evidence ----------------------------------------

def _norm(s: str) -> str:
    n = s.replace(",", "").lstrip("-")
    return n.rstrip("0").rstrip(".") if "." in n else n


def base_period(text: str) -> str:
    m = _BASE.search(text)
    return f"{m.group(1)}=100" if m else ""


def validate(spec: dict | None, evidence: list) -> Calculation:
    """A safe Calculation from the composer's proposal, or CalcError (with a reason worth telling the user)."""
    if not isinstance(spec, dict) or not spec.get("formula") or not spec.get("inputs"):
        raise CalcError("no calculation")
    by_n = {e.n: e for e in evidence}
    inputs = []
    for raw in list(spec["inputs"])[:MAX_INPUTS + 1]:
        name, value = str(raw.get("name", "")), str(raw.get("value", "")).strip()
        ev = by_n.get(raw.get("cited"))
        if not _NAME.match(name) or ev is None:
            raise CalcError("input without a valid name or citation")
        if not _NUM.fullmatch(value.replace(" ", "")):
            raise CalcError(f"input {name} is not a number")
        if _norm(value) not in {_norm(m) for m in _NUM.findall(ev.text)}:
            raise CalcError(f"input {name} = {value} is not in its cited evidence")
        inputs.append(Input(name, value, str(raw.get("label", name))[:150], ev.n, ev.title, ev.page,
                            base_period(ev.text)))
    if len(inputs) > MAX_INPUTS:
        raise CalcError("too many inputs")
    bases = {i.base for i in inputs if i.base}
    if len(bases) > 1:
        raise MixedBases(sorted(bases))
    if bases and any(not i.base for i in inputs):     # one index's base is known, another's can't be read
        raise MixedBases(sorted(bases) + ["unknown"])
    calc = Calculation(str(spec.get("description", ""))[:200], str(spec["formula"]),
                       str(spec.get("formula_text") or spec["formula"])[:200], str(spec.get("unit") or "")[:5], inputs)
    names = {n.id for n in ast.walk(ast.parse(calc.formula, mode="eval")) if isinstance(n, ast.Name)} \
        if len(calc.formula) <= MAX_FORMULA else set()
    if names != {i.name for i in inputs}:
        raise CalcError("formula and inputs don't match")
    compute(calc)                                   # it must evaluate
    return calc


class MixedBases(CalcError):
    def __init__(self, bases: list[str]) -> None:
        super().__init__("mixed index base periods")
        self.bases = bases


# --- wording ---------------------------------------------------------------------------------------

LABEL = {"ha": "🧮 *Lissafin Kasafi, ba alƙalumman hukuma ba*", "en": "🧮 *Kasafi's calculation, not an official figure*"}
OFFER = {
    "ha": "🧮 Ba a wallafa {description} ba, amma zan iya lissafa shi daga alƙalumman hukuma: {formula}. "
          "Amsa *Eh* domin in lissafa.",
    "en": "🧮 {description} isn't published, but I can calculate it from the official figures: {formula}. "
          "Reply *Eh* (yes) to calculate.",
}
MIXED = {
    "ha": "Ba zan iya lissafa shi ba: alƙaluman suna kan tushe daban-daban ({bases}), don haka ba za a haɗa su ba.",
    "en": "I can't calculate it: the figures use different index base periods ({bases}), so they can't be combined.",
}
WORDS = {"ha": ("Tsari", "Bayanan da aka yi amfani da su", "shafi"), "en": ("Formula", "Inputs", "page")}


def offer_text(calc: Calculation, lang: str) -> str:
    return OFFER.get(lang, OFFER["en"]).format(description=calc.description, formula=calc.formula_text)


def _pretty(formula: str, values: dict[str, str]) -> str:
    out = re.sub(r"[a-z][a-z0-9_]*", lambda m: values.get(m.group(0), m.group(0)), formula)
    return out.replace("*", "×").replace("/", "÷").replace("-", "−")


def result_text(calc: Calculation, lang: str) -> str:
    result = compute(calc)
    formula_w, inputs_w, page_w = WORDS.get(lang, WORDS["en"])
    shown = f"{result:,.2f}{calc.unit}"
    sources = {i.cited: i for i in calc.inputs}
    lines = [LABEL.get(lang, LABEL["en"]), "", f"{calc.description}: *{shown}*", "",
             f"{formula_w}: {calc.formula_text}",
             f"= {_pretty(calc.formula, {i.name: i.value for i in calc.inputs})} = {shown}", "", f"{inputs_w}:"]
    lines += [f"• {i.label}: {i.value} [{i.cited}]" + (f" (base {i.base})" if i.base else "") for i in calc.inputs]
    lines += [""] + [f"[{n}] {i.title}, {page_w} {i.page}" for n, i in sorted(sources.items())]
    return "\n".join(lines)
