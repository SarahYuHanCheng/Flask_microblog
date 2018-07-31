"""add game_id to code

Revision ID: ff9fb9e985da
Revises: 87c975aca762
Create Date: 2018-07-29 14:13:57.040943

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff9fb9e985da'
down_revision = '87c975aca762'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('ranks')
    op.add_column('code', sa.Column('game_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'code', 'game', ['game_id'], ['id'])
    op.drop_column('user', 'about_me')
    op.drop_column('user', 'last_seen')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_seen', sa.DATETIME(), nullable=True))
    op.add_column('user', sa.Column('about_me', sa.VARCHAR(length=140), nullable=True))
    op.drop_constraint(None, 'code', type_='foreignkey')
    op.drop_column('code', 'game_id')
    op.create_table('ranks',
    sa.Column('player_id', sa.INTEGER(), nullable=True),
    sa.Column('game_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['game.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['user.id'], )
    )
    # ### end Alembic commands ###
