"""Documents, pages and searchable chunks (full-text search; embeddings come in a later migration).

Revision ID: 0001
Revises:
Create Date: 2026-10-27
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE documents (
        id           TEXT PRIMARY KEY,               -- manifest id, e.g. budget-2025-approved
        title        TEXT NOT NULL,
        category     TEXT,
        year         INTEGER,
        publisher    TEXT,
        source_url   TEXT,
        acquisition  TEXT,                           -- download | local | fetched (self-growing library)
        sha256       TEXT NOT NULL,
        page_count   INTEGER NOT NULL,
        status       TEXT NOT NULL DEFAULT 'auto-indexed' CHECK (status IN ('auto-indexed', 'human-verified')),
        indexed_at   TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE TABLE pages (
        doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page     INTEGER NOT NULL,                   -- 1-based, as printed in citations
        text     TEXT NOT NULL,
        source   TEXT NOT NULL CHECK (source IN ('text', 'ocr', 'none')),  -- none = no text yet (needs OCR)
        PRIMARY KEY (doc_id, page)
    );
    CREATE TABLE chunks (
        id       BIGSERIAL PRIMARY KEY,
        doc_id   TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page     INTEGER NOT NULL,
        idx      INTEGER NOT NULL,                   -- position within the page
        text     TEXT NOT NULL,
        tsv      TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', text)) STORED,
        UNIQUE (doc_id, page, idx)
    );
    CREATE INDEX chunks_tsv_idx ON chunks USING GIN (tsv);
    CREATE INDEX chunks_doc_page_idx ON chunks (doc_id, page);
    CREATE INDEX pages_needs_ocr_idx ON pages (doc_id) WHERE source = 'none';
    """)


def downgrade() -> None:
    op.execute("DROP TABLE chunks; DROP TABLE pages; DROP TABLE documents;")
