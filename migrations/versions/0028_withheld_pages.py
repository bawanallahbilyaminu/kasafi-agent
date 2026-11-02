"""Pages withheld for personal data (3 Nov 2026; app/acquisition/personal.py).

A public document can carry a page listing people with their phone numbers, NIN/BVN, account numbers or salaries
(a beneficiary list, a nominal roll). The document is indexed, but such a page is withheld: its text is replaced by
a placeholder, it has no chunks, no OCR, no charts and no crop, so it never reaches search, an answer or an
evidence image. One row per withheld page, with the reason, for the import report and the admin pages.
ON DELETE CASCADE with its document.

Revision ID: 0028
Revises: 0027
"""

from alembic import op

revision = "0028"
down_revision = "0027"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS withheld_pages (
        doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page INT NOT NULL,
        reason TEXT NOT NULL DEFAULT '',
        withheld_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        PRIMARY KEY (doc_id, page)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS withheld_pages")
