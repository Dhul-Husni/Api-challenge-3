from flask import Blueprint

# This is an instance of Blueprint that represents the RECIPES blueprint

recipe_blueprint = Blueprint('recipes', __name__)

from . import recipe_views