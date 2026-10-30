"""Domains awaiting approval: open-web results on sites outside the allowlist and the trusted patterns.

When the registry's channels and allowlisted search find nothing, Kasafi searches the open web
(docs/question-planning.md §5). A result on a trusted pattern (*.gov.ng, *.int, UN domains, the World Bank) is
fetched; one on any other site is not: its domain is queued here with the (English) question that needed it, and a
person approves or rejects it on /admin/review. Approved domains are fetchable from then on and are added to
data/source_registry.yaml by hand, so the list grows from real use. No user identifier is stored; purged after 90
days like gaps.

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-30
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE domain_reviews (
        domain      TEXT PRIMARY KEY,
        first_seen  TIMESTAMPTZ NOT NULL DEFAULT now(),
        last_seen   TIMESTAMPTZ NOT NULL DEFAULT now(),
        hits        INT NOT NULL DEFAULT 1,
        question    TEXT NOT NULL,                   -- English wording of the latest question that needed it
        url         TEXT NOT NULL,                   -- the document found there
        title       TEXT NOT NULL DEFAULT '',
        status      TEXT NOT NULL DEFAULT 'awaiting' CHECK (status IN ('awaiting', 'approved', 'rejected'))
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE domain_reviews;")
