import http
from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from marshmallow import ValidationError

from webargs import fields
from webargs.flaskparser import use_kwargs

from schema.user import UserSchema
from schema.recipe import RecipeSchema
from models.user import User
from models.recipe import Recipe

user_schema = UserSchema()
user_schema_public = UserSchema(exclude=('email',))
# exclude=('email',) is used to prevent the email details from being passed
recipe_list_schema = RecipeSchema(many=True)


class UserListResource(Resource):
    """
    This class holds the logic for the "/users" endpoint
    """
    def post(self):
        """This function is used to create a new user"""
        json_data = request.get_json()
        
        try:
            data = user_schema.load(json_data)
        except ValidationError as err:
            return {
                "message": "Validation error",
                "errors": err.messages
                }, HTTPStatus.BAD_REQUEST
        
        
        username = data.get('username')
        email = data.get('email')
        
        if User.get_by_username(username):
            return {"message":"this username exists"}, HTTPStatus.BAD_REQUEST

        if User.get_by_email(email):
            return {"message":"this email exists"}, HTTPStatus.BAD_REQUEST
        
        user = User(**data)
        
        user.save()
        
        return user_schema.dump(user), HTTPStatus.CREATED

class UserResource(Resource):
    """
    This class holds the logic for the "/users/<string:username>" endpoint
    """
    @jwt_required(optional=True)
    def get(self, username):
        """
        This function is used to get user information
        The information returned varies by users i.e nore information is given
        to the actual user, while less is given to others.
        """
        user = User.get_by_username(username)
        
        if not user:
            return {"message": "user not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        
        if current_user == user.id:
            data = user_schema.dump(user)
        else:
            data = user_schema_public.dump(user)

        
        return data, HTTPStatus.OK
    

class MeResource(Resource):
    """
    This class holds the logic for the "/me" endpoint
    """
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.get_by_id(id=current_user)
        
        return user_schema.dump(user).data , HTTPStatus.OK
    
    
class UserRecipeListResource(Resource):
    """
    This class holds the logic for the "/users/<string:username>/recipes" 
    endpoint
    """
    #the @use_kwargs line of code is used to specify that we expect to 
    # receive query parameter visibility. 
    @jwt_required(optional=True)
    @use_kwargs({'visibility': fields.Str()},  location="query")
    def get(self, username, visibility):
        user = User.get_by_username(username)
        
        if user == None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'
        recipe = Recipe.get_all_by_user(user_id=user.id, visibility=visibility)
        
        return recipe_list_schema.dump(recipe), HTTPStatus.OK