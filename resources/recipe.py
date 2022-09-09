from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.recipe import Recipe
from schema.recipe import RecipeSchema
from marshmallow import ValidationError

recipe_schema = RecipeSchema()
recipe_list_schema = RecipeSchema(many=True)

class RecipeListResource(Resource):
    
    def get(self):
        recipes = Recipe.get_all_published()
        
        return recipe_list_schema.dump(recipes), HTTPStatus.OK
    
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
    
    @jwt_required(optional=True)
    def get(self, recipe_id):
        recipe = Recipe.get_by_id(recipe_id)
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()

        if current_user != recipe.user_id or recipe.is_publish == False:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        return recipe.data(), HTTPStatus.OK
    
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
    
        
        
        
        