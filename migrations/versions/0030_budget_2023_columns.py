"""The 2023 approved budget's columns in the structured core (3 Nov 2026): 2021 full-year actuals, 2022 revised
budget, 2022 January-September performance, 2023 approved budget, 2024 and 2025 out-year estimates, on
budget_items and projects (app/retrieval/entities.py AMOUNTS). Imported with mof.sk.gov.ng's documents.

Revision ID: 0030
Revises: 0029
"""

from alembic import op

revision = "0030"
down_revision = "0029"
branch_labels = None
depends_on = None

COLUMNS = ("actual_2021", "revised_2022", "jan_sep_2022", "approved_2023", "estimate_2024", "estimate_2025")


def upgrade() -> None:
    for table in ("budget_items", "projects"):
        for col in COLUMNS:
            op.execute(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {col} NUMERIC")


def downgrade() -> None:
    for table in ("budget_items", "projects"):
        for col in COLUMNS:
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS {col}")
