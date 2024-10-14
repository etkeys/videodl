"""seed recovery account

Revision ID: c59603c832e3
Revises: 19fe5bd4d51e
Create Date: 2024-10-13 21:09:38.891049

"""

from alembic import op
import sqlalchemy as sa

from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision = "c59603c832e3"
down_revision = "19fe5bd4d51e"
branch_labels = None
depends_on = None


def upgrade():
    users_table = table(
        "users",
        column("id", sa.String(length=36)),
        column("auth_id", sa.String(length=36)),
        column("email", sa.String(length=255)),
        column("name", sa.String(length=255)),
        column("pw_hash", sa.String(length=60)),
        column("is_admin", sa.Boolean()),
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": "4559f485-c0b1-400d-8db6-1cc114f9c6a1",
                "auth_id": "63c41f46-e4cd-4e4f-8703-c273d1dfa065",
                "email": "",
                "name": "recovery",
                "pw_hash": "$2b$12$MC68/gZ2GXlQMABtU.wtxukBJlOuBMk/tTLsceRII7nBpW1TAYhSe",
                "is_admin": True,
            }
        ],
    )


def downgrade():
    users_table = table("users", column("id", sa.String(length=36)))

    op.execute(
        users_table.delete().where(
            users_table.c.id
            == op.inline_literal("4559f485-c0b1-400d-8db6-1cc114f9c6a1")
        )
    )
