import http
from flask import request, url_for, render_template
from flask_restful import Resource
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from marshmallow import ValidationError
from dotenv import load_dotenv
import os


from webargs import fields
from webargs.flaskparser import use_kwargs

from schema.user import UserSchema
from schema.recipe import RecipeSchema, RecipePaginationSchema
from models.user import User
from models.recipe import Recipe
from mailgun import MailgunApi
from utils import generate_token, verify_token, save_image
from extensions import image_set

user_schema = UserSchema()
user_schema_public = UserSchema(exclude=('email',))
user_schema_avatar = UserSchema(only=('avatar_image',))
# exclude=('email',) is used to prevent the email details from being passed
recipe_list_schema = RecipeSchema(many=True)
recipe_pagination_schema = RecipePaginationSchema()
load_dotenv()

mailgun = MailgunApi(os.getenv("MAILGUN_DOMAIN"),'MAILGUN_API_KEY')


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
        token = generate_token(user.email, salt='activate')
        subject = 'Please confirm your registration'
        link = url_for('useractivateresource',token=token,_external=True)
        text = "Hi! thanks for using smilecook, please confirm your registration by clicking on the link: {}".format(link)
        
        mailgun.send_email(to=user.email, subject=subject, text=text,
                    html=render_template('confirmation.html', link=link))
        
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
    @use_kwargs({
        'visibility': fields.String(missing='public'),
        'q': fields.String(missing=''),
        'page': fields.Int(missing=1),
        'per_page': fields.Int(missing=10),
        'sort': fields.String(missing='created_at'),
        'order': fields.String(missing='desc')
        }, location = "query")
    def get(self, username, visibility, q, page, per_page, sort, order):
        user = User.get_by_username(username)
        
        if user == None:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        
        current_user = get_jwt_identity()
        if current_user == user.id and visibility in ['all', 'private']:
            pass
        else:
            visibility = 'public'
            
        if sort not in ['created_at', 'cook_time', 'num_of_servings']:
            sort = 'created_at'
        if order not in ['asc', 'desc']:
            order = 'desc'
            
        recipe = Recipe.get_all_by_user(q, page, per_page, sort, order, user_id=user.id, visibility=visibility)
        
        return recipe_pagination_schema.dump(recipe), HTTPStatus.OK
    
class UserActivateResource(Resource):
    """This class is used to activate the user account through the email 
    using the activation link sent in the email"""
    
    def get(self, token):
        email = verify_token(token, salt='activate')
        if email is False:
            return {
                "message": "Invalid token or token expired"
            }, HTTPStatus.BAD_REQUEST
        
        user = User.get_by_email(email=email)
        if not user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        if user.is_active:
            return {
                "message": "This user account has been activated"
                }, HTTPStatus.BAD_REQUEST
        
        user.is_active = True
        user.save()
        
        return {}, HTTPStatus.NO_CONTENT
    
class UserAvatarUploadResource(Resource):
    
    @jwt_required()
    def put(self):
        file = request.files.get('avatar')
        
        if not file:
            return {"message": "Not a valid image"}, HTTPStatus.BAD_REQUEST
        
        if not image_set.file_allowed(file, file.filename):
            return {"message": "file type not allowed"}, HTTPStatus.BAD_REQUEST
        
        user = User.get_by_id(get_jwt_identity())
        
        if user.avatar_image:
            avatar_path = image_set.path(folder='avatars',
                                         filename=user.avatar_image)
            if os.path.exists(avatar_path):
                os.remove(avatar_path)
                
        filename = save_image(file, 'avatars')
        user.avatar_image = filename
        user.save()
            
        return user_schema_avatar.dump(user), HTTPStatus.OK
    