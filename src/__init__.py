import os

from flask import Flask, jsonify
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from log import Log

LOGGER = Log("work-at-olist").get_logger(logger_name="app")

db = SQLAlchemy()
ma = Marshmallow()

ALLOWED_EXTENSIONS = {'csv'}
current_dir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = '/src/static'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app(test_config=None):
    LOGGER.info("Initialize Flask app")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="TeMpOrArY",
        SQLALCHEMY_DATABASE_URI="sqlite:///./olist.db",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        UPLOAD_FOLDER=UPLOAD_FOLDER
    )

    if test_config is None:
        LOGGER.info("test-config is None. Get configs from config.py")
        app.config.from_pyfile("config.py", silent=True)
    else:
        LOGGER.info(f"test-config is not None ({test_config}). Add configs from mapping")
        app.config.from_mapping(test_config)

    LOGGER.info("Create 'instance' folder")
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    LOGGER.info("Initialize the application for the use with its DB")
    db.init_app(app)

    migrate = Migrate(app, db)

    from src import models

    from src.author import author as author_blueprint
    app.register_blueprint(author_blueprint)

    from src.book import book as book_blueprint
    app.register_blueprint(book_blueprint)

    # Error handling
    @app.errorhandler(400)
    def bad_request(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 401

    @app.errorhandler(403)
    def forbidden(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 403

    @app.errorhandler(404)
    def page_not_found(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 404

    @app.errorhandler(405)
    def not_logged(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        LOGGER.error(e)
        return jsonify(error=str(e)), 500

    return app
