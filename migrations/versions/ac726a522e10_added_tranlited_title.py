"""added tranlited_title

Revision ID: ac726a522e10
Revises: dac48874b25f
Create Date: 2023-05-18 07:35:03.510153

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac726a522e10'
down_revision = 'dac48874b25f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('jbi_items', sa.Column('tranlited_title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('jbi_items', 'tranlited_title')
    # ### end Alembic commands ###
