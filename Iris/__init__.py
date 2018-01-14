import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from Iris.configurations.config import app_config
from Iris.handlers.error_handler import JsonExceptionHandler


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('configurations/config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('secret_key')
    db.init_app(app)

    from .endpoints.authentication import auth_blueprint
    from .endpoints.categories import category_blueprint
    from .endpoints.recipes import recipe_blueprint
    from .endpoints.search import search_blueprint

    app.register_blueprint(auth_blueprint)
    app.register_blueprint(category_blueprint)
    app.register_blueprint(recipe_blueprint)
    app.register_blueprint(search_blueprint)

    JsonExceptionHandler(app)
    return app
