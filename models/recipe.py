recipe_list = []
# the recipe list is used to store data in the system memory

def get_last_id():
    if recipe_list:
        last_recipe = recipe_list[-1]
    else:
        return 1
    return last_recipe.id + 1


class Recipe():
    
    def __init__(self, name, description, num_of_servings, cook_time, 
                 directions):
        self.id = get_last_id()
        self.name = name
        self.description = description
        self.num_of_servings = num_of_servings
        self.cook_time = cook_time
        self.directions = directions
        self.is_publish = False
        
    # the property decorator is used  to give "special" functionality to
    # certain methods to make them act as getters, setters, or deleters 
    # when we define properties in a class
    @property 
    def data(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.directions,
            "num_of_servings": self.num_of_servings,
            "cook_time": self.cook_time,
            "directions": self.directions
        }