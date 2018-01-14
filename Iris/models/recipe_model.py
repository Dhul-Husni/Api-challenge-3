from Iris import db


class Recipes(db.Model):
    """Models the recipe table
    """
    __tablename__ = 'recipes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    recipe = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):  # pragma: no cover
        db.session.delete(self)
        db.session.commit()
        return "Success"

    def __repr__(self):
        return "<Recipe name:{} Recipe:{}>".format(self.name, self.recipe)
