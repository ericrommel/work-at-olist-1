from sqlalchemy.orm import relationship, backref
from src import db, LOGGER


association_table = db.Table(
    'association',
    db.metadata,
    db.Column('book_id', db.Integer, db.ForeingKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeingKey('authors.id'))
)


class Book(db.Model):
    """
    Create a Book table
    """

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    edition = db.Column(db.String(10), index=True)
    publication_year = db.Column(db.Integer(), index=True)
    authors = relationship('Author', secundary=association_table, backref='books')

    def __repr__(self):
        return f"<Book: {self.name}>"


class Author(db.Model):
    """
    Create an Author table
    """

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    books = relationship('Book', secondary=association_table, backref='authors')

    def __repr__(self):
        return f"<Author: {self.name}>"
