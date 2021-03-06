# api/recipes/recipes_view.py

import uuid
import jwt

from flask import Blueprint, request, make_response, jsonify, json, abort
from flask.views import MethodView
from flasgger import swag_from

from api import app, bcrypt, db
from api.models import RecipeCategory, Recipe, BlacklistToken
from api.auth.views import login_token_required
from api.auth.helpers import (
    is_valid, recipe_key_missing_in_body, key_is_not_string
)

recipes_blueprint = Blueprint('recipes', __name__)


class RecipeAPI(MethodView):
    """
    Recipe Resource
    """

    decorators = [login_token_required]

    @swag_from('swagger_docs/recipe_post.yaml', methods=['POST'])
    def post(self, current_user, cat_id):
        auth_header = request.headers['Authorization']
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ""
        if auth_token:
            resp = current_user.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                if not cat_id.isdigit():
                    responseObject = {
                        'error': 'Category ID must be an integer',
                        'status': "fail"
                    }
                    return make_response(jsonify(responseObject)), 400
                category = RecipeCategory.query.filter_by(id=cat_id, 
                                                  user_id=\
                                                  current_user.id).\
                                                  first()
                if not category:
                    responseObject = {
                        'message': 'Category not found in database'
                    }
                    return make_response(jsonify(responseObject)), 404
                if not request.get_json(force=True):
                    abort(400)
                data = request.get_json(force=True)
                if data:
                    recipe_key_missing_in_body(data)
                    if key_is_not_string(data):
                        response_object = {
                            'error': 'Bad request, body field must be of type string'
                        }
                        return jsonify(response_object), 400
                    if data['name'] == "" or data["description"] == "" \
                       or data['ingredients'] == "" or data['directions'] == "":
                        responseObject = {
                            'status': 'fail',
                            'message': 'field names not provided'
                        }
                        return make_response(
                            jsonify(responseObject)), 200
                    if Recipe.query.filter_by(name=' '.join(data['name'].split()).capitalize(), 
                                      cat_id=cat_id,
                                      user_id=current_user.id).\
                                      first():
                        responseObject = {
                            'status': 'fail',
                            'message': 'Recipe already exists'
                        }
                        return make_response(
                            jsonify(responseObject)), 202
                    recipe = Recipe(name=' '.join(data['name'].split()).capitalize(), 
                            cat_id=cat_id, 
                            user_id=current_user.id,
                            ingredients=data['ingredients'],
                            description=data['description'],
                            directions=data['directions'])
                    recipe.save()
                    responseObject = {
                        'status': 'success',
                        'message': 'New recipe added to category'
                    }
                    return make_response(jsonify(responseObject)), 201
                else:
                    responseObject = {
                        'status': 'fail',
                        'message': 'New recipe not created!'
                    }
                    return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                        'status': 'fail',
                        'message': resp
                    }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403
    
    @swag_from('swagger_docs/recipes.yaml', methods=['GET'])
    def get(self, current_user, cat_id):
        auth_header = request.headers['Authorization']
        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ""
        if auth_token:
            resp = current_user.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                if not cat_id.isdigit():
                    responseObject = {
                        'error': 'Category ID must be an integer',
                        'status': "fail"
                    }
                    return make_response(jsonify(responseObject)), 400
                category = RecipeCategory.query.filter_by(id=cat_id, 
                                                  user_id=\
                                                  current_user.id).\
                                                  first()
                if not category:
                    responseObject = {
                        'message': 'Category not found in database'
                    }
                    return make_response(jsonify(responseObject)), 404
                '''Returns recipes of current logged in user'''
                # recipes = Recipe.query.filter_by(cat_id=cat_id, user_id=current_user.id).all()
                # pagination
                limit = request.args.get('limit', 4)
                page = request.args.get('page', 1)
                if limit and page:
                    try:
                        limit = int(limit)
                        page = int(page)
                    except ValueError:
                        return make_response(jsonify({'message':
                            'limit and page query parameters should be integers'})), 400
                recipes = Recipe.query.filter_by(cat_id=cat_id, user_id=\
                                                 current_user.id).paginate(
                                                 page=page, per_page=limit, 
                                                 error_out=False
                                                )
                total_items = recipes.total
                total_pages = recipes.pages
                current_page = recipes.page
                items_per_page = recipes.per_page
                prev_page = ''
                next_page = ''

                if recipes.has_prev:
                    prev_page = recipes.prev_num
                if recipes.has_next:
                    next_page = recipes.next_num
            
                recipes = recipes.items

                recipe_list = []
                for recipe in recipes:
                    recipe_data = {}
                    recipe_data['id'] = recipe.id
                    recipe_data['cat_id'] = recipe.cat_id
                    recipe_data['user_id'] = recipe.user_id
                    recipe_data['name'] = recipe.name
                    recipe_data['ingredients'] = recipe.ingredients
                    recipe_data['description'] = recipe.description
                    recipe_data['directions'] = recipe.directions
                    recipe_list.append(recipe_data)
                    
                responseObject = {
                    'status': 'sucess',
                    'next_page': next_page,
                    'previous_page': prev_page,
                    'total_count': total_items,
                    'pages': total_pages,
                    'current_page': current_page,
                    'per_page': items_per_page,
                    'recipes_in_category': recipe_list
                }
                return make_response(jsonify(responseObject)), 200
            else:
                responseObject = {
                    'status': 'fail',
                    'message': resp
                }
                return make_response(jsonify(responseObject)), 401
        else:
            responseObject = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return make_response(jsonify(responseObject)), 403

# define the API resources
recipe_view = RecipeAPI.as_view('recipe_api')

# add rules for the API endpoints
recipes_blueprint.add_url_rule(
    '/recipe_category/<cat_id>/recipes',
    view_func=recipe_view,
    methods=['GET', 'POST']
)
