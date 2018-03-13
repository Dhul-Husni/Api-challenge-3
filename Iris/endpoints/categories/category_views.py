from flask.views import MethodView
from flask import make_response, request, jsonify
from flasgger import swag_from
from . import category_blueprint
from Iris.models.category_model import RecipeCategory
from Iris.handlers.token_handler import assert_token
from Iris.handlers.category_handler import assert_category
from Iris.handlers.pagination_handler import assert_pagination


class CategoryPostView(MethodView):
    """This class handles requests on category endpoint
    """
    @staticmethod
    @swag_from("docs/Categories_post.yml", methods=['POST'])
    def post():
        """
        Handles url route /api-2.0/categories with method post
        :return: 201 created
        """
        user_id = assert_token(request)
        name, detail = assert_category(request)
        check_category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(name=name).first()
        if not check_category:
            my_category = RecipeCategory(name=name, detail=detail, created_by=user_id)
            my_category.save()
            response = jsonify({
                "Category Id": my_category.id,
                "Recipe Category Name": my_category.name.title(),
                "Recipe Category Detail": my_category.detail.title(),
                "Date Created": my_category.date_created,
                "Date Modified": my_category.date_modified
            })
            return make_response(response), 201
        else:
            response = jsonify({'message': 'Category already exists'})
            return make_response(response), 400

class CategoryGetView(MethodView):
    """
    Handles get on endpoint /categories
    :returns: 200 <ok>
    """
    @staticmethod
    @swag_from("docs/Categories_get.yml", methods=['GET'])
    def get():
        user_id = assert_token(request)
        page, per_page = assert_pagination(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).order_by(RecipeCategory.id)\
            .paginate(page=page, per_page=per_page)
        result = []
        for each_category in category.items:
            obj = {
                "id": each_category.id,
                "Recipe Category Name": each_category.name.title(),
                "Recipe Category Detail": each_category.detail.title(),
                "Date Created": each_category.date_created,
                "Date Modified": each_category.date_modified
            }
            result.append(obj)
        if not result:  # if the result is empty
            result.append("Nothing here yet")
        response = jsonify({'Next page': category.next_num,
                            'Prev page': category.prev_num,
                            'Has next': category.has_next,
                            'Has prev': category.has_prev,
                            'current page': category.page,
                            'total items': category.total,
                            'total pages': category.pages,
                            }, result)
        return make_response(response), 200


class CategoryIdGetView(MethodView):
    """
    Handles get on endpoint /categories/<id>
    :returns: 200 <ok>
    """
    @staticmethod
    @swag_from("docs/Category_id_get.yml", methods=['GET'])
    def get(id):
        # retrieve a category by it's id
        user_id = assert_token(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        if category:
            response = jsonify({
                    "id": category.id,
                    "Recipe Category Name": category.name.title(),
                    "Recipe Category Detail": category.detail.title(),
                    "Date Created": category.date_created,
                    "Date Modified": category.date_modified
                })
            return make_response(response), 200
        return make_response(jsonify({"message": "The category does not exist, Would you like to create one?"})), 404


class CategoryPutView(MethodView):
    """
    Handles put on endpoint /categories
    :returns: 200 <0k>
    """
    @staticmethod
    @swag_from("docs/Categories_id_edit.yml", methods=['PUT'])
    def put(id):
        user_id = assert_token(request)
        name, detail = assert_category(request)
        edit_category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        if edit_category:
            name_exists = RecipeCategory.query.filter_by(created_by=user_id).filter_by(name=name).first()
            same_names = bool(edit_category.name == name_exists.name) if name_exists else False
            if not name_exists or same_names:
                edit_category.name = name
                edit_category.detail = detail
                edit_category.save()
                response = jsonify({
                    "id": edit_category.id,
                    "Recipe Category Name": edit_category.name.title(),
                    "Recipe Category Detail": edit_category.detail.title(),
                    "Date Created": edit_category.date_created,
                    "Date Modified": edit_category.date_modified

                })
                return make_response(response), 200
            response = jsonify({'message': 'Category already exists'})
            return make_response(response), 400

        else:
            # abort early with an error four oh four if not in found
            return make_response(jsonify({"message": "The category does not exist, Would you like to create one?"})), 404


class CategoryDeleteView(MethodView):

    @staticmethod
    @swag_from("docs/Categories_id_delete.yml", methods=['DELETE'])
    def delete(id):
        user_id = assert_token(request)
        category = RecipeCategory.query.filter_by(created_by=user_id).filter_by(id=id).first()
        if category:
            category.delete()
            return make_response(jsonify({
                       "message": 'Category {} was deleted successfully'.format(category.id)

                   })), 200
        else:
            # abort early with an error four oh four if not in found
            return make_response(jsonify({"message": "The category does not exist, Would you like to create one?"})), 404


base_url = '/v2/'
# Post
category_post_view = CategoryPostView.as_view('category_post_view')
category_blueprint.add_url_rule(base_url+'categories', view_func=category_post_view, methods=['POST'])
# Get
category_get_view = CategoryGetView.as_view('category_get_view')
category_blueprint.add_url_rule(base_url+'categories', view_func=category_get_view, methods=['GET'])
# Get by Id
category_id_get_view = CategoryIdGetView.as_view('category_id_get_view')
category_blueprint.add_url_rule(base_url+'categories/<int:id>', view_func=category_id_get_view, methods=['GET'])
# Put
category_put_view = CategoryPutView.as_view('category_put_view')
category_blueprint.add_url_rule(base_url+'categories/<int:id>', view_func=category_put_view, methods=['PUT'])
# Delete
category_delete_view = CategoryDeleteView.as_view('category_delete_view')
category_blueprint.add_url_rule(base_url+'categories/<int:id>', view_func=category_delete_view, methods=['DELETE'])


