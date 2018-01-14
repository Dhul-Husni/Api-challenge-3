from flask import Blueprint

# This is an instance of Blueprint that represents the SEARCH blueprint

search_blueprint = Blueprint('search', __name__)

from . import search_view
