import os

from flask import Flask, make_response, redirect
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

from Iris.configurations.config import app_config
from Iris.handlers.error_handler import JsonExceptionHandler


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)

    @app.route('/')
    def docs():
        return redirect('apidocs')
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

    app.config['SWAGGER'] = {
        "swagger": "2.0",
        "title": "iRis",
        "description": "**Powered** by **Flask!** \
            \n###THIS API GIVES YOU POWER TO:\
            \n + Register, login and manage their account. \
            \n + Create, update, view and delete a category. \
            \n + Add, update, view or delete recipes. \
            \n + Enable logging of data manipulation timestamps. ",
        "termsOfService": "https://opensource.org/ToS",
        "version": "2.0",
        "contact": {
            "email": "Thalkifly.hassan@andela.com",
            "license": {
                "name": "Apache 2.0",
                "url": "http://www.apache.org/licenses/LICENSE-2.0.html"
            }
        },
        "schemes": [
            "http",
            "https"
        ],
        "host": "api-iris.herokuapp.com",
        "securityDefinitions": {
            "TokenHeader": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        },
        "tags": [
            {
                "name": "auth",
                "description": "All functionality about authention of the user"
            },
            {
                "name": "Categories",
                "description": "All functionality on the categories endpoint"
            },
            {
                "name": "Recipes",
                "description": "All functionality on the Recipes endpoint"
            }
        ]
    }
    Swagger(app)
    return app
