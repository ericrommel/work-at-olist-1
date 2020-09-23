from tests.conftest import get_url, generic_post, generic_put


def test_list_authors_view(app, client):
    """
    Test list authors
    """

    target_url = get_url(app=app, url="author.list_authors")
    response = client.get(target_url)
    assert response.status_code == 200


def test_author_details_view(app, client):
    """
    Test list an author details
    """

    target_url = get_url(app=app, url="author.author_detail", id=1)
    response = client.get(target_url)
    assert response.status_code == 200


def test_add_author_view(app, client):
    """
    Test add an author
    """

    target_url = get_url(app=app, url="author.add_author")
    a_dict = dict(
        name="J. R. R. Tolkien"
    )
    response = generic_post(target_url, a_dict)
    assert response.status_code == 201


def test_author_detail_that_does_not_exist_view(app, client):
    """
    Test list an author details that doesn't exist
    """

    target_url = get_url(app=app, url="author.author_detail", id=10000000)
    response = client.get(target_url)
    assert response.status_code == 404


def test_edit_author_view(app):
    """
    Test edit an author
    """

    target_url = get_url(app=app, url="author.edit_author", id=1)
    a_dict = dict(
        name="William Shakespeare"
    )
    response = generic_put(target_url, a_dict)
    assert response.status_code == 200


def test_edit_author_that_does_not_exist_view(app, client):
    """
    Test edit an author that does not exist
    """

    target_url = get_url(app=app, url="author.edit_author", id=1000000)
    response = client.put(target_url)
    assert response.status_code == 404


def test_delete_author_view(app, client):
    """
    Test delete an author
    """

    target_url = get_url(app=app, url="author.delete_author", id=1)
    response = client.delete(target_url)
    assert response.status_code == 200


def test_delete_author_that_does_not_exist_view(app, client):
    """
    Test delete an author that does not exist
    """

    target_url = get_url(app=app, url="author.delete_author", id=1000000)
    response = client.delete(target_url)
    assert response.status_code == 404
