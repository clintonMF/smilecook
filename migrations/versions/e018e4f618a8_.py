"""empty message

Revision ID: e018e4f618a8
Revises: ff6be83f4dbe
Create Date: 2022-09-26 07:10:43.613310

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e018e4f618a8'
down_revision = 'ff6be83f4dbe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('recipe', sa.Column('ingredients', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('recipe', 'ingredients')
    # ### end Alembic commands ###
