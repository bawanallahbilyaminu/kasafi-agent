"""pages.source may be 'withheld' (3 Nov 2026): a page listing people with personal data keeps a placeholder
(app/acquisition/personal.py, migration 0028). The constraint from 0001 allowed only text | ocr | none.

Revision ID: 0029
Revises: 0028
"""

from alembic import op

revision = "0029"
down_revision = "0028"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE pages DROP CONSTRAINT IF EXISTS pages_source_check")
    op.execute("ALTER TABLE pages ADD CONSTRAINT pages_source_check "
               "CHECK (source IN ('text', 'ocr', 'none', 'withheld'))")


def downgrade() -> None:
    op.execute("UPDATE pages SET source = 'none' WHERE source = 'withheld'")
    op.execute("ALTER TABLE pages DROP CONSTRAINT IF EXISTS pages_source_check")
    op.execute("ALTER TABLE pages ADD CONSTRAINT pages_source_check CHECK (source IN ('text', 'ocr', 'none'))")
