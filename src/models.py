from flask import url_for
from sqlalchemy.orm import relationship

from src import db, ma


class AuthorBook(db.Model):
    """
    Association table between author and book (many to many relationship)
    """

    __tablename__ = 'author_books'

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))


class Author(db.Model):
    """
    Create an Author table
    """

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)

    def get_url(self):
        return url_for("author.list_authors", id=self.id, _external=True)

    def __repr__(self):
        return f"<Author: {self.name}>"


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # Fields to expose
        fields = ("id", "name", "books")
        model = Author
        # load_instance = True


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)


class Book(db.Model):
    """
    Create a Book table
    """

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True, nullable=False)
    edition = db.Column(db.String(10), index=True, nullable=False)
    publication_year = db.Column(db.Integer(), index=True, nullable=False)
    # authors = db.relationship('Author', secondary=association_table, backref='books', lazy="joined")

    def get_url(self):
        return url_for("book.list_books", id=self.id, _external=True)

    def __repr__(self):
        return f"<Book: {self.name}>"


class BookSchema(ma.SQLAlchemyAutoSchema):
    # authors = ma.Nested(AuthorSchema, many=True)

    class Meta:
        # Fields to expose
        fields = ("id", "name", "edition", "publication_year", "authors")
        model = Book
        # load_instance = True
        include_fk = True
    author = ma.Nested(AuthorSchema)


book_schema = BookSchema()
books_schema = BookSchema(many=True)
