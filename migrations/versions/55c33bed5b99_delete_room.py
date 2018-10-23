"""delete room

Revision ID: 55c33bed5b99
Revises: 99eabe5c256f
Create Date: 2018-10-13 19:59:19.508247

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55c33bed5b99'
down_revision = '99eabe5c256f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('players',
    sa.Column('log_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['log_id'], ['log.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['user.id'], )
    )
    op.add_column('game', sa.Column('category_id', sa.Integer(), nullable=False))
    op.add_column('game', sa.Column('game_file', sa.String(length=1024), nullable=True))
    op.add_column('game', sa.Column('language', sa.String(length=1024), nullable=True))
    op.add_column('game', sa.Column('level', sa.String(length=1024), nullable=True))
    op.add_column('game', sa.Column('player_num', sa.String(length=1024), nullable=True))
    op.add_column('game', sa.Column('rules', sa.String(length=1024), nullable=True))
    op.create_foreign_key(None, 'game', 'category', ['category_id'], ['id'])
    op.drop_constraint(None, 'log', type_='foreignkey')
    op.drop_constraint(None, 'log', type_='foreignkey')
    op.drop_column('log', 'code_id_list')
    op.drop_column('log', 'user_id')
    op.add_column('room', sa.Column('max_people', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'room', ['roomname'])
    op.drop_constraint(None, 'room', type_='foreignkey')
    op.drop_constraint(None, 'room', type_='foreignkey')
    op.create_foreign_key(None, 'room', 'user', ['max_people'], ['id'])
    op.drop_column('room', 'max_players')
    op.drop_column('room', 'is_all_in_room')
    op.drop_column('room', 'playerlist')
    op.drop_column('room', 'audience_list')
    op.drop_column('room', 'log_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('room', sa.Column('log_id', sa.INTEGER(), nullable=True))
    op.add_column('room', sa.Column('audience_list', sa.VARCHAR(length=1024), nullable=True))
    op.add_column('room', sa.Column('playerlist', sa.VARCHAR(length=512), nullable=True))
    op.add_column('room', sa.Column('is_all_in_room', sa.INTEGER(), nullable=True))
    op.add_column('room', sa.Column('max_players', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'room', type_='foreignkey')
    op.create_foreign_key(None, 'room', 'user', ['max_players'], ['id'])
    op.create_foreign_key(None, 'room', 'log', ['log_id'], ['id'])
    op.drop_constraint(None, 'room', type_='unique')
    op.drop_column('room', 'max_people')
    op.add_column('log', sa.Column('user_id', sa.INTEGER(), nullable=True))
    op.add_column('log', sa.Column('code_id_list', sa.INTEGER(), nullable=True))
    op.create_foreign_key(None, 'log', 'user', ['user_id'], ['id'])
    op.create_foreign_key(None, 'log', 'code', ['code_id_list'], ['id'])
    op.drop_constraint(None, 'game', type_='foreignkey')
    op.drop_column('game', 'rules')
    op.drop_column('game', 'player_num')
    op.drop_column('game', 'level')
    op.drop_column('game', 'language')
    op.drop_column('game', 'game_file')
    op.drop_column('game', 'category_id')
    op.drop_table('players')
    op.drop_table('category')
    # ### end Alembic commands ###