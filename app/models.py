from app import db
from werkzeug.security import generate_password_hash
from datetime import timedelta, datetime
import jwt

class User(db.Model):
    """Represents the user table
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True, index=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    secret = db.Column(db.String(128), nullable=False)
    password_hash = db.Column(db.String(128))
    category = db.relationship('RecipeCategory', order_by='RecipeCategory.id', cascade="all, delete-orphan")
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    @property
    def password(self):
        return AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):  # pragma: no cover
        db.session.delete(self)
        db.session.commit()

    def generate_token(self, user_id):
        """Generates a token for user authorization"""
        try:
            # setup a payload with an expiration date
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow(),
                'sub': user_id,
            }
            # create the byte string token using the token and the secret key
            jwt_string = jwt.encode(payload, 'sir3n.sn@gmail.com', algorithm='HS256')
            return jwt_string
        except Exception as e:  # pragma: no cover
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the token from the authorization header"""
        revoked_token = RevokeToken.query.filter_by(revoked_token=str(token)).first()
        if not revoked_token:
            try:
                # try to decode the token from our secret variable
                payload = jwt.decode(token, 'sir3n.sn@gmail.com')
                return payload['sub']
            except jwt.ExpiredSignatureError:
                return 'Expired token. Please log in to get a new token'
            except jwt.InvalidTokenError:
                return "Invalid token. Please register or log in"
        else:
            return "Invalid token provided. Please login"

    def __repr__(self):
        return "<User:{}>".format(self.first_name)


class RecipeCategory(db.Model):
    """Table for info on the recipe categories
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


class RevokeToken(db.Model):
    """This function revokes a token"""
    __tablename__ = 'revoked_tokens'
    id = db.Column(db.Integer, primary_key=True)
    revoked_token = db.Column(db.Text)

    def save(self): # pragma: no cover
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return "<Revoked token: {}".format(self.revoked_tokens)