"""correct trigger function

Revision ID: a3146f58caf8
Revises: 68733a8cdb36
Create Date: 2026-09-29 10:27:46.834773

"""

import os
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a3146f58caf8"
down_revision: Union[str, Sequence[str], None] = "68733a8cdb36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
  """Upgrade schema."""
  # Читаем SQL файл с данными и выполняем его
  BASE_DIR = Path(__file__).resolve().parents[2]
  SQL_DIR = Path(BASE_DIR, "psql-configs")

  triggers_path = os.path.join(SQL_DIR, "triggers.sql")
  with open(triggers_path, "r", encoding="utf-8") as f:
    sql_trigger = f.read()
  op.execute(sa.text(sql_trigger))


def downgrade() -> None:
  """Downgrade schema."""
  pass
