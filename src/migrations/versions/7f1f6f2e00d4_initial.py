"""initial

Revision ID: 7f1f6f2e00d4
Revises:
Create Date: 2026-02-26 21:08:13.392009

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f1f6f2e00d4"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "activities",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["activities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "buildings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=False),
        sa.Column("longitude", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_buildings_address"), "buildings", ["address"], unique=False
    )
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("building_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["building_id"],
            ["buildings.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_organizations_building_id"),
        "organizations",
        ["building_id"],
        unique=False,
    )
    op.create_table(
        "organization_activity",
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["activity_id"],
            ["activities.id"],
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("organization_id", "activity_id"),
    )
    op.create_table(
        "phones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("phones")
    op.drop_table("organization_activity")
    op.drop_index(op.f("ix_organizations_building_id"), table_name="organizations")
    op.drop_table("organizations")
    op.drop_index(op.f("ix_buildings_address"), table_name="buildings")
    op.drop_table("buildings")
    op.drop_table("activities")
