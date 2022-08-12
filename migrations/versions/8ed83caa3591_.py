"""Add relationships between all three tables.

Revision ID: 8ed83caa3591
Revises: 881207c8259d
Create Date: 2022-08-13 00:05:10.473741

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8ed83caa3591'
down_revision = '881207c8259d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('venue_id', sa.Integer(), nullable=True))
    op.add_column('Show', sa.Column('artist_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'Show', 'Venue', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'Show', 'Artist', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_constraint(None, 'Show', type_='foreignkey')
    op.drop_column('Show', 'artist_id')
    op.drop_column('Show', 'venue_id')
    # ### end Alembic commands ###
