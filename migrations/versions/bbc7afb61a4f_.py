"""empty message

Revision ID: bbc7afb61a4f
Revises:
Create Date: 2020-09-23 21:34:03.597647

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bbc7afb61a4f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authors',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=60), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_authors_name'), 'authors', ['name'], unique=False)
    op.create_table('books',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=60), nullable=False),
                    sa.Column('edition', sa.String(length=10), nullable=False),
                    sa.Column('publication_year', sa.Integer(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_books_edition'), 'books', ['edition'], unique=False)
    op.create_index(op.f('ix_books_name'), 'books', ['name'], unique=False)
    op.create_index(op.f('ix_books_publication_year'), 'books', ['publication_year'], unique=False)
    op.create_table('author_books',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('author_id', sa.Integer(), nullable=True),
                    sa.Column('book_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
                    sa.ForeignKeyConstraint(['book_id'], ['books.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('author_books')
    op.drop_index(op.f('ix_books_publication_year'), table_name='books')
    op.drop_index(op.f('ix_books_name'), table_name='books')
    op.drop_index(op.f('ix_books_edition'), table_name='books')
    op.drop_table('books')
    op.drop_index(op.f('ix_authors_name'), table_name='authors')
    op.drop_table('authors')
    # ### end Alembic commands ###