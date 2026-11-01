"""Office documents converted to PDF: the original's format and hash and the converter (docs/architecture.md).

Revision ID: 0023
Revises: 0022
"""

from alembic import op

revision = "0023"
down_revision = "0022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    ALTER TABLE documents ADD COLUMN IF NOT EXISTS original_format TEXT;    -- docx | doc | odt | rtf; NULL for a PDF
    ALTER TABLE documents ADD COLUMN IF NOT EXISTS original_sha256 TEXT;    -- the Word-type original's hash
    ALTER TABLE documents ADD COLUMN IF NOT EXISTS converter TEXT;          -- e.g. 'LibreOffice 7.4.7.2'
    """)


def downgrade() -> None:
    op.execute("""
    ALTER TABLE documents DROP COLUMN IF EXISTS converter;
    ALTER TABLE documents DROP COLUMN IF EXISTS original_sha256;
    ALTER TABLE documents DROP COLUMN IF EXISTS original_format;
    """)
