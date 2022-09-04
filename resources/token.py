from flask import request
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from http import HTTPStatus

from utils import verify_password
from models.user import User

class TokenResource(Resource):
    
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = User.get_by_email(email)
        
        if not user or not verify_password(password, user.password):
            return {
                "message": "email or password is incorrect"
                }, HTTPStatus.UNAUTHORIZED
        access_token = create_access_token(identity=user.id)
        
        return {"access_token": access_token}, HTTPStatus.OK

