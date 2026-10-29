"""Agent traces: one record per answered question, for the admin trace page and the review queue.

No user identifier is stored, only the English wording of the question, the steps the agent took (plan, searches,
what each model reading chose, verification, citations, timings) and the reply. Purged after 30 days
(app/agent/trace.py), like technical logs.

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-29
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE traces (
        id          BIGSERIAL PRIMARY KEY,
        created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
        lang        TEXT NOT NULL,
        question    TEXT NOT NULL,                   -- English wording only
        outcome     TEXT NOT NULL,                   -- answered | partial | not found | unverified | clarify
        path        TEXT NOT NULL,                   -- lines:<op> | query_budget:<op> | search | latest | fetch
        seconds     REAL NOT NULL,
        trace       JSONB NOT NULL,
        answer      TEXT NOT NULL,
        review      TEXT NOT NULL DEFAULT 'open' CHECK (review IN ('open', 'ok', 'wrong'))
    );
    CREATE INDEX traces_created_idx ON traces (created_at DESC);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE traces;")
