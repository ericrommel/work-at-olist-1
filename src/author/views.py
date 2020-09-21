import os
from csv import DictReader
from flask import abort, jsonify, request, app, url_for
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from werkzeug.utils import secure_filename

from . import author
from .. import allowed_file, current_dir, db, LOGGER, UPLOAD_FOLDER
from ..models import Author, authors_schema, author_schema


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
    pages["results"] = query_result[(start - 1) : (start - 1 + limit)]
    return pages


# Author views
@author.route("/authors", methods=["GET"])
@author.route("/authors/page/<int:page>")
def list_authors(page=1, per_page=20):
    """
    List all authors
    """

    LOGGER.info("Get the list of authors from the database")
    try:
        all_authors = authors_schema.dump(Author.query.order_by(Author.id.asc()))
    except OperationalError:
        LOGGER.info("There is no authors in the database")
        all_authors = None

    if all_authors is None:
        return jsonify({"Warning": "There is no data to show"})

    LOGGER.info("Response the list of authors")
    return jsonify(
        get_paginated_list(
            query_result=all_authors,
            url=url_for("book.list_books"),
            start=request.args.get("start", page),
            limit=request.args.get("limit", per_page),
        )
    )


@author.route("/authors/<int:id>", methods=["GET"])
def author_detail(id):
    """
    List details for an author
    """

    author = Author.query.get_or_404(id)
    return author_schema.jsonify(author)


@author.route("/authors/<int:id>/books", methods=["GET"])
def list_books_for_an_author(id):
    """
    List all books for an author
    """

    author = Author.query.get_or_404(id)
    return author_schema.jsonify(author.books)


@author.route("/authors/add", methods=["POST"])
def add_author():
    """
    Add an author to the database
    """

    author_name = ""

    LOGGER.info("Set author variable from request")
    try:
        author_name = request.json.get("name")
    except KeyError as e:
        abort(400, f"There is no key with that value: {e}")

    author_instance = Author()
    author_instance.name = author_name

    LOGGER.info(f"Add author {author_name} to the database")
    try:
        # Add author to the database
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
    try:
        author_instance.name = request.json["name"]

    except KeyError as e:
        abort(400, f"There is no key with that value: {e}")

    LOGGER.info(f"Edit author {author_instance.id} in the database")
    try:
        # Edit author in the database
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
