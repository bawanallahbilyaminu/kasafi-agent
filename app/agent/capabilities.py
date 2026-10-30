"""Capabilities and cells (docs/question-planning.md §3): what each tool can answer, matched to what a question
needs, in code.

A question's information need (app/agent/need.py) becomes cells, one per measure x entity x split x time. For
each cell, the capabilities in data/catalog.yaml that can fill it are listed best first: structured before
text, finer geographic level before coarser. A cell no capability can fill at the requested level is a coverage
gap, and the answer says what exists instead.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from app.agent.need import Entity, Need

CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "catalog.yaml"
KIND_RANK = {"structured": 0, "semi_structured": 1, "text": 2}
LEVEL_RANK = {"lga": 0, "town": 1, "state": 2, "zone": 3, "national": 4}


@dataclass(frozen=True)
class Capability:
    id: str
    kind: str
    measures: tuple[str, ...]
    entity_types: tuple[str, ...]
    geo_levels: tuple[str, ...]
    operations: tuple[str, ...]
    splits: tuple[str, ...] = ()
    needs_key: str = ""
    what: str = ""

    def can(self, cell: "Cell", operation: str) -> bool:
        return ((cell.measure in self.measures or "any" in self.measures)
                and (cell.entity.type in self.entity_types or "any" in self.entity_types)
                and (cell.level in self.geo_levels)
                and (not cell.split or cell.split == "total" or cell.split in self.splits)
                and (operation in self.operations or not self.operations))


@dataclass
class Cell:
    measure: str
    entity: Entity
    level: str = "state"
    split: str = ""                 # personnel / overhead / capital / total, for a ministry or agency
    year: int | None = None
    quarter: int | None = None
    value: object = None            # filled by a tool: a Decimal or int, with its source
    source: str = ""                # document and page, or the API and its round
    by: str = ""                    # the capability that filled it
    note: str = ""

    @property
    def filled(self) -> bool:
        return self.value is not None

    def label(self) -> str:
        parts = [self.entity.resolved or self.entity.name, self.split if self.split not in ("", "total") else "",
                 self.measure, f"{self.year}" if self.year else "", f"Q{self.quarter}" if self.quarter else ""]
        return " ".join(p for p in parts if p)


@lru_cache(maxsize=1)
def catalog(path: str = str(CATALOG_PATH)) -> tuple[Capability, ...]:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) if Path(path).exists() else {}
    t = lambda v: tuple(str(x) for x in (v or []))      # noqa: E731
    return tuple(Capability(str(c["id"]), str(c.get("kind") or "text"), t(c.get("measures")),
                            t(c.get("entity_types")), t(c.get("geo_levels")), t(c.get("operations")),
                            t(c.get("splits")), str(c.get("needs_key") or ""), str(c.get("what") or ""))
                 for c in raw.get("capabilities") or [])


def required_cells(need: Need, *, latest_year: int | None = None) -> list[Cell]:
    """Every value the question needs: measures x entities x splits x years (a quarter if one is asked)."""
    entities = need.entities or [Entity("state", "Sokoto", "Sokoto")]
    years = need.years() or [latest_year]
    splits = need.splits or [""]
    if (need.operation == "share" or (need.operation not in ("compare", "trend", "rank") and len(splits) == 1)) \
            and splits != [""] and "total" not in splits:
        splits = [*splits, "total"]          # a part is read against its whole ('how much of it is capital?')
    quarter = need.time.get("quarter")
    cells = []
    for e in entities:
        level = "lga" if e.type == "lga" else need.geo_level if e.type == "state" else "state"
        for m in need.measures or ["other"]:
            for s in splits:
                for y in years:
                    cells.append(Cell(m, e, level, s, y, quarter))
    return cells


def match(cell: Cell, operation: str, *, available: set[str] | None = None) -> list[Capability]:
    """The capabilities that can fill a cell, best first; `available` drops tools that can't run now (no key)."""
    able = [c for c in catalog() if c.can(cell, operation) and (available is None or c.id in available)]
    return sorted(able, key=lambda c: (KIND_RANK.get(c.kind, 3), min(LEVEL_RANK.get(lv, 5) for lv in c.geo_levels)))


@dataclass
class Coverage:
    cells: list[Cell]
    plan: dict[str, list[Cell]] = field(default_factory=dict)    # capability id -> the cells it should fill first
    gaps: list[Cell] = field(default_factory=list)              # cells nothing can fill at the requested level

    def best(self) -> str:
        """The capability that should fill the most cells first ('' if none)."""
        return max(self.plan, key=lambda k: len(self.plan[k])) if self.plan else ""

    def all_by(self, cap: str) -> bool:
        return bool(self.cells) and not self.gaps and set(self.plan) == {cap}


def cover(need: Need, *, available: set[str], latest_year: int | None = None) -> Coverage:
    """Cells, each assigned to its best capability; cells no capability can fill are gaps. When one capability
    can fill every cell, all go to the best such one: a need isn't split over two tools for a tie-break (the
    revised budget is in budget_core and in the analysis tools, spending to date only in budget_core)."""
    cov = Coverage(required_cells(need, latest_year=latest_year))
    per_cell = [match(cell, need.operation, available=available) for cell in cov.cells]
    if per_cell and all(per_cell):
        common = [c for c in per_cell[0] if all(any(c.id == x.id for x in caps) for caps in per_cell[1:])]
        if common:
            cov.plan[common[0].id] = list(cov.cells)
            return cov
    for cell, caps in zip(cov.cells, per_cell):
        if caps:
            cov.plan.setdefault(caps[0].id, []).append(cell)
        else:
            cov.gaps.append(cell)
    return cov


def available_capabilities(settings) -> set[str]:
    """The catalog's capabilities that can run now (a tool needing a key runs only with it)."""
    out = set()
    for c in catalog():
        key = c.needs_key.lower()
        if not key or getattr(settings, key, None):
            out.add(c.id)
    return out
