"""Editions of recurring reports: documents.series and documents.edition (app/acquisition/editions.py).

Back-fills documents already in the library from their ids (seed ids, and ones fetched before this
migration such as bir-2025-q3 and cpi-2025-06 on the server).

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-28
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(r"""
    ALTER TABLE documents ADD COLUMN series TEXT, ADD COLUMN edition TEXT;
    CREATE INDEX documents_series_idx ON documents (series, edition);
    UPDATE documents SET series = 'sokoto_bir', edition = substring(id from '^b[ip]r-(\d{4})-') || '-Q' ||
           substring(id from '-q([1-4])$') WHERE id ~ '^b[ip]r-\d{4}-q[1-4]$';
    UPDATE documents SET series = 'sokoto_budget', edition = substring(id from '^budget-(\d{4})-approved$')
           WHERE id ~ '^budget-\d{4}-approved$';
    UPDATE documents SET series = 'sokoto_audited_fs', edition = substring(id from '^audited-fs-(\d{4})$')
           WHERE id ~ '^audited-fs-\d{4}$';
    UPDATE documents SET series = 'nbs_cpi', edition = substring(id from '^cpi-(\d{4}-\d{2})$')
           WHERE id ~ '^cpi-\d{4}-\d{2}$';
    """)


def downgrade() -> None:
    op.execute("DROP INDEX documents_series_idx; ALTER TABLE documents DROP COLUMN series, DROP COLUMN edition;")
