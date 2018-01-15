from iris import db
from .user_model import User


class RecipeCategory(db.Model):
    """ORM table to store recipe category
    """
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    detail = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))
    recipes = db.relationship('Recipes', backref='belonging_to', cascade="all, delete-orphan", lazy='dynamic')
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):  # pragma: no cover
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Categories:{}>".format(self.name)
