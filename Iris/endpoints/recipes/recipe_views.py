"""
Handles all requests to /recipes endpoint
"""
from flask.views import MethodView
from flask import jsonify, request, make_response

from . import recipe_blueprint
from flasgger import swag_from
from Iris.models.category_model import RecipeCategory
from Iris.models.recipe_model import Recipes
from Iris.handlers.token_handler import assert_token
from Iris.handlers.pagination_handler import assert_pagination
from Iris.handlers.recipes_handler import assert_recipe, assert_recipe_exists, RecipeAlreadyExists


class RecipesGetView(MethodView):
    """
    Handles get request to endpoint /recipes
    """
    @staticmethod
    @swag_from("docs/Recipes_get.yml", methods=['GET'])
    def get(id):
        user_id = assert_token(request)
        page, per_page = assert_pagination(request)
        result = []
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        try:
            recipe_object = category.recipes.paginate(page=page, per_page=per_page)
        except AttributeError:
            return make_response(jsonify({"message": "Category does not exist"})), 404
        else:
            for recipe in recipe_object.items:
                obj = {
                        "id": recipe.id,
                        "name": recipe.name.title(),
                        "Recipe": recipe.recipe.title(),
                        "Date Created": recipe.date_created,
                        "Date Modified": recipe.date_modified
                        }
                result.append(obj)
            if not result:
                result.append("Nothing Here yet")
            response = jsonify({'Next Page': recipe_object.next_num,
                                'Prev Page': recipe_object.prev_num,
                                'Has next': recipe_object.has_next,
                                'Has previous': recipe_object.has_prev}, result)
            return make_response(response), 200


class RecipesIdGetView(MethodView):
    """
    Handles get by id in endpoint /recipes
    """
    @staticmethod
    @swag_from("docs/Recipe_id_get.yml", methods=['GET'])
    def get(category_id, recipe_id):
        user_id = assert_token(request)
        my_recipe = assert_recipe_exists(user_id, category_id, recipe_id)
        for the_recipe in my_recipe:
            response = jsonify({
                                "Recipe Name": the_recipe.name.title(),
                                "Recipe": the_recipe.recipe.title(),
                                "Date Created": the_recipe.date_created,
                                "Date Modified": the_recipe.date_modified,
                                })
            return make_response(response), 200


class RecipesPostView(MethodView):
    """
    Handles post request to endpoint /recipes
    """
    @staticmethod
    @swag_from("docs/Recipes_post.yml", methods=['POST'])
    def post(id):
        user_id = assert_token(request)
        name, recipe = assert_recipe(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        result = []
        if category:
            recipe_exists = category.recipes.filter_by(name=name).first()
            if not recipe_exists:
                new_recipe = Recipes(name=name, recipe=recipe, belonging_to=category)
                new_recipe.save()
                obj = {
                        "id": new_recipe.id,
                        "name": new_recipe.name.title(),
                        "Recipe": new_recipe.recipe.title(),
                        "Date created": new_recipe.date_created,
                        "Date modified": new_recipe.date_modified
                        }
                result.append(obj)
                response = jsonify(result)
                return make_response(response), 201

            elif recipe_exists:
                return make_response(jsonify({"message":"Recipe already exists"})), 404
        else:
            return make_response(jsonify({"message": "Category does not exist"})), 404


class RecipesPutView(MethodView):
    """
    Handles edit request to endpoint /recipes
    """
    @staticmethod
    @swag_from("docs/Recipes_id_edit.yml", methods=['PUT'])
    def put(category_id, recipe_id):
        user_id = assert_token(request)
        my_recipe = assert_recipe_exists(user_id, category_id, recipe_id)
        name, recipe = assert_recipe(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=category_id).first()
        recipe_name_exists = category.recipes.filter_by(name=name).first()
        if not recipe_name_exists:
            for the_recipe in my_recipe:
                the_recipe.name = name
                the_recipe.recipe = recipe
                the_recipe.save()
                reply = jsonify({
                                "Recipe Name": the_recipe.name.title(),
                                "Recipe": the_recipe.recipe.title(),
                                "Date Created": the_recipe.date_created,
                                "Date Modified": the_recipe.date_modified,
                                })
                reply.status_code = 201
                return make_response(reply), 201
        else:
            raise RecipeAlreadyExists


class RecipeDeleteView(MethodView):
    """
    Handles delete request to endpoint /recipes
    """
    @staticmethod
    @swag_from("docs/Recipes_id_delete.yml", methods=['DELETE'])
    def delete(category_id, recipe_id):
        user_id = assert_token(request)
        my_recipe = assert_recipe_exists(user_id, category_id, recipe_id)
        for this_recipe in my_recipe:
            this_recipe.delete()
            return make_response(jsonify({
                       "message": 'Recipe {} was deleted successfully'.format(recipe_id)

                   })), 200


base_url = '/v2/'
# Post
recipes_post_view = RecipesPostView.as_view('recipes_post_view')
recipe_blueprint.add_url_rule(base_url+'categories/<int:id>/recipes', view_func=recipes_post_view, methods=['POST'])
# Get
recipes_get_view = RecipesGetView.as_view('recipes_get_view')
recipe_blueprint.add_url_rule(base_url+'categories/<int:id>/recipes', view_func=recipes_get_view, methods=['GET'])
# Get by Id
recipes_id_get_view = RecipesIdGetView.as_view('recipes_id_get_view')
recipe_blueprint.add_url_rule(base_url+'categories/<int:category_id>/recipes/<int:recipe_id>', view_func=recipes_id_get_view, methods=['GET'])
# Put
recipes_put_view = RecipesPutView.as_view('recipes_put_view')
recipe_blueprint.add_url_rule(base_url+'categories/<int:category_id>/recipes/<int:recipe_id>', view_func=recipes_put_view, methods=['PUT'])
# Delete
recipes_delete_view = RecipeDeleteView.as_view('recipes_delete_view')
recipe_blueprint.add_url_rule(base_url+'categories/<int:category_id>/recipes/<int:recipe_id>', view_func=recipes_delete_view, methods=['DELETE'])