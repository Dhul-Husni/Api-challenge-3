from datetime import timedelta, datetime

from werkzeug.security import generate_password_hash
import jwt

from iris import db
from .token_model import RevokedTokens


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

    @staticmethod
    def generate_token(user_id):
        """Generates a token for user authorization"""
        try:
            # setup a payload with an expiration date
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=24),
                'iat': datetime.utcnow(),
                'sub': user_id,
            }
            # create the byte string token using the payload and the secret key
            jwt_string = jwt.encode(payload, 'sir3n.sn@gmail.com', algorithm='HS256')
            return jwt_string
        except Exception as e:  # pragma: no cover
            return str(e)

    @staticmethod
    def decode_token(token):
        """Decodes the token from the authorization header"""
        revoked_token = RevokedTokens.query.filter_by(revoked_token=str(token)).first()
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
