import json

from flask import abort, jsonify, request, url_for, g
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from . import book
from .. import db, LOGGER
from ..models import AuthorBook, Book, books_schema, book_schema, Author


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
    pages["results"] = query_result[(start - 1): (start - 1 + limit)]
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
        all_books = books_schema.dump(Book.query.order_by(Book.name.asc()))
    except OperationalError:
        LOGGER.info("There is no book in the database")
        all_books = None

    if all_books is None:
        return jsonify({"Warning": "There is no data to show"})

    LOGGER.info("Response the list of books")
    return get_paginated_list(
        query_result=all_books,
        url=url_for("book.list_books"),
        start=request.args.get("start", page),
        limit=request.args.get("limit", per_page),
    ), 200


@book.route("/books/<int:id>", methods=["GET"])
def books_detail(id):
    """
    List details for a book
    """

    book_instance = book_instance = Book.query.get_or_404(id)
    author_instance = AuthorBook.query.filter_by(book_id=book_instance.id).all()
    authors = [author.author_id for author in author_instance]

    LOGGER.info(f"Return book added: '{book_instance.name}'")
    return {
        'id': book_instance.id,
        'name': book_instance.name,
        'publication_year': book_instance.publication_year,
        'authors': authors
    }, 200


@book.route("/books/add", methods=["POST"])
def add_book():
    """
    Add a book to the database
    """

    request_fields = request.get_json() if request.get_json() else request.form
    LOGGER.info("Check for missed fields")
    mandatory_fields = ["name", "edition", "publication_year"]
    missing_fields = []
    for m_field in mandatory_fields:
        if m_field not in request_fields:
            LOGGER.info(f'{m_field} key is missing.')
            missing_fields.append(m_field)
    if missing_fields:
        abort(400, f"{' and '.join(missing_fields)} {'field is' if len(missing_fields) == 1 else 'fields are'} missing.")

    LOGGER.info("Set book variables from request")
    book_instance = Book()
    book_instance.name = request_fields.get("name")
    book_instance.edition = request_fields.get("edition")
    book_instance.publication_year = request_fields.get("publication_year")

    LOGGER.info(f"Add book '{book_instance.name}' to the database")
    try:
        # Add book to the database (it will generate an book_id to store at the association table)
        db.session.add(book_instance)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(403, f"SQLAlchemyError: {e}")
    except Exception as e:
        abort(500, e)

    book_instance = Book.query.filter_by(name=request_fields.get("name")).first()
    if 'authors' in request_fields:
        LOGGER.info(f"Add authors for the book '{book_instance.name}'")

        for author in request_fields.get("authors"):
            association_instance = AuthorBook()
            association_instance.author_id = author
            association_instance.book_id = book_instance.id
            try:
                db.session.add(association_instance)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                abort(403, f"SQLAlchemyError: {e}")
            except Exception as e:
                abort(500, e)

    LOGGER.info(f"Return book added: '{book_instance.name}'")
    author_instance = AuthorBook.query.filter_by(book_id=book_instance.id).all()
    authors = [author.author_id for author in author_instance]

    return {
        'id': book_instance.id,
        'name': book_instance.name,
        'publication_year': book_instance.publication_year,
        'authors': authors
    }, 201


@book.route("/books/edit/<int:id>", methods=["PUT"])
def edit_book(id):
    """
    Edit a book
    """

    book_instance = Book.query.get_or_404(id)

    LOGGER.info("Set book variable from request")
    request_fields = request.get_json() if request.get_json() else request.form

    book_instance.name = request_fields.get("name", book_instance.name)
    book_instance.edition = request_fields.get("edition", book_instance.edition)
    book_instance.publication_year = request_fields.get("publication_year", book_instance.publication_year)

    if 'authors' in request_fields:
        LOGGER.info(f"Edit authors for the book '{book_instance.name}'")
        for author in request_fields.get("authors"):
            author_book_instance = AuthorBook()
            author_book_instance.author_id = author
            author_book_instance.book_id = book_instance.id
            try:
                db.session.add(author_book_instance)
                db.session.commit()
            except SQLAlchemyError as e:
                db.session.rollback()
                abort(403, f"SQLAlchemyError: {e}")
            except Exception as e:
                abort(500, e)

    LOGGER.info(f"Edit book {book_instance.id} in the database")
    try:
        # Edit book in the database
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        abort(400, f"SQLAlchemyError: {e}.")
    except Exception as e:
        abort(500, e)

    LOGGER.info(f"Return book edited: '{book_instance.name}'")
    author_instance = AuthorBook.query.filter_by(book_id=book_instance.id).all()
    authors = [author.author_id for author in author_instance]

    return {
        'id': book_instance.id,
        'name': book_instance.name,
        'publication_year': book_instance.publication_year,
        'authors': authors
    }, 200


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
