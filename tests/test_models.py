from src.models import Author, Book, AuthorBook


def test_author_model(app):
    """
    Test number of records in Author table
    """

    assert Author.query.count() == 2


def test_book_model(app):
    """
    Test number of records in Book table
    """

    assert Book.query.count() == 2


def test_author_book_model(app):
    """
    Test number of records in AuthorBook (association) table
    """

    assert AuthorBook.query.count() == 2
