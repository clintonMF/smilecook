from flask import url_for


from marshmallow import (
    Schema, fields, validate, validates, ValidationError, post_dump
    )
from schema.user import UserSchema
from schema.pagination import PaginationSchema

# the schema class are used for serialization and deserialization

def validate_number_of_servings(n):
    """This function validates the number of servings"""
    if n < 1:
        raise ValidationError(
            'Number of servings must be greater than 0')
    if n > 50:
        raise ValidationError(
            'Number of servings cannot be greater than 50')
            
class RecipeSchema(Schema):
    """
    This class is used to define valid data for the Recipe models
    """
    class Meta: ordered =True
    
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=[validate.Length(max=100)])
    description = fields.String(required=True, 
                                validate=[validate.Length(max=200)])
    directions = fields.String(required=True, 
                               validate=[validate.Length(max=1000)])
    is_published = fields.Boolean(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)    
    num_of_servings = fields.Method(validate=validate_number_of_servings)
    cook_time = fields.Integer()
    cover_image = fields.Method(serialize='dump_cover_url')
    
    @validates('cook_time')
    def validate_cook_time(self, value):
        # this function validates the cook time 
        # when validating the cook_time property this function is called 
        # because of the validates decorator
        if value < 1:
            raise ValidationError("cook time must be greater than 0 minutes")
        if value > 300:
            raise ValidationError("cook time must be greater than 300 minutes")
        
    author = fields.Nested(UserSchema, attribute='user',dump_only=True, 
                           only=['id', 'username'])
    
    def dump_cover_url(self, recipe):
        if recipe.cover_image:
            return url_for('static', 
                filename='images/covers/{}'.format(recipe.cover_image),
                _external = True)
        else:
            return url_for('static', 
                           filename='images/assets/default-cover.jpg',
                           _external = True)
        
    
    
    