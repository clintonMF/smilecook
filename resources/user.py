from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from marshmallow import ValidationError

from schema.user import UserSchema

from models.user import User

user_schema = UserSchema()
user_schema_public = UserSchema(exclude=('email',))


class UserListResource(Resource):
    
    def post(self):
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
    
    @jwt_required(optional=True)
    def get(self, username):
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
    
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.get_by_id(id=current_user)
        
        return user_schema.dump(user).data , HTTPStatus.OK