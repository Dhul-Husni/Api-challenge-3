from flask import Blueprint

# This is an instance of Blueprint that represents the categories blueprint

category_blueprint = Blueprint('categories', __name__)

from . import category_views
