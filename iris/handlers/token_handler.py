"""
Handles token validation
"""
from iris.models.user_model import User
from werkzeug.exceptions import HTTPException


class NoTokenProvided(HTTPException):
    """
    :raises: No Token provided
    """
    def __init__(self):
        HTTPException.__init__(self, "Please provide an access token")
        self.code = 499


class InvalidToken(HTTPException):
    """
    :raises: Invalid token provided
    """
    def __init__(self, error):
        HTTPException.__init__(self, str(error))
        self.error = error
        self.code = 498


def assert_token(request):
    """
    Assert that a token was provided and is legit
    :param request: Http request
    :return: True else Exception
    """
    token = request.headers.get("Authorization")
    if not token:
        raise NoTokenProvided

    user_id = User.decode_token(token)

    if isinstance(user_id, str):
        raise InvalidToken(user_id)

    return user_id
