"""
Handles authentication on the api
"""
import re

from werkzeug.exceptions import HTTPException
from Iris.handlers.category_handler import IllegalCategoryName, LongCategoryName


class NamesNotProvided(HTTPException):
    """
    raises: Name not provided
    """
    def __init__(self):
        HTTPException.__init__(self, "Provide First Name, Last Name, email, password and Secret word (Case Sensitive)")
        self.code = 449


class InvalidEmailProvided(HTTPException):
    """
    raises: Invalid email provided
    """
    def __init__(self):
        HTTPException.__init__(self, "Invalid Email Provided")
        self.code = 400


class InvalidPasswordProvided(HTTPException):
    """
    raises: Invalid email provided
    """
    def __init__(self):
        HTTPException.__init__(self, "Password must be greater than 8")
        self.code = 411


class InvalidLogin(HTTPException):
    """
    :raise: please use keys email and password
    """
    def __init__(self):
        HTTPException.__init__(self, "please use keys email and password (Case Sensitive)")
        self.code = 449


class InvalidReset(HTTPException):
    """
    :raise: Invalid reset details
    """
    def __init__(self):
        HTTPException.__init__(self, 'Please provide your email, Secret word and password (Case Sensitive)')
        self.code = 449


class InvalidSecretKey(HTTPException):
    """
    :raise: Invalid reset secret
    """
    def __init__(self):
        HTTPException.__init__(self, "Invalid email or secret word please try again. type \
                                'send me an email' in the secret word key to recover via email")
        self.code = 401


def validate_characters(first_name, last_name, email):
    """

    :param first_name: First Name
    :param last_name: Last Name
    :param email: Email
    :raise: validation error
    :return: first_name, last_name, secret
    """
    pattern = r'^[A-Za-z]+$'
    email_pattern = r'^[a-zA-Z.0-9_+]+@[a-zA-z-]+\.[a-zA-Z-]{2,3}$'
    args = [first_name, last_name]
    validated = True
    for names in args:
        if not bool(re.fullmatch(pattern, names)):
            validated = False
    if not bool(re.search(email_pattern, email)):
        raise InvalidEmailProvided
    if validated:
        return first_name, last_name, email
    else:
        raise IllegalCategoryName


def assert_registration(request):
    """

    :param request:
    :raise: IllegalName, LongName
    :return: first_name, last_name, email, password, secret
    """
    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip()
        first_name = request.data.get('First Name', '').strip().lower()
        last_name = request.data.get('Last Name', '').strip().lower()
        secret = request.data.get('Secret word', '').strip().lower()
    except AttributeError:
        raise IllegalCategoryName
    else:
        if first_name and last_name and email and password and secret:
            if len(email) >= 80 or len(first_name) >= 80 or len(last_name) >= 80 or len(secret) >= 80:
                raise LongCategoryName
            if len(password) < 8:
                raise InvalidPasswordProvided
        else:
            raise NamesNotProvided
        first_name, last_name, email, = validate_characters(first_name, last_name, email)
        return first_name, last_name, email, password, secret


def assert_login(request):
    try:
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip().lower()
    except AttributeError:
        raise IllegalCategoryName
    if not email or not password:
        raise InvalidLogin
    else:
        return email, password


def assert_reset(request):
    """

    :param request:  Http Request
    :return: Validated, email, secret, password
    """
    try:
        secret = str(request.data.get('Secret word', '')).strip().lower()
        password = str(request.data.get('password', ''))
        email = str(request.data.get('email', '')).strip().lower()
    except AttributeError:
        raise IllegalCategoryName
    if not email and not secret:
        raise InvalidReset
    if secret != 'send me an email':
        if len(password) >= 8:
            return email, secret, password
        raise InvalidPasswordProvided
    return email, secret, ''

