from sqlalchemy import asc, desc, or_

from extensions import db

class Recipe(db.Model):
    __tablename__ = 'recipe'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    num_of_servings = db.Column(db.Integer)
    cook_time = db.Column(db.Integer)
    directions = db.Column(db.String(1000))
    is_publish = db.Column(db.Boolean(), default=False)
    created_at = db.Column(db.DateTime(), nullable=False, 
                           server_default=db.func.now())
    updated_at = db.Column(db.DateTime(), nullable=False, 
                        server_default=db.func.now(), onupdate=db.func.now())
    cover_image = db.Column(db.String(100), default=None)
    user_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
        
    @classmethod
    def get_all_published(cls, q, page, per_page, sort, order):
        keyword = "%{}%".format(q)
        
        if order == 'desc':
            sort_logic = desc(getattr(cls, sort))
        else:
            sort_logic = asc(getattr(cls, sort))
            
            
        return cls.query.filter(
            or_(cls.name.ilike(keyword), cls.description.ilike(keyword)),
            cls.is_publish.is_(True)).order_by(
                sort_logic).paginate(page=page, per_page=per_page)
    
    @classmethod
    def get_by_id(cls, recipe_id):
        return cls.query.filter_by(id=recipe_id).first()
    
    @classmethod
    def get_all_by_user(cls, user_id, visibility='public'):
        
        """
        This method is used to filter the recipes a logged in user can see
        from an author. based on the user and the visibility assigned by the
        author.
        """
        if visibility == 'public':
            return cls.query.filter_by(user_id=user_id, is_publish=True)
        elif visibility == 'private':
            return cls.query.filter_by(user_id=user_id, is_publish=False)
        else:
            return cls.query.filter_by(user_id=user_id).all()
            
          
    def save(self):
        db.session.add(self)
        db.session.commit()
        
    def delete(self):
        db.session.delete(self)
        db.session.commit()