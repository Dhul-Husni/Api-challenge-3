"""
Validates data before its added to the data on the endpoint
/recipes
"""
import re

from werkzeug.exceptions import HTTPException

from Iris.models.category_model import RecipeCategory

pattern = r"^[a-zA-Z\s',\._-]+$"


class IllegalRecipeName(HTTPException):
    """
    Exception for recipe name
    """
    def __init__(self):
        HTTPException.__init__(self, "Fatal! Illegal Characters Used" )
        self.code = 406


class LongRecipeName(HTTPException):
    """
    Short Name exception
    """
    def __init__(self):
        HTTPException.__init__(self, "Please use a shorter name or recipe(description)")
        self.code = 411


class ProvideCorrectName(HTTPException):
    """
    Name  does not exist exception
    """

    def __init__(self):
        HTTPException.__init__(self, "please use keys name and recipe (Case Sensitive)")
        self.code = 400


class RecipeDoesNotExist(HTTPException):
    """
    :raises: Recipe does not exist
    """
    def __init__(self):
        HTTPException.__init__(self, "This page does not exist on Iris")
        self.code = 404


class RecipeAlreadyExists(HTTPException):
    """
    :raises: Recipe does not exist
    """
    def __init__(self):
        HTTPException.__init__(self, "Recipe Already Exists")
        self.code = 400


def assert_recipe_exists(user_id, category_id, recipe_id):
    """
    :param user_id: User id
    :param category_id: Category id
    :param recipe_id:  Recipe Id
    :return recipe object
    :raise RecipeDoesNotExist
    """
    category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=category_id).first()
    try:
        recipe_exists = category.recipes.filter_by(id=recipe_id).first()  # raises attr error if category is none
        if not recipe_exists:
            raise RecipeDoesNotExist
    except (AttributeError, RecipeDoesNotExist):
        raise RecipeDoesNotExist
    else:
        return recipe_exists


def assert_recipe(request):
    """
    Assert data is legit
    :param request: Http request
    :return: True Else Exception
    """
    try:
        name = str(request.data.get('name', '')).strip().lower()
        recipe = str(request.data.get('recipe', '')).strip().lower()
    except AttributeError:
        raise IllegalRecipeName
    else:
        if not name or not recipe:
            raise ProvideCorrectName
        validated = bool(re.match(pattern, name)) and bool(re.match(pattern, recipe))

        if validated:
            if len(name) >= 80:
                raise LongRecipeName
            return name, recipe
        else:
            raise IllegalRecipeName
