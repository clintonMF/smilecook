from flask import Flask
from flask_restful import Api

from resources.recipe import RecipeListResource, RecipeResource
from resources.recipe import RecipePublishResource

app = Flask(__name__)
api = Api(app) 

api.add_resource(RecipeListResource, "/recipes")
api.add_resource(RecipeResource, "/recipes/<int:recipe_id>")
api.add_resource(RecipePublishResource, "/recipes/<int:recipe_id>/publish")

if __name__=='__main__':
    app.run(debug=True)
