import os
from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from webargs import fields
from webargs.flaskparser import use_kwargs

from models.recipe import Recipe
from schema.recipe import RecipeSchema, RecipePaginationSchema
from utils import save_image
from extensions import image_set


recipe_schema = RecipeSchema()
recipe_pagination_schema = RecipePaginationSchema()
recipe_list_schema = RecipeSchema(many=True) 
recipe_cover_schema = RecipeSchema(only=('cover_image',))
# many = True is used to let the serializer (the @post_dump(pass_many)
# decorator) know that several objects would be passed.


class RecipeListResource(Resource):
    """
    This class holds the logic for the "/recipes" endpoint
    """
    
    @use_kwargs({
        'page': fields.Int(missing=1),
        'per_page': fields.Int(missing=10),
        }, location = "query")
    def get(self, page, per_page):
        
        recipes = Recipe.get_all_published(page, per_page)
        print(page)
        print(recipe_pagination_schema.dump(recipes))
        return recipe_pagination_schema.dump(recipes), HTTPStatus.OK
    @jwt_required()
    def post(self):
        json_data = request.get_json()
        current_user = get_jwt_identity()
        try:
            data = recipe_schema.load(json_data)
        except ValidationError as err:
            return {
                "message": "Validation error",
                "errors": err.messages
                }, HTTPStatus.BAD_REQUEST
            
        
        recipe = Recipe(**data)
        recipe.user_id = current_user
        
        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.CREATED
    
class RecipeResource(Resource):
    """
    This class holds the logic for the "/recipes/<recipe_id" endpoint
    """
    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id or recipe.is_publish == False:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        return recipe_schema.dump(recipe), HTTPStatus.OK
    
    @jwt_required()
    def patch(self, recipe_id):
        json_data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id)
        
        try:
            data = recipe_schema.load(
                json_data, partial=('name','description', 'directions'))
        except ValidationError as err:
            return {
                "messages":"validation error",
                "errors": err.messages
                }, HTTPStatus.BAD_REQUEST
        
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.FORBIDDEN
        
        recipe.name = data.get("name") or recipe.name
        recipe.description = data.get('description') or recipe.description
        recipe.num_of_servings = data.get('num_of_servings') or recipe.num_of_servings
        recipe.cook_time = data.get('cook_time') or recipe.cook_time
        recipe.directions = data.get('directions') or recipe.directions
        
        recipe.save()
        return recipe_schema.dump(recipe), HTTPStatus.OK
    
    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        recipe.delete()
        
        return {}, HTTPStatus.NO_CONTENT
        
    
class RecipePublishResource(Resource):
    """
    This class holds the logic for the "/recipes/<int:recipe_id>/publish"
    endpoint.
    """
    
    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        recipe.is_publish = True
        recipe.save()
        
        return {}, HTTPStatus.NO_CONTENT
    
    @jwt_required()
    def delete(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        recipe.is_publish = False
        recipe.save()
        return {}, HTTPStatus.NO_CONTENT
    
class RecipeCoverUploadResource(Resource):
    
    @jwt_required()
    def put(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        file = request.files.get('cover')
        
        if not file:
            return {"message": "Not a valid image"}, HTTPStatus.BAD_REQUEST
        
        if not image_set.file_allowed(file, file.filename):
            return {"message": "file type not allowed"}, HTTPStatus.BAD_REQUEST
        

        
        if recipe.cover_image:
            cover_path = image_set.path(folder='covers',
                                         filename=recipe.cover_image)
            if os.path.exists(cover_path):
                os.remove(cover_path)
                
        filename = save_image(file, 'covers')
        recipe.cover_image = filename
        recipe.save()
            
        return recipe_cover_schema.dump(recipe), HTTPStatus.OK
    
        