import json

from tests.conftest import get_url


def test_list_books_view(app, client):
    """
    Test list books
    """

    response = client.get(get_url(app=app, url="book.list_books"))
    assert response.status_code == 200


def test_list_books_with_invalid_type_to_start_field_view(app, client):
    """
    Test list books using an invalid type to start field (pagination)
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?start=A&limit=100')
    assert response.status_code == 400
    assert "Invalid value for the parameters" in str(response.data)


def test_list_books_with_invalid_type_to_limit_field_view(app, client):
    """
    Test list books using an invalid type to limit field (pagination)
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?start=1&limit=A')
    assert response.status_code == 400
    assert "Invalid value for the parameters" in str(response.data)


def test_list_books_with_start_greater_than_query_results_view(app, client):
    """
    Test list books with start field value greater than the query results count (pagination)
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?start=10000000&limit=10')
    assert response.status_code == 404
    assert "Start value is greater than the query results" in str(response.data)


def test_list_books_use_filter_name_view(app, client):
    """
    Test list books using filter 'name'
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?name=The Paul Street Boys')
    assert response.status_code == 200


def test_list_books_use_filter_edition_view(app, client):
    """
    Test list books using filter 'edition'
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?edition=5th')
    assert response.status_code == 200


def test_list_books_use_filter_publication_year_view(app, client):
    """
    Test list books using filter 'publication_year'
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?publication_year=2002')
    assert response.status_code == 200


def test_list_books_use_all_filters_view(app, client):
    """
    Test list books using all filters available
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?name=Saint&edition=3rd&publication_year=2002')
    assert response.status_code == 200


def test_list_books_use_a_filter_and_there_is_no_data_view(app, client):
    """
    Test list books using a filter that will not get any data
    """

    response = client.get(f'{get_url(app=app, url="book.list_books")}?name=-x-x-x-x-x-x-')

    assert response.status_code == 404
    assert 'There is no data to show' in str(response.data)


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


def test_add_book_without_field_edition_view(app, client):
    """
    Test add a book without the field edition
    """

    response = client.post(
        get_url(app=app, url="book.add_book"),
        data=json.dumps({
            "name": "The Niggard Rich",
            "publication_year": "1954",
        }),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "edition field is missing" in str(response.data)


def test_add_book_without_field_publication_year_view(app, client):
    """
    Test add a book without the field publication year
    """

    response = client.post(
        get_url(app=app, url="book.add_book"),
        data=json.dumps({
            "name": "The Niggard Rich",
            "edition": "2nd Edition",
        }),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "publication_year field is missing" in str(response.data)


def test_add_book_without_field_name_view(app, client):
    """
    Test add a book without the field name
    """

    response = client.post(
        get_url(app=app, url="book.add_book"),
        data=json.dumps({
            "edition": "2nd Edition",
            "publication_year": "1954",
        }),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "name field is missing" in str(response.data)


def test_add_book_with_author_view(app, client):
    """
    Test add a book with an author
    """

    response = client.post(
        get_url(app=app, url="book.add_book"),
        data=json.dumps({
            "name": "The Niggard Rich",
            "edition": "2nd Edition",
            "publication_year": "1954",
            "authors": [2]
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


def test_edit_book_with_author_view(app, client):
    """
    Test add a book with an author
    """

    response = client.put(
        get_url(app=app, url="book.edit_book", id=2),
        data=json.dumps({
            "authors": [2]
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
