"""Add missing recipe columns

Revision ID: initial_recipes
Revises: 
Create Date: 2025-11-26 11:55:49.619167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'initial_recipes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to recipes table
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        # Check if columns exist before adding (for idempotency)
        batch_op.add_column(sa.Column('description', sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column('prep_time_minutes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cook_time_minutes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('total_time_minutes', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('cuisine', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('dietary_tags', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('image_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('average_rating', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        
        # Only create foreign key if it doesn't exist
        try:
            batch_op.create_foreign_key('fk_recipes_author_id_users', 'users', ['author_id'], ['id'])
        except:
            pass


def downgrade():
    # Drop the columns if rolling back
    with op.batch_alter_table('recipes', schema=None) as batch_op:
        try:
            batch_op.drop_constraint('fk_recipes_author_id_users', type_='foreignkey')
        except:
            pass
        
        batch_op.drop_column('author_id', if_exists=True)
        batch_op.drop_column('average_rating', if_exists=True)
        batch_op.drop_column('image_filename', if_exists=True)
        batch_op.drop_column('dietary_tags', if_exists=True)
        batch_op.drop_column('cuisine', if_exists=True)
        batch_op.drop_column('total_time_minutes', if_exists=True)
        batch_op.drop_column('cook_time_minutes', if_exists=True)
        batch_op.drop_column('prep_time_minutes', if_exists=True)
        batch_op.drop_column('description', if_exists=True)
