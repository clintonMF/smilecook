from flask import request
from flask_restful import Resource
from http import HTTPStatus
from flask_jwt_extended import get_jwt_identity, jwt_required

from models.recipe import Recipe

class RecipeListResource(Resource):
    
    def get(self):
        recipe_list = Recipe.get_all_published()
        data = []
        
        for recipe in recipe_list:
            data.append(recipe.data())
        
        return {"data": data}, HTTPStatus.OK
    
    @jwt_required()
    def post(self):
        data = request.get_json()
        current_user = get_jwt_identity()
        recipe = Recipe(name=data["name"],
                        description=data['description'],
                        num_of_servings=data['num_of_servings'],
                        cook_time=data['cook_time'],
                        directions=data['directions'],
                        user_id=current_user)
        
        recipe.save()
        return recipe.data(), HTTPStatus.CREATED
    
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
    def put(self, recipe_id):
        data = request.get_json()
        recipe = Recipe.get_by_id(recipe_id)
        
        if recipe is None:
            return {"message": "recipe not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        
        if current_user != recipe.user_id:
            return {"message": "Access not allowed"}, HTTPStatus.UNAUTHORIZED
        
        
        recipe.name = data["name"]
        recipe.description = data['description']
        recipe.num_of_servings = data['num_of_servings']
        recipe.cook_time = data['cook_time']
        recipe.directions = data['directions']
        
        recipe.save()
        return recipe.data(), HTTPStatus.OK
    
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
    
        
        
        
        