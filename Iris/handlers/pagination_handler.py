"""
Validates pagination parameters
"""
from werkzeug.exceptions import HTTPException


class InvalidPaginationParameter(HTTPException):
    """
    Returns pagination exception
    """
    def __init__(self):
        HTTPException.__init__(self, "Invalid pagination parameter")
        self.code = 400


def assert_pagination(request):
    """
    assert pagination query is legit
    :param request: http request
    :return: pagination values
    """
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
    except ValueError:
        raise InvalidPaginationParameter
    else:
        return page, per_page
