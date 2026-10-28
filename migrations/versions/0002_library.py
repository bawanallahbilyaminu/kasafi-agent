"""Self-growing library: fetch provenance on documents, and the review queue of gaps.

Revision ID: 0002
Revises: 0001
Create Date: 2026-10-28
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE documents ADD COLUMN final_url TEXT, ADD COLUMN fetched_at TIMESTAMPTZ;
    -- Questions Kasafi couldn't answer, for a human to review. No user identifier is stored: only the
    -- English question, what was missing and what was tried. Purged after 90 days (app/acquisition/library.py).
    CREATE TABLE gaps (
        id           BIGSERIAL PRIMARY KEY,
        created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
        question     TEXT NOT NULL,
        missing_doc  TEXT,
        reason       TEXT NOT NULL,                  -- not_found | fetch_failed | no_answer | limit
        detail       JSONB,
        status       TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'dismissed'))
    );
    CREATE INDEX gaps_open_idx ON gaps (created_at) WHERE status = 'open';
    """)


def downgrade() -> None:
    op.execute("DROP TABLE gaps; ALTER TABLE documents DROP COLUMN final_url, DROP COLUMN fetched_at;")
