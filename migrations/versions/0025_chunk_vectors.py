"""Chunk vectors for the library-wide search: a 384-dimension vector (BAAI/bge-small-en-v1.5, run locally, the same
model as the budget lines' meaning search) of every chunk's text, so a question finds a relevant document it doesn't
name even when its words differ from the page's ('paid by households out of pocket' / 'born by households out of
pocket (OOP)'). No vector index: an exact scan of ~26k chunks takes milliseconds and keeps the document filters exact.

Revision ID: 0025
Revises: 0024
"""

from alembic import op

revision = "0025"
down_revision = "0024"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute("ALTER TABLE chunks ADD COLUMN IF NOT EXISTS embedding vector(384)")


def downgrade() -> None:
    op.execute("ALTER TABLE chunks DROP COLUMN IF EXISTS embedding")
