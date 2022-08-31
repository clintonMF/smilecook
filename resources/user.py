from flask import request
from flask_restful import Resource

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
        
        return data, 201