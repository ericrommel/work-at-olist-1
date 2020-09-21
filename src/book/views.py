from flask import abort, jsonify, request, url_for
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from . import book
from .. import db, LOGGER
from ..models import Book, books_schema, book_schema


def get_paginated_list(query_result, url: str, start: int, limit: int) -> dict:
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


# Books views
@book.route("/books", methods=["GET"])
@book.route("/books/page/<int:page>")
def list_books(page=1, per_page=20):
    """
    List all books
    """

    LOGGER.info("Get the list of books from the database")
    try:
        all_books = books_schema.dump(Book.query.order_by(Book.id.asc()))
    except OperationalError:
        LOGGER.info("There is no book in the database")
        all_books = None

    if all_books is None:
        return jsonify({"Warning": "There is no data to show"})

    LOGGER.info("Response the list of books")
    return jsonify(
        get_paginated_list(
            query_result=all_books,
            url=url_for("book.list_books"),
            start=request.args.get("start", page),
            limit=request.args.get("limit", per_page),
        )
    )


@book.route("/books/<int:id>", methods=["GET"])
def books_detail(id):
    """
    List details for a book
    """

    book_instance = Book.query.get_or_404(id)
    return book_schema.jsonify(book_instance)


@book.route("/books/<int:id>/authors", methods=["GET"])
def list_authors_for_a_book(id):
    """
    List all authors for a book
    """

    book_instance = Book.query.get_or_404(id)
    return books_schema.jsonify(book_instance.authors)


@book.route("/books/add", methods=["POST"])
def add_book():
    """
    Add a book to the database
    """

    LOGGER.info("Check for missed fields")
    mandatory_fields = ["name", "edition", "publication_year"]
    missing_fields = []
    for i in mandatory_fields:
        if i not in request.json:
            LOGGER.info(f'{i} key is missing.')
            missing_fields.append(i)
    if missing_fields:
        abort(400, f"{' and '.join(missing_fields)} {'field is' if len(missing_fields) == 1 else 'fields are'} missing.")

    LOGGER.info("Set book variables from request")
    book_instance = Book()
    book_instance.name = request.json.get("name")
    book_instance.edition = request.json.get("edition")
    book_instance.publication_year = request.json.get("publication_year")
    book_instance.authors = request.json.get("authors", [])

    LOGGER.info(f"Add book {request.json.get('name')} to the database")
    try:
        # Add book to the database
        db.session.add(book_instance)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(403, f"SQLAlchemyError: {e}")
    except Exception as e:
        abort(500, e)

    return book_schema.jsonify(book_instance), 201


@book.route("/books/edit/<int:id>", methods=["PUT"])
def edit_book(id):
    """
    Edit a book
    """

    books_instance = Book.query.get_or_404(id)

    LOGGER.info("Set book variable from request")
    try:
        books_instance.name = request.json.get("name", books_instance.name)
        books_instance.edition = request.json.get("edition", books_instance.edition)
        books_instance.publication_year = request.json.get("publication_year", books_instance.publication_year)
        books_instance.authors = request.json.get("authors", books_instance.authors)
    except KeyError as e:
        abort(400, f"There is no key with that value: {e}")

    LOGGER.info(f"Edit book {books_instance.id} in the database")
    try:
        # Edit book in the database
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400, f"SQLAlchemyError: {e}.")
    except Exception as e:
        abort(500, e)

    return book_schema.jsonify(books_instance), 200


@book.route("/books/delete/<int:id>", methods=["DELETE"])
def delete_book(id):
    """
    Delete a book from the database
    """

    book_instance = Book.query.get_or_404(id)

    LOGGER.info(f"Delete {book_instance} from the database")
    try:
        db.session.delete(book_instance)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400, f"SQLAlchemyError: {e}.")
    except Exception as e:
        abort(500, e)

    return jsonify({"message": "The book has successfully been deleted."}), 200
