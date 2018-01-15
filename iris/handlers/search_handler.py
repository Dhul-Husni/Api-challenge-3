"""
Handles validations for search
"""
from werkzeug.exceptions import HTTPException


class SearchItemNotAllowed(HTTPException):
    """
    Handles invalid search item
    """
    def __init__(self):
        HTTPException.__init__(self, "Invalid Search Parameter")
        self.code = 400


class EmptySearchParameter(HTTPException):
    """
    Handles invalid search item
    """
    def __init__(self):
        HTTPException.__init__(self, "Cannot search for nothing")
        self.code = 400


def assert_search(request):
    """
    Assert Search values
    :param request: get parameter q
    :return: q
    """
    q = request.values.get('q', '')
    if not isinstance(q, str):
        raise SearchItemNotAllowed
    q = q.strip().lower()
    if not q:
        raise EmptySearchParameter
    return q
