"""Structured budget rows: every labelled budget/performance table cell as a typed row (query_budget).

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-29
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE budget_rows (
        id              BIGSERIAL PRIMARY KEY,
        doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page            INTEGER NOT NULL,
        table_title     TEXT,
        classification  TEXT NOT NULL,   -- function | administrative | economic | programme | project | other
        spend_kind      TEXT NOT NULL,   -- total | capital | personnel | overhead | debt | revenue | other
        code            TEXT,            -- e.g. 7094 (function), 017200000000 (ministry), 23 (economic)
        name            TEXT NOT NULL,
        column_label    TEXT NOT NULL,   -- as printed, e.g. "2026 Approved Budget"
        year            INTEGER,
        measure         TEXT NOT NULL,   -- approved | revised | original | final | actual | estimate | proposal
        period          TEXT NOT NULL,   -- full_year | jan_sep | q1 | q1_q2 | q1_q3 | q1_q4 | q4 | ...
        amount_naira    NUMERIC,         -- "-" is stored as 0; thousands-tables are scaled to naira
        row_text        TEXT NOT NULL    -- the labelled row, for evidence and crops
    );
    CREATE INDEX budget_rows_lookup_idx ON budget_rows (classification, spend_kind, year, measure);
    CREATE INDEX budget_rows_code_idx ON budget_rows (code);
    CREATE INDEX budget_rows_doc_idx ON budget_rows (doc_id, page);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE budget_rows;")
