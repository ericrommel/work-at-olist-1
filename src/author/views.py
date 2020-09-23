import json
import os
from csv import DictReader
from flask import abort, jsonify, request, app, url_for
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.utils import secure_filename

from . import author
from .. import allowed_file, current_dir, db, LOGGER, UPLOAD_FOLDER
from ..models import Author, authors_schema, author_schema, AuthorBook


def get_paginated_list(query_result: list, url: str, start: int, limit: int) -> dict:
    """
    Return a paginate response
    """

    if not isinstance(start, int):
        start = int(start)

    if not isinstance(limit, int):
        limit = int(limit)

    count = len(query_result)

    if count < start:
        abort(404)

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

    LOGGER.info("Get the list of authors from the database")
    all_authors = None
    try:
        all_authors = authors_schema.dump(Author.query.order_by(Author.name.asc()), many=True)
    except Exception as error:
        LOGGER.error(f"ExceptionError: {error}")
        abort(500, error)

    if all_authors is None:
        return jsonify({"message": "There is no data to show"})

    LOGGER.info(f"Response the list of authors: {all_authors}")
    return get_paginated_list(
        query_result=all_authors,
        url=url_for("author.list_authors"),
        start=request.args.get("start", page),
        limit=request.args.get("limit", per_page),
    )


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
    if not request_fields:
        abort(400, "Name is a mandatory field.")

    author_instance = Author()
    try:
        author_instance.name = request_fields.get("name")
    except KeyError as e:
        abort(400, "Name is a mandatory field.")

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

    csv_file = 'author/authors_bulk.csv'
    data_file = os.path.join(current_dir, csv_file)

    if 'csv_upload' in request.files:
        LOGGER.info('Request there is a file part. Using it.')
        data_file = request.files['csv_upload']
        if data_file and allowed_file(data_file.filename):
            filename = secure_filename(data_file.filename)
            data_file.save(os.path.join(current_dir, f'static/{filename}'))
            data_file = os.path.join(current_dir, f'static/{data_file.filename}')

    with open(data_file, newline='') as csv_file:
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

    return jsonify({"message": "The authors have successfully been imported."}), 201


@author.route("/authors/edit/<int:id>", methods=["PUT"])
def edit_author(id):
    """
    Edit an author
    """

    author_instance = Author.query.get_or_404(id)

    LOGGER.info("Set author variable from request")
    request_fields = request.get_json() if request.get_json() else request.form
    try:
        author_instance.name = request_fields.get("name")
    except KeyError as e:
        abort(400, f"There is no key with that value: {e}")

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

    return jsonify({"message": "The author has successfully been deleted."}), 200
