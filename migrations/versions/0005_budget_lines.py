"""Budget lines: one row per printed table line (projects, economic items, agencies, ministries, functions),
searchable by keyword, stemmed full text and trigram similarity ("wide search, model reads, code verifies").

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-29
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS pg_trgm;
    CREATE TABLE budget_lines (
        id              TEXT PRIMARY KEY,            -- <doc_id>:<page>:<n>
        doc_id          TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page            INTEGER NOT NULL,
        table_title     TEXT,
        classification  TEXT NOT NULL,
        spend_kind      TEXT NOT NULL,
        code            TEXT,
        name            TEXT NOT NULL,
        row_text        TEXT NOT NULL,
        tsv             TSVECTOR GENERATED ALWAYS AS
                        (to_tsvector('english', coalesce(table_title, '') || ' ' || name || ' ' || row_text)) STORED
    );
    CREATE INDEX budget_lines_tsv_idx ON budget_lines USING GIN (tsv);
    CREATE INDEX budget_lines_name_trgm_idx ON budget_lines USING GIN (name gin_trgm_ops);
    CREATE INDEX budget_lines_doc_idx ON budget_lines (doc_id, page);
    ALTER TABLE budget_rows ADD COLUMN line_id TEXT REFERENCES budget_lines(id) ON DELETE CASCADE;
    CREATE INDEX budget_rows_line_idx ON budget_rows (line_id);
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE budget_rows DROP COLUMN line_id; DROP TABLE budget_lines;")
