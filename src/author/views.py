from flask import abort, jsonify, request
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from . import author
from .. import db, LOGGER
from ..models import Author, authors_schema, author_schema


# Author views
@author.route("/authors", methods=["GET"])
def list_authors():
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
    return jsonify(all_authors)


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


@author.route("/authors/add", methods=["GET", "POST"])
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


@author.route("/authors/edit/<int:id>", methods=["GET", "PUT"])
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


@author.route("/authors/delete/<int:id>", methods=["GET", "DELETE"])
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
