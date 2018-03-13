"""
Handles search
"""
from flask.views import MethodView
from flask import make_response, request, jsonify
from flasgger import swag_from

from . import search_blueprint
from Iris.handlers.token_handler import assert_token
from Iris.handlers.pagination_handler import assert_pagination
from Iris.handlers.search_handler import assert_search
from Iris.handlers.recipes_handler import RecipeDoesNotExist
from Iris.models.category_model import RecipeCategory

four_oh_four = {"message": "Sorry we could not find what you are looking for"}


class SearchCategory(MethodView):
    """This searches the category for items with similar or equal names to the get
    parameter q"""
    @staticmethod
    @swag_from("docs/Categories_search_get.yml", methods=['GET'])
    def get():
        user_id = assert_token(request)
        q = assert_search(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).all()
        result = []
        for each_category in category:
            if q in each_category.name or q in each_category.detail:
                obj = {
                    "id": each_category.id,
                    "Recipe Category Name": each_category.name.title(),
                    "Recipe Category Detail": each_category.detail.title(),
                    "Date Created": each_category.date_created,
                    "Date Modified": each_category.date_modified
                }
                result.append(obj)
        if not result:
            message = four_oh_four
            result.append(message)
        response = jsonify({'Next Page': None,
                            'Prev Page': None,
                            'Has next':  False,
                            'Has prev': False}, result)
        response.status_code = 200 if result else 404
        return response


class SearchRecipe(MethodView):
    """
    This searches the recipes database for items similar or equal and returns them
    """
    @staticmethod
    @swag_from("docs/Recipes_search_get.yml", methods=['GET'])
    def get(id):
        """This searches the recipes for items with similar or equal names to the get
        parameter q"""
        user_id = assert_token(request)
        q = assert_search(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        try:
            my_recipes = category.recipes.all()
        except AttributeError:
            raise RecipeDoesNotExist
        else:
            result = []
            for each_recipe in my_recipes:
                if q in each_recipe.name or q in each_recipe.recipe:
                    obj = {
                        "id": each_recipe.id,
                        "name": each_recipe.name.title(),
                        "Recipe": each_recipe.recipe.title(),
                        "Date Created": each_recipe.date_created,
                        "Date Modified": each_recipe.date_modified
                    }
                    result.append(obj)
            if not result:
                message = four_oh_four
                result.append(message)
            response = jsonify({'Next Page': None,
                                'Prev Page': None,
                                'Has next':  False,
                                'Has prev': False},result)
            response.status_code = 200 if result else 404
            return response


class SearchAll(MethodView):
    """This searches all the category and recipe for items with similar or equal names to the get
    parameter q"""
    @staticmethod
    def get():
        user_id = assert_token(request)
        q = assert_search(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).all()
        result = []
        for everything in category:
            if q in everything.name or q in everything.detail:
                obj = {
                    "id": everything.id,
                    "Recipe Category Name": everything.name.title(),
                    "Recipe Category Detail": everything.detail.title(),
                    "Date Created": everything.date_created,
                    "Date Modified": everything.date_modified
                }
                result.append(obj)
            my_recipes = everything.recipes.paginate(page=page, per_page=per_page)
            for each_recipe in my_recipes.items:
                if q in each_recipe.name or q in each_recipe.recipe:
                    obj = {
                        "id": each_recipe.id,
                        "Recipe Category Name": each_recipe.name.title(),
                        "Recipe Category Detail": each_recipe.recipe.title(),
                        "Date Created": each_recipe.date_created,
                        "Date Modified": each_recipe.date_modified
                    }
                    result.append(obj)
        if not result:
            message = four_oh_four
            result.append(message)
        response = jsonify({'Next Page': None,
                            'Prev Page': None,
                            'Has next':  False,
                            'Has prev': False}, result)
        response.status_code = 200 if result else 404
        return response


base_url = '/v2/'
# Get by Category
category_search_view = SearchCategory.as_view('category_search_view')
search_blueprint.add_url_rule(base_url+'categories/search', view_func=category_search_view, methods=['GET'])
# Get by Recipe
recipe_search_view = SearchRecipe.as_view('recipe_search_view')
search_blueprint.add_url_rule(base_url+'categories/<int:id>/recipes/search', view_func=recipe_search_view, methods=['GET'])
# Get All
search_view = SearchAll.as_view('search_view')
search_blueprint.add_url_rule(base_url+'search', view_func=search_view, methods=['GET'])
