"""Charts on text pages, read once at index time (2 Nov 2026; app/retrieval/charts.py, chart_read.py).

One row per chart region: its page and box, the caption from the PDF's text layer, what the vision model read
(type, units, axis and legend labels, values with printed=true only for data labels), the model, the searchable text
added to the page, and a JPEG crop of the chart for evidence. ON DELETE CASCADE: a re-indexed document's charts are
read again. Public documents only; no user data.

Revision ID: 0027
Revises: 0026
"""

from alembic import op

revision = "0027"
down_revision = "0026"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS charts (
        id BIGSERIAL PRIMARY KEY,
        doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        page INT NOT NULL,
        box JSONB NOT NULL,                     -- [left, bottom, right, top] in PDF points
        region_kind TEXT NOT NULL DEFAULT '',   -- image | form | vector
        label TEXT NOT NULL DEFAULT '',         -- 'Figure 3'
        caption TEXT NOT NULL DEFAULT '',
        is_chart BOOLEAN NOT NULL DEFAULT TRUE,
        chart_type TEXT NOT NULL DEFAULT '',
        data JSONB NOT NULL DEFAULT '{}',       -- title, units, axes, legend, period, place, values[{category,series,value,printed}]
        value_source TEXT NOT NULL DEFAULT '',  -- label | estimated | mixed
        text TEXT NOT NULL DEFAULT '',          -- what was added to the page's searchable text
        crop BYTEA,
        model TEXT NOT NULL DEFAULT '',
        built_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (doc_id, page, box)
    );
    CREATE INDEX IF NOT EXISTS charts_doc_page_idx ON charts (doc_id, page);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS charts")
