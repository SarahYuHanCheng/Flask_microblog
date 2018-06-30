"""User social_Id

Revision ID: 51f07833b257
Revises: 05e4db8fb2ab
Create Date: 2018-06-30 22:31:30.202901

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51f07833b257'
down_revision = '05e4db8fb2ab'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('social_id', sa.String(length=64), nullable=False))
    op.create_unique_constraint(None, 'user', ['social_id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'social_id')
    # ### end Alembic commands ###
