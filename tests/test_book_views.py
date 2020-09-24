import json

from tests.conftest import get_url


def test_list_book_view(app, client):
    """
    Test list books
    """

    response = client.get(get_url(app=app, url="book.list_books"))
    assert response.status_code == 200


def test_book_detail_view(app, client):
    """
    Test list book details
    """

    response = client.get(get_url(app=app, url="book.book_detail", id=1))
    assert response.status_code == 200


def test_book_detail_that_does_not_exist_view(app, client):
    """
    Test list book details that does not exist
    """

    response = client.get(get_url(app=app, url="book.book_detail", id=1000000))
    assert response.status_code == 404


def test_add_book_view(app, client):
    """
    Test add a book
    """

    response = client.post(
        get_url(app=app, url="book.add_book"),
        data=json.dumps({
            "name": "The Niggard Rich",
            "edition": "2nd Edition",
            "publication_year": "1954",
        }),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 201


def test_edit_book_view(app, client):
    """
    Test edit a book
    """

    response = client.put(
        get_url(app=app, url="book.edit_book", id=1),
        data=json.dumps({
            "name": "The Hobbit",
            "edition": "1st Edition",
            "publication_year": "1937",
        }),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 200


def test_edit_book_that_does_not_exist_view(app, client):
    """
    Test edit a book that does not exist
    """

    response = client.put(get_url(app=app, url="book.edit_book", id=1000000))
    assert response.status_code == 404


def test_delete_book_view(app, client):
    """
    Test delete a book
    """

    response = client.delete(get_url(app=app, url="book.delete_book", id=1))
    assert response.status_code == 200


def test_delete_book_that_does_not_exist_view(app, client):
    """
    Test delete a book that does not exist
    """

    response = client.delete(get_url(app=app, url="book.delete_book", id=1000000))
    assert response.status_code == 404
