import os
import pathlib
from csv import DictReader

from flask import abort, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from . import author
from .. import allowed_file, current_dir, db, LOGGER
from ..models import Author, authors_schema, author_schema, AuthorBook


def get_paginated_list(query_result: list, url: str, start: int, limit: int) -> dict:
    """
    Return a paginate response
    """

    LOGGER.info("Prepare pagination")
    try:
        if not isinstance(start, int):
            start = int(start)

        if not isinstance(limit, int):
            limit = int(limit)

    except ValueError as error:
        LOGGER.error(f'ValueError: {error}')
        abort(400, "Invalid value for the parameters")

    count = len(query_result)

    if count < start:
        abort(404, "Start value is greater than the query results")

    pages = {"start": start, "limit": limit, "count": count}

    LOGGER.info("Build the urls to return")
    if start == 1:
        pages["previous"] = ""
    else:
        start_copy = max(1, start - limit)
        limit_copy = start - 1
        pages["previous"] = url + "?start=%d&limit=%d" % (start_copy, limit_copy)

    if start + limit > count:
        pages["next"] = ""
    else:
        start_copy = start + limit
        pages["next"] = url + "?start=%d&limit=%d" % (start_copy, limit)

    LOGGER.info("Extract result according to the bounds")
    pages["results"] = query_result[(start - 1): (start - 1 + limit)]

    return pages


# Author views
@author.route("/authors", methods=["GET"])
@author.route("/authors/page/<int:page>")
def list_authors(page=1, per_page=20):
    """
    List all authors
    """

    request_fields = request.get_json() if request.get_json() else request.args

    LOGGER.info("Get the list of authors from the database")
    all_authors = None
    try:
        query = db.session.query(Author)

        if "name" in request_fields:
            LOGGER.info(f"Filtering by {request_fields.get('name')}")
            query = query.filter(Author.name.like(f'%{request_fields.get("name")}%'))

        all_authors = authors_schema.dump(query.order_by(Author.name.asc()).all(), many=True)
    except Exception as error:
        LOGGER.error(f"ExceptionError: {error}")
        abort(500, error)

    if not all_authors:
        return {"message": "There is no data to show"}, 404

    LOGGER.info("Response the list of authors")
    return get_paginated_list(
        query_result=all_authors,
        url=url_for("author.list_authors"),
        start=request_fields.get("start", page),
        limit=request_fields.get("limit", per_page),
    ), 200


@author.route("/authors/<int:id>", methods=["GET"])
def author_detail(id):
    """
    List details for an author
    """

    author_instance = Author.query.get_or_404(id)
    author_book_instance = AuthorBook.query.filter_by(author_id=author_instance.id).all()
    books = [book.book_id for book in author_book_instance]

    LOGGER.info(f"Return details for the author: '{author_instance.name}'")
    return {
        'id': author_instance.id,
        'name': author_instance.name,
        'books': books
    }, 200


@author.route("/authors/add", methods=["POST"])
def add_author():
    """
    Add an author to the database
    """

    request_fields = request.get_json() if request.get_json() else request.form
    if "name" not in request_fields:
        abort(400, "Name is a mandatory field.")

    author_instance = Author()
    author_instance.name = request_fields.get("name")

    if request_fields.get("name") is None or not request_fields.get("name").strip():
        abort(400, "Name cannot be empty or null.")

    LOGGER.info(f"Add author {author_instance.name} to the database")
    try:
        db.session.add(author_instance)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(403, f"SQLAlchemyError: {e}")
    except Exception as e:
        abort(500, e)

    return author_schema.jsonify(author_instance), 201


@author.route("/authors/add/bulk", methods=["POST"])
def add_author_bulk():
    """
    Add authors in bulk
    """

    LOGGER.info('Import authors in bulk')

    data_file = pathlib.Path(current_dir, 'author', 'authors_bulk.csv')

    request_fields = request.get_json() if request.get_json() else request.files

    if 'csv_upload' in request_fields:
        LOGGER.info('Request there is a file part. Using it.')
        data_file = request.files['csv_upload']
        if not allowed_file(data_file.filename):
            abort(400, "File not allowed")

        filename = secure_filename(data_file.filename)
        data_file.save(pathlib.Path(current_dir, 'static', filename))
        data_file.close()
        data_file = pathlib.Path(current_dir, 'static', filename)

    try:
        with open(data_file, newline='', encoding='utf-8') as csv_file:
            reader = DictReader(csv_file)

            LOGGER.info("Add authors in bulk to the database")
            try:
                db.session.bulk_insert_mappings(Author, reader)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                abort(403, f"SQLAlchemyError: {e}")
            except Exception as e:
                abort(500, e)

    except FileNotFoundError as error:
        LOGGER.error(f'FileNotFoundException: {error}')
        abort(400, error)

    return {"message": "The authors have successfully been imported."}, 201


@author.route("/authors/edit/<int:id>", methods=["PUT"])
def edit_author(id):
    """
    Edit an author
    """

    author_instance = Author.query.get_or_404(id)

    LOGGER.info("Set author variable from request")
    request_fields = request.get_json() if request.get_json() else request.form

    if "name" not in request_fields:
        abort(400, "Name is a mandatory field.")

    if request_fields.get("name") is None or not request_fields.get("name").strip():
        abort(400, "Name cannot be empty or null.")

    author_instance.name = request_fields.get("name")

    LOGGER.info(f"Edit author {author_instance.id} in the database")
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400, f"SQLAlchemyError: {e}.")
    except Exception as e:
        abort(500, e)

    return author_schema.jsonify(author_instance), 200


@author.route("/authors/delete/<int:id>", methods=["DELETE"])
def delete_author(id):
    """
    Delete an author from the database
    """

    author = Author.query.get_or_404(id)

    LOGGER.info(f"Delete {author} from the database")
    try:
        db.session.delete(author)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400, f"SQLAlchemyError: {e}.")
    except Exception as e:
        abort(500, e)

    return {"message": "The author has successfully been deleted."}, 200
