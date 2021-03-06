import os

from . import auth_blueprint
from flask.views import MethodView
from flasgger import swag_from

from flask import Flask
from flask_mail import Mail
from flask_mail import Message
from flask import make_response, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from Iris.models.user_model import User
from Iris.models.token_model import RevokedTokens

from Iris.handlers import auth_handler

iris = Flask(__name__)
iris.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
iris.secret_key = os.environ.get('secret_key')
iris.config['MAIL_SERVER'] = 'smtp.gmail.com'
iris.config['MAIL_PORT'] = 465
iris.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
iris.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
iris.config['MAIL_USE_TLS'] = False
iris.config['MAIL_USE_SSL'] = True
mail = Mail(iris)


class RegistrationView(MethodView):
    """This class handles user registration"""
    @staticmethod
    @swag_from("docs/Register_user.yml", methods=['POST'])
    def post():
        """Handles post requests from this url /auth/register"""
        first_name, last_name, email, password, secret = auth_handler.assert_registration(request)
        existing_user = User.query.filter_by(email=email).first()  # checks if the user exists
        if existing_user:
            response = {'message': 'User already exists. Please login'}
            return make_response(jsonify(response)), 406
        else:
            user = User(email=email, password=password, first_name=first_name, last_name=last_name, secret=secret)
            user.save()
            response = {'message': 'You have successfully registered'}
            return make_response(jsonify(response)), 201


class LoginView(MethodView):
    """Handles user login"""
    @staticmethod
    @swag_from("docs/Login.yml", methods=['POST'])
    def post():
        """Handles post requests to this url /auth/login"""
        email, password = auth_handler.assert_login(request)
        user = User.query.filter_by(email=email).first()
        try:
            login = bool(user and check_password_hash(user.password_hash, password))
            if not login:
                raise ValueError
        except (ValueError, AttributeError):
            response = {'message': 'Incorrect Email or Password'}
            return make_response(jsonify(response)), 401
        else:
            access_token = user.generate_token(user.id)
            response = {'message': 'You have successfully logged in',
                        "Access token": access_token.decode(),
                        'email': email}
            return make_response(jsonify(response)), 200


class LogoutView(MethodView):
    """Handles user logout"""
    @staticmethod
    @swag_from("docs/Logout.yml", methods=['POST'])
    def post():
        # Get the access token from the header
        access_token = request.headers.get('Authorization')
        if not access_token:
            return make_response(jsonify({"message": "Please Provide an access token"})), 499
        revoked_token = RevokedTokens(revoked_token=access_token)
        revoked_token.save()
        response = {"message": "You have successfully logged out"}
        return make_response(jsonify(response)), 200


class ResetPasswordView(MethodView):
    """Handles reset password"""
    @staticmethod
    @swag_from("docs/Reset_password.yml", methods=['POST'])
    def post():
        email, secret, password = auth_handler.assert_reset(request)
        user = User.query.filter_by(email=email).first()
        try:
            reset = bool(user and user.secret == secret or secret == 'send me an email')
            if not reset:
                raise ValueError
            if reset and secret == 'send me an email':
                msg = 'Yummy Api Password reset. '
                msg = Message(msg, sender='sir3n.sn@gmail.com', recipients=[email])
                msg.html = '<b>Hi. Its siren from Api recipes. </b> <p>Your Secret word is '+str(user.secret)\
                           + '</p>' + '<p>Please use it to reset your password.\
                           </p> <p>If you did not request for this message please ignore</p>'
                mail.send(msg)
                response = {"message": "A reset value has been sent with instructions via the email provided."}
                return make_response(jsonify(response)), 200
        except (ValueError, AttributeError):
            raise auth_handler.InvalidSecretKey
        else:
            user.password = password
            user.save()
            response = {"message": "Password updated successfully"}
            return make_response(jsonify(response)), 201


base_url = '/v2/auth/'
registration_view = RegistrationView.as_view('register_view')
login_view = LoginView.as_view('login_view')
# Define the rule for the registration url > /auth/login
# Add the rule to the blueprint
auth_blueprint.add_url_rule(base_url+'register', view_func=registration_view, methods=['POST'])
auth_blueprint.add_url_rule(base_url+'login', view_func=login_view, methods=['POST'])

logout_view = LogoutView.as_view('logout_view')
auth_blueprint.add_url_rule(base_url+'logout', view_func=logout_view, methods=['POST'])

reset_password_view = ResetPasswordView.as_view('reset_view')
auth_blueprint.add_url_rule(base_url+'reset-password', view_func=reset_password_view, methods=['POST'])
