"""Official warnings and outbreak figures (docs/hazard-and-services.md section 5).

- advisories: NEMA, NIHSA, NiMet, Sokoto SEMA (state portal) and Sokoto Ministry of Health posts that are alerts,
  warnings, outlooks or outbreak notices for Sokoto: the verbatim excerpt (the hazard's sentences; no sentence
  naming an office holder), its issue date, the LGAs it names (P-codes) or state-wide, its URL and language.
- outbreak_cases: Sokoto's figures from NCDC weekly situation reports (suspected, confirmed, deaths) per disease
  and epi week, each number checked against the page it was read from.

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-30
"""

from alembic import op

revision = "0013"
down_revision = "0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE advisories (
        id            BIGSERIAL PRIMARY KEY,
        source        TEXT NOT NULL,                 -- the registry publisher id: nema_alerts, sokoto_moh ...
        title         TEXT NOT NULL,
        kind          TEXT NOT NULL,                 -- alert | outlook | report | notice
        hazard        TEXT NOT NULL,                 -- flood | heat | dust | rain | fire | storm | cholera | ...
        issued_at     TIMESTAMPTZ NOT NULL,
        valid_until   TIMESTAMPTZ,                   -- when the source states it
        lgas          TEXT[] NOT NULL DEFAULT '{}',  -- P-codes it names
        state_wide    BOOLEAN NOT NULL DEFAULT false,
        text          TEXT NOT NULL,                 -- verbatim excerpt
        url           TEXT NOT NULL,
        key           TEXT NOT NULL UNIQUE,          -- a post's URL; for a document: doc_id:page:item
        doc_id        TEXT,                          -- an outlook from a library document (NIHSA AFO, NiMet SCP)
        page          INT,
        covers        TEXT,                          -- the months a statement is about ('October-November 2026')
        issued_label  TEXT,                          -- the issue date as printed ('April 2026')
        language      TEXT NOT NULL DEFAULT 'en',
        fetched_at    TIMESTAMPTZ NOT NULL DEFAULT now()
    );
    CREATE INDEX advisories_hazard ON advisories (hazard, issued_at DESC);

    CREATE TABLE outbreak_cases (
        id            BIGSERIAL PRIMARY KEY,
        disease       TEXT NOT NULL,                 -- lassa | csm | cholera | measles | diphtheria
        year          INT NOT NULL,
        epi_week      INT NOT NULL,
        report_date   DATE,
        period        TEXT NOT NULL,                 -- what the figures cover, as the report says ('week 40', 'weeks 1-40')
        suspected     INT,
        confirmed     INT,
        deaths        INT,
        listed        BOOLEAN NOT NULL,              -- Sokoto is in the report's state table (false: not listed)
        doc_id        TEXT,
        page          INT,
        url           TEXT NOT NULL,
        fetched_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
        UNIQUE (disease, url)
    );
    CREATE INDEX outbreak_cases_disease ON outbreak_cases (disease, year DESC, epi_week DESC);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE outbreak_cases, advisories;")
