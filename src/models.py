from sqlalchemy.orm import relationship, backref
from src import db, ma


association_table = db.Table(
    'association',
    db.metadata,
    db.Column('book_id', db.Integer, db.ForeignKey('books.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('authors.id'))
)


class Author(db.Model):
    """
    Create an Author table
    """

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    # books = relationship('Book', secondary=association_table, backref='authors')

    def __repr__(self):
        return f"<Author: {self.name}>"


class AuthorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # Fields to expose
        fields = ("id", "name", "books")
        model = Author
        load_instance = True


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)


class Book(db.Model):
    """
    Create a Book table
    """

    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), index=True)
    edition = db.Column(db.String(10), index=True)
    publication_year = db.Column(db.Integer(), index=True)
    authors = relationship('Author', secondary=association_table, backref='books')

    def __repr__(self):
        return f"<Book: {self.name}>"


class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        # Fields to expose
        fields = ("id", "name", "edition", "publication_year", "authors")
        model = Book
        load_instance = True


book_schema = BookSchema()
books_schema = BookSchema(many=True)
