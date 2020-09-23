import json
import string
from random import choice

import pytest
from flask import url_for

from src import create_app, db
from src.models import Author, Book, AuthorBook


def get_url(app, url, next_url=None, id=None):
    with app.test_request_context():
        return url_for(url, next=next_url, id=id)


def generic_put(self, url, a_dict):
    """
    Generic PUT request
    """

    return self._client.put(url, data=json.dumps(a_dict), content_type="application/json", follow_redirects=True)


def generic_post(self, url, a_dict):
    """
    Generic POST request
    """

    return self._client.post(url, data=json.dumps(a_dict), content_type="application/json", follow_redirects=True)


@pytest.fixture()
def app():
    """
    Create app with a database test
    """

    SQLALCHEMY_DATABASE_URI = "sqlite:///../tests/olist-test.db"

    app = create_app()
    app.config.from_object("config.TestingConfig")
    app.config.update(SQLALCHEMY_DATABASE_URI=SQLALCHEMY_DATABASE_URI)
    app.config.update(PRESERVE_CONTEXT_ON_EXCEPTION=False)

    with app.app_context():
        # Will be called before every test
        db.create_all()

        # Create 2 Authors
        author_1 = Author()
        author_1.name = "Molnar Ferenc"

        author_2 = Author()
        author_2.name = "Ariano Suassuna"

        # Create 2 books
        book_1 = Book()
        book_1.name = "The Paul Street Boys"
        book_1.edition = "5th Edition"
        book_1.publication_year = "1934"

        book_2 = Book()
        book_2.name = "The Saint and The Sow"
        book_2.edition = "3rd Edition"
        book_2.publication_year = "2002"

        db.session.add(author_1)
        db.session.add(author_2)
        db.session.add(book_1)
        db.session.add(book_1)
        db.session.commit()

        # Create 2 associations
        book_1 = Book.query.filter_by(name="The Paul Street Boys").first()
        author_1 = Author.query.filter_by(name="Molnar Ferenc").first()

        book_2 = Book.query.filter_by(name="The Saint and The Sow").first()
        author_2 = Author.query.filter_by(name="Ariano Suassuna").first()

        author_book_1 = AuthorBook()
        author_book_1.book_id = book_1.id
        author_book_1.author_id = author_1.id

        author_book_2 = AuthorBook()
        author_book_2.book_id = book_2.id
        author_book_2.author_id = author_2.id

        db.session.add(author_book_1)
        db.session.add(author_book_2)
        db.session.commit()

        yield app

        # Will be called after every test
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """
    Make requests to the application without running the server
    """

    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


def json_of_response(response):
    """
    Decode json from response
    """

    return json.loads(response.data.decode("utf8"))


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    a_string = "".join(choice(letters) for i in range(length))
    return a_string


def get_random_int(length: int) -> int:
    if length > 10:
        length = 10

    numbers = "0123456789"
    a_string = "".join(choice(numbers) for i in range(length))
    return int(a_string)
