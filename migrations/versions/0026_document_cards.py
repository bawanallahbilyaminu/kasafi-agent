"""Document cards, section cards and related documents (2 Nov 2026).

- doc_cards: one per document, written by Muse Spark Open from the whole document (section by section, then merged):
  a 3-4 sentence summary, the kind of document, topics with their pages, the geography covered (state, LGAs,
  wards), the period covered, the key measures; with a vector of the card for the library search.
- section_cards: one per section (a chapter, a section under a heading, or a table with its title): a 1-2 sentence
  summary, topics, geography, period, measures and the page range, with a vector, so a question can go straight
  to the matching section and read its pages.
- doc_links: documents covering the same topic, place and period, both directions, with the shared topics as
  the reason.
Cards belong to their document (ON DELETE CASCADE): re-indexing a document deletes its cards, which are built
again. No user data.

Revision ID: 0026
Revises: 0025
"""

from alembic import op

revision = "0026"
down_revision = "0025"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE IF NOT EXISTS doc_cards (
        doc_id TEXT PRIMARY KEY REFERENCES documents(id) ON DELETE CASCADE,
        summary TEXT NOT NULL,
        kind TEXT NOT NULL DEFAULT '',
        topics JSONB NOT NULL DEFAULT '[]',          -- [{"topic": str, "pages": [int]}]
        geography JSONB NOT NULL DEFAULT '{}',       -- {"level": "state|lga|ward|national|zone", "places": [str]}
        period TEXT NOT NULL DEFAULT '',
        year_from INT,
        year_to INT,
        measures JSONB NOT NULL DEFAULT '[]',        -- [str]
        model TEXT NOT NULL DEFAULT '',
        built_at TIMESTAMPTZ NOT NULL DEFAULT now(),
        embedding vector(384)
    );
    CREATE TABLE IF NOT EXISTS section_cards (
        id BIGSERIAL PRIMARY KEY,
        doc_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        seq INT NOT NULL,
        title TEXT NOT NULL DEFAULT '',
        kind TEXT NOT NULL DEFAULT 'section',        -- chapter | section | table
        page_from INT NOT NULL,
        page_to INT NOT NULL,
        summary TEXT NOT NULL DEFAULT '',
        topics JSONB NOT NULL DEFAULT '[]',
        geography JSONB NOT NULL DEFAULT '{}',
        period TEXT NOT NULL DEFAULT '',
        measures JSONB NOT NULL DEFAULT '[]',
        embedding vector(384),
        UNIQUE (doc_id, seq)
    );
    CREATE INDEX IF NOT EXISTS section_cards_doc_idx ON section_cards (doc_id);
    CREATE TABLE IF NOT EXISTS doc_links (
        doc_a TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        doc_b TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
        reason TEXT NOT NULL,
        score REAL NOT NULL,
        PRIMARY KEY (doc_a, doc_b)
    );
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS doc_links; DROP TABLE IF EXISTS section_cards; DROP TABLE IF EXISTS doc_cards;")
