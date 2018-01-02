from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify, request
from instance.config import app_config
from flask import redirect
from flasgger import Swagger
from flasgger import swag_from
from flask_heroku import Heroku
# initialize SQLAlchemy
db = SQLAlchemy()


def create_app(config_name):
    from app.models import User
    from app.models import Recipes
    from app.models import RecipeCategory

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    app.secret_key = 'Sir3n.sn@gmail.com'
    app.config['SWAGGER'] = {
        "swagger": "2.0",
        "title": "Recipes API",
        "description": "Powered by Flask! \
        \nRestful api that gives users power to:\
        \nRegister, login and manage their account. \
        \n\tCreate, update, view and delete a category. \
        \n\tAdd, update, view or delete recipes. \
        \n\tEnable logging of data manipulation timestamps. ",
        "termsOfService": "https://opensource.org/ToS",
        "version": "0.0.1",
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
        "host": "api-recipe-challenge.herokuapp.com",
        "securityDefinitions":{
            "TokenHeader":{
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
    Swagger(app)  # This creates a swagger ui documentation
    Heroku(app)
    # The views for the application

    @app.route('/')
    def index():  # pragma: no cover
        return redirect('apidocs')

    @swag_from('docs/Categories_get.yml', methods=['GET'])
    @swag_from('docs/Categories_post.yml', methods=['POST'])
    @app.route('/api-1.0/categories', methods=['GET', 'POST'])
    def categories():
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please Provide an access token"}, 300
        if access_token:
            # Attempt to decode and the user id
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                #  Go ahead and process the request
                if request.method == 'POST':
                    name = str(request.data.get('name', '')).strip().lower()
                    detail = str(request.data.get('detail', '')).strip().lower()
                    if name and detail:
                        # checks if the category posted already exists with the user
                        check_category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(name=name).first()
                        if not check_category:
                            category = RecipeCategory(name=name, detail=detail, created_by=user_id)
                            category.save()
                            response = jsonify({
                                                "id": category.id,
                                                "Recipe Category Name": category.name.title(),
                                                "Recipe Category Detail": category.detail.title(),
                                                "Date Created": category.date_created,
                                                "Date Modified": category.date_modified
                                                })
                            response.status_code = 201
                            return response
                        else:
                            response = jsonify({'Message': 'Category already exists'})
                            response.status_code = 409
                            return response
                    else:
                        response = jsonify({"Message": "please use keys name and detail"})
                        response.status_code = 203
                        return response
                else:
                    # GET
                    category = RecipeCategory.query.filter_by(created_by=user_id).paginate(page=page, per_page=per_page)
                    result = []
                    for each_category in category.items:
                        obj = {
                            "id": each_category.id,
                            "Recipe Category Name": each_category.name.title(),
                            "Recipe Category Detail": each_category.detail.title(),
                            "Date Created":  each_category.date_created,
                            "Date Modified": each_category.date_modified
                            }
                        result.append(obj)
                    response = jsonify({'Next page': category.next_num,
                                        'Prev page': category.prev_num,
                                        'Has next': category.has_next,
                                        'Has prev': category.has_prev,
                                        }, result)
                    if not result:  # if the result is empty
                        response = jsonify({'Next page': category.next_num,
                                            'Prev page': category.prev_num,
                                            'Has next': category.has_next,
                                            'Has prev': category.has_prev,
                                            }, {'Message': 'Nothing here yet'})
                    response.status_code = 200
                    return response
            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    @swag_from('docs/Category_id_get.yml', methods=['GET'])
    @swag_from('docs/Categories_id_delete.yml', methods=['DELETE'])
    @swag_from('docs/Categories_id_edit.yml', methods=['PUT'])
    @app.route('/api-1.0/categories/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def categories_manipulation(id):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please provide an access token"}, 300
        # retrieve a category by it's id
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
                if category:
                    if request.method == 'DELETE':
                        category.delete()
                        return {
                            "Message": 'Category {} was deleted successfully'.format(category.id)

                        }, 200

                    elif request.method == 'PUT':
                        name = str(request.data.get('name', '')).strip().lower()
                        detail = str(request.data.get('detail', '')).strip().lower()
                        if name and detail:
                            category.name = name
                            category.detail = detail
                            category.save()
                            response = jsonify({
                                                "id": category.id,
                                                "Recipe Category Name": category.name.title(),
                                                "Recipe Category Detail": category.detail.title(),
                                                "Date Created": category.date_created,
                                                "Date Modified": category.date_modified

                                                })
                            response.status_code = 200
                            return response
                        else:
                            response = jsonify({"Message": "Please use the keys name and detail"})
                            response.status_code = 203
                            return response
                    # Get
                    else:
                        response = jsonify({
                                            "id": category.id,
                                            "Recipe Category Name": category.name.title(),
                                            "Recipe Category Detail": category.detail.title(),
                                            "Date Created": category.date_created,
                                            "Date Modified": category.date_modified
                                            })
                        response.status_code = 200
                        return response
                else:
                    # abort early with an error four oh four if not in found
                    return {"Message": "The category does not exist, Would you like to create one?"}, 404
            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    @swag_from('docs/Categories_search_get.yml', methods=['GET'])
    @app.route('/api-1.0/categories/search', methods=['GET'])
    def search_item():
        """This searches the category for items with similar or equal names to the get
        parameter q"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please provide an access token"}, 300
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                q = request.values.get('q', '').strip().lower()
                if q:
                    search_result = RecipeCategory.query.filter_by(created_by=user_id).paginate(page=page, per_page=per_page)
                    # GET
                    result = []
                    for each_category in search_result.items:
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
                        message = {"Message": "Sorry we could not find what you are looking for"}, 403
                        result.append(message)
                    response = jsonify({'Next Page': search_result.next_num,
                                        'Prev Page': search_result.prev_num,
                                        'Has next':  search_result.has_next,
                                        'Has previous': search_result.has_prev}, result)
                    response.status_code = 200
                    return response

                else:
                    message = {"Message": "Please provide a search query"}
                    response = jsonify(message)
                    response.status_code = 404
                    return response

            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    @swag_from('docs/Recipes_get.yml', methods=['GET'])
    @swag_from('docs/Recipes_post.yml', methods=['POST'])
    @app.route('/api-1.0/categories/<int:id>/recipes', methods=['GET', 'POST'])
    def recipes(id):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please provide an access token"}, 300
        result = []
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                if category:
                    if request.method == 'GET':
                        if category.recipes:
                            recipe_object = category.recipes.paginate(page=page, per_page=per_page)
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
                                response = jsonify({'Next Page': recipe_object.next_num,
                                                    'Prev Page': recipe_object.prev_num,
                                                    'Has next': recipe_object.has_next,
                                                    'Has previous': recipe_object.has_prev},
                                                   {"Message": "Nothing here yet"})
                                response.status_code = 200
                                return response
                            else:
                                response = jsonify({'Next Page': recipe_object.next_num,
                                                    'Prev Page': recipe_object.prev_num,
                                                    'Has next': recipe_object.has_next,
                                                    'Has previous': recipe_object.has_prev}, result)
                                response.status_code = 200
                                return response
                    elif request.method == 'POST':
                        name = request.data.get('name', '').strip().lower()
                        recipe = request.data.get('recipe', '').strip().lower()
                        if name and recipe:
                            the_recipes = Recipes(name=name, recipe=recipe, belonging_to=category)
                            the_recipes.save()
                            for recipe in category.recipes.all():
                                obj = {
                                        "id": recipe.id,
                                        "name": recipe.name.title(),
                                        "Recipe": recipe.recipe.title(),
                                        "Date created": recipe.date_created,
                                        "Date modified": recipe.date_modified
                                        }
                                result.append(obj)
                                response = jsonify(result)
                                response.status_code = 201
                                return response
                        else:
                            return {"Message": "Please use keys name and recipe"}, 203
                else:
                    return {"Message": "Category does not exist"}, 405

            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    @swag_from('docs/Recipes_search_get.yml', methods=['GET'])
    @app.route('/api-1.0/categories/<int:id>/recipes/search', methods=['GET'])
    def search_recipe_item(id):
        """This searches the recipes for items with similar or equal names to the get
        parameter q"""
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please provide an access token"}, 300
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
                page = int(request.args.get('page', 1))
                per_page = int(request.args.get('per_page', 20))
                if category:
                    if category.recipes:
                        q = request.values.get('q', '').strip().lower()
                        if q:
                            search_result = category.recipes.paginate(page=page, per_page=per_page)
                            # GET
                            result = []
                            for each_recipe in search_result.items:
                                if q in each_recipe.name or q in each_recipe.recipe:
                                    obj = {
                                        "id": each_recipe.id,
                                        "Name": each_recipe.name.title(),
                                        "Recipe": each_recipe.recipe.title(),
                                        "Date Created": each_recipe.date_created,
                                        "Date Modified": each_recipe.date_modified
                                    }
                                    result.append(obj)
                            if not result:
                                message = {"Message": "Sorry we could not find what you are looking for"}, 403
                                result.append(message)
                            response = jsonify({'Next Page': search_result.next_num,
                                                'Prev Page': search_result.prev_num,
                                                'Has next': search_result.has_next,
                                                'Has previous': search_result.has_prev}, result)
                            response.status_code = 200
                            return response

                        else:
                            message = {"Message": "Please provide a search query"}
                            response = jsonify(message)
                            response.status_code = 404
                            return response
                else:
                    # abort early with an error four oh four if not in found
                    return {"Message": "Category does not exist"}, 405
            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    @swag_from('docs/Recipe_id_get.yml', methods=['GET'])
    @swag_from('docs/Recipes_id_edit.yml', methods=['PUT'])
    @swag_from('docs/Recipes_id_delete.yml', methods=['DELETE'])
    @app.route("/api-1.0/categories/<int:val>/recipes/<int:res>", methods=['GET', 'PUT', 'DELETE'])
    def recipe_manipulation(val, res):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please provide and access token"}, 300
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=val).first()
                if category:
                    current_recipe = category.recipes.filter_by(id=res).all()  # Access the recipe related to the category
                    if current_recipe:
                        if request.method == 'DELETE':
                            for each_recipe in current_recipe:
                                each_recipe.delete()
                                return {
                                "Message": 'Recipe {} was deleted successfully'.format(res)

                                }, 200

                        elif request.method == 'PUT':
                            name = request.data.get('name', '').strip().lower()
                            recipe = request.data.get('recipe', '').strip().lower()
                            if name and recipe:
                                for the_recipe in current_recipe:
                                    the_recipe.name = name
                                    the_recipe.recipe = recipe
                                    the_recipe.save()
                                    response = jsonify({
                                                    "Recipe Name": the_recipe.name.title(),
                                                    "Recipe": the_recipe.recipe.title(),
                                                    "Date Created": the_recipe.date_created,
                                                    "Date Modified": the_recipe.date_modified,
                                                    })
                                    response.status_code = 201
                                    return response
                            else:
                                return {"Message": "name and recipe cannot be empty"}, 203

                        elif request.method == 'GET':
                            for the_recipe in current_recipe:
                                response = jsonify({
                                                    "Recipe Name": the_recipe.name.title(),
                                                    "Recipe": the_recipe.recipe.title(),
                                                    "Date Created": the_recipe.date_created,
                                                    "Date Modified": the_recipe.date_modified,
                                                    })
                                response.status_code = 200
                                return response
                    else:
                        return {"Message": "The recipe does not exist"}, 404
                else:
                    return {"Message": "The category does not exist"}, 405
            else:
                #  Token is not legit so return the error message
                message = user_id
                response = jsonify({"Message": message})
                response.status_code = 401
                return response

    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app
