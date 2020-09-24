import json

from tests.conftest import get_url


def test_list_authors_view(app, client):
    """
    Test list authors
    """

    response = client.get(get_url(app=app, url="author.list_authors"))
    assert response.status_code == 200


def test_author_details_view(app, client):
    """
    Test list an author details
    """

    response = client.get(get_url(app=app, url="author.author_detail", id=1))
    assert response.status_code == 200


def test_add_author_view(app, client):
    """
    Test add an author
    """

    response = client.post(
        get_url(app=app, url="author.add_author"),
        data=json.dumps({"name": "J. R. R. Tolkien"}),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 201


def test_author_detail_that_does_not_exist_view(app, client):
    """
    Test list an author details that doesn't exist
    """

    response = client.get(get_url(app=app, url="author.author_detail", id=10000000))
    assert response.status_code == 404


def test_edit_author_view(app, client):
    """
    Test edit an author
    """

    response = client.put(
        get_url(app=app, url="author.edit_author", id=1),
        data=json.dumps({"name": "J. R. R. Tolkien"}),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 200


def test_edit_author_that_does_not_exist_view(app, client):
    """
    Test edit an author that does not exist
    """

    response = client.put(get_url(app=app, url="author.edit_author", id=1000000))
    assert response.status_code == 404


def test_delete_author_view(app, client):
    """
    Test delete an author
    """

    response = client.delete(get_url(app=app, url="author.delete_author", id=1))
    assert response.status_code == 200


def test_delete_author_that_does_not_exist_view(app, client):
    """
    Test delete an author that does not exist
    """

    response = client.delete(get_url(app=app, url="author.delete_author", id=1000000))
    assert response.status_code == 404
