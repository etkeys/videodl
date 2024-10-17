"""Add item file name

Revision ID: c00040348f55
Revises: c59603c832e3
Create Date: 2024-10-14 19:40:08.897384

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c00040348f55"
down_revision = "c59603c832e3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("download_items", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("file_name", sa.String(length=255), nullable=False)
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("download_items", schema=None) as batch_op:
        batch_op.drop_column("file_name")

    # ### end Alembic commands ###