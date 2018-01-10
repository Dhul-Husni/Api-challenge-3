import re

from . import auth_blueprint
from flask.views import MethodView
from flask_mail import Mail
from flask_mail import Message
from app import create_app, validate_illegal_char
from flask import make_response, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app.models import RevokeToken, User
from flasgger import swag_from




config_name = "development"
app = create_app(config_name)
mail = Mail(app)


class RegistrationView(MethodView):
    """This class handles user registration"""
    @swag_from("docs/Register_user.yml", methods=['POST'])
    def post(self):
        """Handles post requests from this url /auth/register"""
        # Register the user
        try:
            email = request.data.get('email', '').strip().lower()
            password = request.data.get('password', '')
            first_name = request.data.get('First Name', '').strip().lower()
            last_name = request.data.get('Last Name', '').strip().lower()
            secret = request.data.get('Secret word', '').strip().lower()  # A way to help the user reset password
            if first_name and last_name and email and password and secret:
                if len(email) >=80 or len(first_name) >=80 or len(last_name) >= 80 or len(secret)  >= 80:
                    response = jsonify({
                        "Message": "Please use a shorter value"
                    })
                    response.status_code = 401
                    return response

                if validate_illegal_char(first_name+last_name):
                    response = jsonify({
                        "Message": "Fatal! illegal characters used"
                    })
                    response.status_code = 401
                    return response
                if re.match(r'^[a-zA-Z0-9_+.]+@[a-zA-z-]+\.[a-zA-Z-]+$', email):  # validate email
                    if len(password) >= 8:  # validate password
                        existing_user = User.query.filter_by(email=email).first()  # check if the user exists
                        if existing_user:
                            response = {'Message': 'User already exists. Please login'}
                            return make_response(jsonify(response)), 202
                        else:  # the user does not exist and should be registered
                            user = User(email=email, password=password, first_name=first_name, last_name=last_name, secret=secret)
                            user.save()
                            response = {'Message': 'You have successfully registered'}
                    else:
                        response = {'Message': 'Password must be greater than 8'}
                else:
                    response = {'Message': 'Please provide a valid email'}
                return make_response(jsonify(response)), 201
            else:
                response = {"Message": "Please fill out First Name, Last Name, email, password and Secret word (Case Sensitive)"}
                return make_response(jsonify(response)), 203
        except Exception as e:  #pragma: no cover
            # if error occured returns the error as a message
            return {'Message': str(e)}, 401


class LoginView(MethodView):
    """Handles user login"""
    @swag_from("docs/Login.yml", methods=['POST'])
    def post(self):
        """Handles post requests to this url /auth/login"""
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password','').strip().lower()
        if not email or not password:
            response = {
                "Message": "please use keys email and password (Case Sensitive)"
            }
            return make_response(jsonify(response)), 203
        try:
            #  check if user exists
            user = User.query.filter_by(email=request.data['email'].lower()).first()
            if user:
                #  Check if password match
                if check_password_hash(user.password_hash, request.data['password']):
                    #  Generate access token. This will be used as the authorization header
                    access_token = user.generate_token(user.id)
                    response = {'Message': 'You have successfully logged in',
                                "Access token": access_token.decode()}
                    return make_response(jsonify(response)), 200
                else:
                    response = {'Message': 'Password Mismatch. Please try again'}
                    return make_response(jsonify(response)), 301
            else:
                response = {'Message': 'Email address does not match any. Please try again'}
                return make_response(jsonify(response)), 401
        except Exception as e:  # pragma: no cover
            #  Create a response with the error message
            response = {
                        "Message": str(e)
                        }
            return make_response(jsonify(response)), 500


class LogoutView(MethodView):
    """Handles user logout"""
    @swag_from("docs/logout.yml", methods=['POST'])
    def post(self):
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header
        else:
            return {"Message": "Please Provide an access token"}, 300
        if access_token:
            revoked_token = RevokeToken(revoked_token=access_token)
            revoked_token.save()
            response = {"Message": "You have successfully logged out"}
            return make_response(jsonify(response)), 200


class ResetPasswordView(MethodView):
    """Handles reset password"""
    @swag_from("docs/Reset_password.yml", methods=['POST'])
    def post(self):
        secret = str(request.data.get('Secret word', '')).strip().lower() # Get the secret word
        password = str(request.data.get('password', ''))
        email = str(request.data.get('email', '')).strip().lower()
        if email and secret:
            user = User.query.filter_by(email=email).first()
            if user:
                if user.secret == secret:
                    if not len(password) >= 8:
                        response = {'Message': 'Password must be greater than 8'}
                        return make_response(jsonify(response)), 400
                    user.password = password
                    user.save()
                    response = {"Message": "Password updated successfully"}
                    return make_response(jsonify(response)), 201
                elif secret.lower().strip() == 'send me an email':
                    msg = 'Yummy Api Password reset. '
                    msg = Message(msg, sender='sir3n.sn@gmail.com', recipients=[email])
                    msg.html = '<b>Hi. Its siren from Api recipes. </b> <p>Your Secret word is '+str(user.secret)\
                    +'</p>'+ '<p>Please use it to reset your password.\
                     </p> <p>If you did not request for this message please ignore</p>'
                    mail.send(msg)
                    response = {"Message": "A reset value has been sent with instructions via the email provided."}
                    return make_response(jsonify(response)), 200

                else:
                    response = {"Message": "Invalid secret word, please try again",
                                "Instruction" : "type 'send me an email' in the secret word key to recover via email "}
                    return make_response(jsonify(response)), 400
            else:
                response = {"Message": "Please provide a valid email"}
                return make_response(jsonify(response)), 405
        else:
            response = {"Message": "Please provide your email, Secret word and password (Case Sensitive)"}
            return make_response(jsonify(response)), 401


registration_view = RegistrationView.as_view('register_view')
# Define the rule for the registration url > /auth/register
login_view = LoginView.as_view('login_view')
# Define the rule for the registration url > /auth/login
# Add the rule to the blueprint
auth_blueprint.add_url_rule('/api-1.0/auth/register', view_func=registration_view, methods=['POST'])
auth_blueprint.add_url_rule('/api-1.0/auth/login', view_func=login_view, methods=['POST'])

logout_view = LogoutView.as_view('logout_view')
auth_blueprint.add_url_rule('/api-1.0/auth/logout', view_func=logout_view, methods=['POST'])

reset_password_view = ResetPasswordView.as_view('reset_view')
auth_blueprint.add_url_rule('/api-1.0/auth/reset-password', view_func=reset_password_view, methods=['POST'])