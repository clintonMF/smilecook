from flask import request
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus

from utils import hash_password
from models.user import User


class UserListResource(Resource):
    
    def post(self):
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        non_hashed_password = data.get('password')
        
        if User.get_by_username(username):
            return {"message":"this username exists"}, 403

        if User.get_by_email(email):
            return {"message":"this email exists"}, 403
        
        password = hash_password(non_hashed_password)
        
        user = User(
            username = username,
            email = email,
            password = password
        )
        
        user.save()
        
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        
        return data, HTTPStatus.CREATED

class UserResource(Resource):
    
    @jwt_required(optional=True)
    def get(self, username):
        user = User.get_by_username(username)
        
        if not user:
            return {"message": "user not found"}, HTTPStatus.NOT_FOUND
        current_user = get_jwt_identity()
        
        if current_user == user.id:
            data = {
                "id": user.id,
                "email": user.email,
                "username": username
            }
        else:
            data = {
                "email": user.email,
                "username": username
            }
        
        return data, HTTPStatus.OK

class MeResource(Resource):
    
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.get_by_id(id=current_user)
        
        print(user)
        data = {
            "id": user.id,
            "email": user.email,
            "username": user.username
        }
        
        return data, HTTPStatus.OK