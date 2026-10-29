"""HNSW index on budget-line vectors, for meaning search with iterative scans.

0006 left the vectors unindexed: a plain HNSW scan applies the year / document filters after the fact and lost
lines. pgvector 0.8 iterative scans (set per connection in app/retrieval/line_search.py) keep scanning until
enough lines pass the filters. On the dev index: the same nearest names as the exact scan for 10 test queries
(recall 1.00 at 60 names), 0.06 s per query vector instead of 0.32 s with a year filter.

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-29
"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE INDEX IF NOT EXISTS budget_lines_embedding_hnsw ON budget_lines "
               "USING hnsw (embedding vector_cosine_ops)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS budget_lines_embedding_hnsw")
