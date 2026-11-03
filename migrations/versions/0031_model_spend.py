"""What the models cost, kept across restarts (3 Nov 2026), for the Meta credit guard (app/spend.py): spend per
hour and provider, and the credit balances read on the Meta dashboard (the API has no balance endpoint: dev.meta.ai
docs, 3 Nov). Server state only: --sync-index never copies these tables.

Revision ID: 0031
Revises: 0030
"""

from alembic import op

revision = "0031"
down_revision = "0030"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS model_spend (
        hour TIMESTAMPTZ NOT NULL,
        provider TEXT NOT NULL,
        calls INTEGER NOT NULL DEFAULT 0,
        prompt_tokens BIGINT NOT NULL DEFAULT 0,
        cached_tokens BIGINT NOT NULL DEFAULT 0,
        completion_tokens BIGINT NOT NULL DEFAULT 0,
        usd NUMERIC NOT NULL DEFAULT 0,
        PRIMARY KEY (hour, provider))""")
    op.execute("""CREATE TABLE IF NOT EXISTS meta_credit_readings (
        id SERIAL PRIMARY KEY,
        usd NUMERIC NOT NULL,
        as_of TIMESTAMPTZ NOT NULL,
        noted_at TIMESTAMPTZ NOT NULL DEFAULT now())""")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS meta_credit_readings")
    op.execute("DROP TABLE IF EXISTS model_spend")
