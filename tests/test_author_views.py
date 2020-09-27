import json
import os
import pathlib
from io import BytesIO

from tests.conftest import get_url


def test_list_authors_view(app, client):
    """
    Test list authors
    """

    response = client.get(get_url(app=app, url="author.list_authors"))
    assert response.status_code == 200


def test_list_authors_with_invalid_type_to_start_field_view(app, client):
    """
    Test list authors using an invalid type to start field (pagination)
    """

    response = client.get(f'{get_url(app=app, url="author.list_authors")}?start=A&limit=100')
    assert response.status_code == 400
    assert "Invalid value for the parameters" in str(response.data)


def test_list_authors_with_invalid_type_to_limit_field_view(app, client):
    """
    Test list authors using an invalid type to limit field (pagination)
    """

    response = client.get(f'{get_url(app=app, url="author.list_authors")}?start=1&limit=A')
    assert response.status_code == 400
    assert "Invalid value for the parameters" in str(response.data)


def test_list_authors_with_start_greater_than_query_results_view(app, client):
    """
    Test list authors with start field value greater than the query results count (pagination)
    """

    response = client.get(f'{get_url(app=app, url="author.list_authors")}?start=10000000&limit=10')
    assert response.status_code == 404
    assert "Start value is greater than the query results" in str(response.data)


def test_list_authors_use_filter_name_view(app, client):
    """
    Test list authors using filter 'name'
    """

    response = client.get(f'{get_url(app=app, url="author.list_authors")}?name=Ariano')
    assert response.status_code == 200


def test_list_authors_use_filter_name_and_there_is_no_data_view(app, client):
    """
    Test list authors using filter 'name' but with no data to show
    """

    response = client.get(f'{get_url(app=app, url="author.list_authors")}?name=-x-x-x-')

    assert response.status_code == 404
    assert 'There is no data to show' in str(response.data)


def test_author_details_view(app, client):
    """
    Test list an author details
    """

    response = client.get(get_url(app=app, url="author.author_detail", id=1))
    assert response.status_code == 200


def test_author_detail_that_does_not_exist_view(app, client):
    """
    Test list an author details that doesn't exist
    """

    response = client.get(get_url(app=app, url="author.author_detail", id=10000000))
    assert response.status_code == 404


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


def test_add_author_field_name_is_invalid_view(app, client):
    """
    Test add an author with the field name invalid (empty string or spaces there)
    """

    response = client.post(
        get_url(app=app, url="author.add_author"),
        data=json.dumps({"name": ""}),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "Name cannot be empty or null" in str(response.data)


def test_add_author_no_body_view(app, client):
    """
    Test add an author with no body
    """

    response = client.post(
        get_url(app=app, url="author.add_author"),
        data=json.dumps({"age": ""}),
        content_type="application/json",
        follow_redirects=True
    )

    print(response.data)
    assert response.status_code == 400
    assert "Name is a mandatory field" in str(response.data)


def test_add_author_bulk_passing_file_view(app, client):
    """
    Test add author in bulk. A file is sent from the request
    """

    current_dir = os.path.abspath(os.path.dirname(__file__))
    csv_file = 'another_authors_bulk.csv'
    data_file = os.path.join(current_dir, csv_file)
    data_file = pathlib.Path(current_dir, csv_file)

    response = client.post(
        get_url(app=app, url="author.add_author_bulk"),
        data={
            "csv_upload": (open(data_file, 'rb'), data_file.name)
        },
        content_type="multipart/form-data;",
        follow_redirects=True
    )

    assert response.status_code == 201
    assert "The authors have successfully been imported." in str(response.data)


def test_add_author_bulk_no_passing_file_view(app, client):
    """
    Test add author in bulk. The file stored at the server will be used
    """

    response = client.post(
        get_url(app=app, url="author.add_author_bulk"),
        follow_redirects=True
    )

    assert response.status_code == 201
    assert "The authors have successfully been imported." in str(response.data)


def test_add_author_bulk_file_not_allowed_view(app, client):
    """
    Test add author in bulk. A file is sent from the request
    """

    data = dict(
        csv_upload=(BytesIO(b'File content'), "foo.pdf")
    )

    response = client.post(
        get_url(app=app, url="author.add_author_bulk"),
        data=data,
        content_type="multipart/form-data;",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "File not allowed" in str(response.data)


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


def test_edit_author_with_field_name_invalid_view(app, client):
    """
    Test edit an author with the field name invalid (empty string or spaces there)
    """

    response = client.put(
        get_url(app=app, url="author.edit_author", id=1),
        data=json.dumps({"name": ""}),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "Name cannot be empty or null" in str(response.data)


def test_edit_author_with_no_field_name_view(app, client):
    """
    Test edit author with no field name
    """

    response = client.put(
        get_url(app=app, url="author.edit_author", id=1),
        data=json.dumps({"age": ""}),
        content_type="application/json",
        follow_redirects=True
    )

    assert response.status_code == 400
    assert "Name is a mandatory field" in str(response.data)


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
