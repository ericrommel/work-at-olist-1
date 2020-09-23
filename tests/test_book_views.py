from tests.conftest import get_url, generic_post, generic_put


def test_list_book_view(app, client):
    """
    Test list books
    """

    target_url = get_url(app=app, url="book.list_books")
    response = client.get(target_url)
    assert response.status_code == 200


def test_book_detail_view(app, client):
    """
    Test list book details
    """

    target_url = get_url(app=app, url="book.book_detail", id=1)
    response = client.get(target_url)
    assert response.status_code == 200


def test_book_detail_that_does_not_exist_view(app, client):
    """
    Test list book details that does not exist
    """

    target_url = get_url(app=app, url="book.book_detail", id=1000000)
    response = client.get(target_url)
    assert response.status_code == 404


def test_add_book_view(app):
    """
    Test add a book
    """

    target_url = get_url(app=app, url="book.add_book")
    a_dict = dict(
        name="The Niggard Rich",
        edition="2nd Edition",
        publication_year="1954",
    )
    response = generic_post(target_url, a_dict)
    assert response.status_code == 201


def test_edit_book_view(app):
    """
    Test edit a book
    """

    target_url = get_url(app=app, url="book.edit_book", id=1)
    a_dict = dict(
        name="The Hobbit",
        edition="1st Edition",
        publication_year="1937",
    )
    response = generic_put(target_url, a_dict)
    assert response.status_code == 200


def test_edit_book_that_does_not_exist_view(app, client):
    """
    Test edit a book that does not exist
    """

    target_url = get_url(app=app, url="book.edit_book", id=1000000)
    response = client.put(target_url)
    assert response.status_code == 404


def test_delete_book_view(app, client):
    """
    Test delete a book
    """

    target_url = get_url(app=app, url="book.delete_book", id=1)
    response = client.delete(target_url)
    assert response.status_code == 200


def test_delete_book_that_does_not_exist_view(app, client):
    """
    Test delete a book that does not exist
    """

    target_url = get_url(app=app, url="book.delete_book", id=1000000)
    response = client.delete(target_url)
    assert response.status_code == 404
