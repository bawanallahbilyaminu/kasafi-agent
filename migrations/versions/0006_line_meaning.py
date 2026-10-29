"""Budget lines get their codes' standard descriptions and a meaning vector.

- context: the descriptions of the economic, function and administrative codes printed on a line, with their parent
  categories ("23010104 PURCHASE MOTOR CYCLES" also gets "PURCHASE OF FIXED ASSETS - GENERAL", "FIXED ASSETS
  PURCHASED"), taken from the documents' own classification tables. Lines whose printed name is a fragment are then
  found by what they are. The full-text vector now covers it.
- embedding: a 384-dimension vector (BAAI/bge-small-en-v1.5, run locally) of the line's name and context, for
  meaning search ("assistive devices" finds "Trycle bicycle for disable").

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-29
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE EXTENSION IF NOT EXISTS vector;
    ALTER TABLE budget_lines ADD COLUMN context TEXT NOT NULL DEFAULT '';
    DROP INDEX budget_lines_tsv_idx;
    ALTER TABLE budget_lines DROP COLUMN tsv;
    ALTER TABLE budget_lines ADD COLUMN tsv TSVECTOR GENERATED ALWAYS AS
        (to_tsvector('english', coalesce(table_title, '') || ' ' || name || ' ' || row_text || ' ' || context)) STORED;
    CREATE INDEX budget_lines_tsv_idx ON budget_lines USING GIN (tsv);
    -- no vector index: an exact scan of ~30k lines takes milliseconds, and an approximate index applies the year
    -- and document filters after its scan, so filtered queries lose lines
    ALTER TABLE budget_lines ADD COLUMN embedding vector(384);
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE budget_lines DROP COLUMN embedding;
    DROP INDEX budget_lines_tsv_idx;
    ALTER TABLE budget_lines DROP COLUMN tsv;
    ALTER TABLE budget_lines DROP COLUMN context;
    ALTER TABLE budget_lines ADD COLUMN tsv TSVECTOR GENERATED ALWAYS AS
        (to_tsvector('english', coalesce(table_title, '') || ' ' || name || ' ' || row_text)) STORED;
    CREATE INDEX budget_lines_tsv_idx ON budget_lines USING GIN (tsv);
    """)
