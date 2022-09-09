from marshmallow import (
    Schema, fields, validate, validates, ValidationError, post_dump
    )
from schema.user import UserSchema

def validate_number_of_servings(n):
    if n < 1:
        raise ValidationError(
            'Number of servings must be greater than 0')
    if n > 50:
        raise ValidationError(
            'Number of servings cannot be greater than 50')
            
class RecipeSchema(Schema):
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
    
    @validates('cook_time')
    def validate_cook_time(self, value):
        if value < 1:
            raise ValidationError("cook time must be greater than 0 minutes")
        if value > 300:
            raise ValidationError("cook time must be greater than 300 minutes")
        
    author = fields.Nested(UserSchema, attribute='user',dump_only=True, 
                           only=['id', 'username'])
    
    @post_dump(pass_many=True)
    def wraps(self, data, many, **kwargs):
        if many:
            return {'data': data}
        else:
            return data
        
    
    
    