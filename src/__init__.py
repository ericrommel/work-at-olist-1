import os

from flask import Flask, jsonify


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="TeMpOrArY"
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # Error handling
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify(error=str(e)), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify(error=str(e)), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify(error=str(e)), 404

    @app.errorhandler(405)
    def not_logged(e):
        return jsonify(error=str(e)), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify(error=str(e)), 500

    return app
