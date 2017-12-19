from . import auth_blueprint
from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User
from werkzeug.security import check_password_hash
from app.models import RevokeToken
from flasgger import swag_from
import re
class RegistrationView(MethodView):
    """This class handles user registration"""
    @swag_from("docs/Register_user.yml", methods=['POST'])
    def post(self):
        """Handles post requests from this url /auth/register"""
        user = User.query.filter_by(email=request.data['email']).first()  # returns None if none exist
        if not user:
            # Register the user
            try:
                email = request.data.get('email', '')
                password = request.data.get('password', '')
                first_name = request.data.get('First Name', '')
                last_name = request.data.get('Last Name', '')
                if first_name and last_name and email and password:
                    if re.match(r'^[a-zA-z0-9_+.]+@[a-zA-z-]+\.[a-zA-z-]+$', email): # validate email
                        if password >= 8:  # validate password
                            user = User(email=email, password=password, first_name=first_name, last_name=last_name)
                            user.save()
                            response = {'Message': 'You have successfully registered'}
                        else:
                            response = {'Message': 'Password must be greater than 8'}
                    else:
                        response = {'Message': 'Please provide a valid email'}
                    return make_response(jsonify(response)), 201
                else:
                    response = {"Message": "Please fill out First Name, Last Name, email and password"}
                    return make_response(jsonify(response)), 203
            except Exception as e:
                # if error occured returns the error as a message
                return {'Message': str(e)}, 401

        else:
            # The user is already registered. We don't want to register them twice
            response = {'Message': 'User already exists. Please login'}
            return make_response(jsonify(response)), 202


class LoginView(MethodView):
    """Handles user login"""
    @swag_from("docs/Login.yml", methods=['POST'])
    def post(self):
        """Handles post requests to this url /auth/login"""
        try:
            #  check if user exists
            user = User.query.filter_by(email=request.data['email']).first()
            if user:
                #  Check if password match
                if check_password_hash(user.password_hash, request.data['password']):
                    #  Generate access token. This will be used as the authorization header
                    access_token = user.generate_token(user.id)
                    if access_token:
                        response = {'Message': 'You have successfully logged in',
                                    "Access token": access_token.decode()}
                        return make_response(jsonify(response)), 200
                    else:
                        response = {'Message': 'Something went wrong. Please try again'}
                        return make_response(jsonify(response)), 300

                else:
                    response = {'Message': 'Password Mismatch. Please try again'}
                    return make_response(jsonify(response)), 301
            else:
                response = {'Message': 'Email address does not match any. Please try again'}
                return make_response(jsonify(response)), 401
        except Exception as e:
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
            access_token = auth_header.split(" ")[1]
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
        # Get the access token from the header
        auth_header = request.headers.get('Authorization')
        if auth_header:
            access_token = auth_header.split(" ")[1]
        else:
            return {"Message": "Please Provide an access token"}, 300
        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                password = str(request.data.get('password', ''))
                user = User.query.filter_by(id=user_id).first()
                if password:
                    user.password = password
                    user.save()
                    response = {"Message": "Password updated successfully"}
                    return make_response(jsonify(response)), 201
                else:
                    response = {"Message": "Password cannot be an empty string"}
                    return make_response(jsonify(response)), 401
            else:
                response = {"Message": str(user_id)}
                return make_response(jsonify(response)), 405
        else:
            response = {"Please login to change password"}
            return make_response(jsonify(response)), 400


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