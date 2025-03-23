"""add original_image_id column

Revision ID: 311ec12fad70
Revises: 18b71e704fe9
Create Date: 2025-03-23 19:55:00.810703

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '311ec12fad70'
down_revision: Union[str, None] = '18b71e704fe9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.add_column(sa.Column('original_image_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_images_original_image_id_images',
            'images',
            ['original_image_id'],
            ['id']
        )


def downgrade():
    with op.batch_alter_table("images", schema=None) as batch_op:
        batch_op.drop_constraint('fk_images_original_image_id_images', type_='foreignkey')
        batch_op.drop_column('original_image_id')
