"""Structured budget core: one row per budget line, per capital project and per implementation-report line.

budget_lines/budget_rows hold every printed cell (one row per cell). The analysis tools (project status, an LGA's
projects, rankings, an MDA's or function's profile, revenue) need the same facts as entities, with one column per
year and measure as printed, so that every count and sum is one SQL query:

  budget_items  one row per printed budget line (2024-2026 budgets): its classification, spending kind, code, name,
                the administrative unit (MDA) it belongs to, and the printed amounts.
  projects      one row per capital project in a budget's statewide project list: name, MDA, economic, function and
                location codes and names, the printed amounts and page. Parsed from the page text by its code anchors
                (the labelled rows split wrapped project names).
  perf_items    one row per line of a budget implementation / performance report: original, revised and final
                budget, the quarter's spending and the year-to-date spending.
  entity_builds the build report per document: counts and the reconciliation checks that passed and failed.

Built by app/retrieval/entities.py when a document is indexed (and at startup for documents indexed before this).

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-30
"""

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None

_AMOUNTS = """
        actual_2022     NUMERIC,
        actual_2023     NUMERIC,
        actual_2024     NUMERIC,
        jan_sep_2023    NUMERIC,
        jan_sep_2024    NUMERIC,
        jan_sep_2025    NUMERIC,
        revised_2023    NUMERIC,
        revised_2024    NUMERIC,
        revised_2025    NUMERIC,
        original_2025   NUMERIC,
        approved_2024   NUMERIC,
        approved_2025   NUMERIC,
        approved_2026   NUMERIC,
        proposal_2024   NUMERIC,
        estimate_2026   NUMERIC,
        estimate_2027   NUMERIC,
        estimate_2028   NUMERIC,
        other           JSONB NOT NULL DEFAULT '{}'      -- any other printed column, by its label
"""


def upgrade() -> None:
    op.execute(f"""
    CREATE TABLE budget_items (
        id              TEXT PRIMARY KEY REFERENCES budget_lines(id) ON DELETE CASCADE,
        doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page            INT NOT NULL,
        seq             INT NOT NULL,                    -- reading order within the document
        table_title     TEXT NOT NULL,
        classification  TEXT NOT NULL,
        spend_kind      TEXT NOT NULL,
        code            TEXT,
        name            TEXT NOT NULL,
        mda_code        TEXT,                            -- 12-digit administrative code it belongs to
        mda_name        TEXT,
        {_AMOUNTS}
    );
    CREATE INDEX budget_items_lookup_idx ON budget_items (doc_id, classification, spend_kind, code);
    CREATE INDEX budget_items_mda_idx ON budget_items (doc_id, mda_code);

    CREATE TABLE projects (
        id              TEXT PRIMARY KEY,                -- document id, page and position on the page
        doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page            INT NOT NULL,
        seq             INT NOT NULL,
        name            TEXT NOT NULL,
        mda_code        TEXT NOT NULL,
        mda_name        TEXT NOT NULL,
        econ_code       TEXT NOT NULL,
        econ_name       TEXT NOT NULL,
        function_code   TEXT,
        function_name   TEXT,
        location_code   TEXT NOT NULL,
        location_name   TEXT NOT NULL,
        {_AMOUNTS}
    );
    CREATE INDEX projects_doc_idx ON projects (doc_id, mda_code);
    CREATE INDEX projects_location_idx ON projects (doc_id, location_code);
    CREATE INDEX projects_name_trgm_idx ON projects USING GIN (name gin_trgm_ops);

    CREATE TABLE perf_items (
        id              TEXT PRIMARY KEY REFERENCES budget_lines(id) ON DELETE CASCADE,
        doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page            INT NOT NULL,
        seq             INT NOT NULL,
        year            INT NOT NULL,
        quarter         INT NOT NULL,                    -- the report's last quarter (year to date = Q1..quarter)
        table_title     TEXT NOT NULL,
        classification  TEXT NOT NULL,
        spend_kind      TEXT NOT NULL,
        code            TEXT,
        name            TEXT NOT NULL,
        mda_code        TEXT,
        mda_name        TEXT,
        original        NUMERIC,
        revised         NUMERIC,
        final           NUMERIC,
        quarter_spent   NUMERIC,
        ytd_spent       NUMERIC
    );
    CREATE INDEX perf_items_lookup_idx ON perf_items (doc_id, classification, spend_kind, code);

    CREATE TABLE entity_builds (
        doc_id          TEXT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
        built_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
        counts          JSONB NOT NULL,
        checks          JSONB NOT NULL                   -- per check: passed, failed, examples
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE entity_builds; DROP TABLE perf_items; DROP TABLE projects; DROP TABLE budget_items;")
