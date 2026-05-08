"""add_unique_title_to_tasks_manual

Revision ID: 174f34b15c81
Revises: 1843b7330352
Create Date: 2026-05-08 13:44:57.781179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '174f34b15c81'
down_revision: Union[str, Sequence[str], None] = '1843b7330352'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_tasks_title", "tasks", ["title"])


def downgrade() -> None:
    op.drop_constraint("uq_tasks_title", "tasks", type_="unique")
