"""
Validates data before its added to the data on the endpoint
/categories
"""
import re

from werkzeug.exceptions import HTTPException

pattern = r"^[a-zA-Z\s',_-.]+$"


class IllegalCategoryName(HTTPException):
    """
    Exception for category name
    """
    def __init__(self):
        HTTPException.__init__(self, "Fatal! Illegal Characters Used" )
        self.code = 406


class LongCategoryName(HTTPException):
    """
    Short Name exception
    """
    def __init__(self):
        HTTPException.__init__(self, "Please use a shorter name or detail(description)")
        self.code = 411


class ProvideCorrectName(HTTPException):
    """
    Name  does not exist exception
    """

    def __init__(self):
        HTTPException.__init__(self, "please use keys name and detail (Case Sensitive)")
        self.code = 400


def assert_category(request):
    """
    Assert data is legit
    :param request: Http request
    :return: True Else Exception
    """
    try:
        name = str(request.data.get('name', '')).strip().lower()
        name = re.sub(' +', ' ', name)
        detail = str(request.data.get('detail', '')).strip().lower()
        detail = re.sub(' +',' ', detail)
    except AttributeError:
        raise IllegalCategoryName
    else:
        if not name or not detail:
            raise ProvideCorrectName
        validated = bool(re.match(pattern, name)) and bool(re.match(pattern, detail))

        if validated:
            if len(name) >= 80 or len(detail) >= 80:
                raise LongCategoryName
            return name, detail
        else:
            raise IllegalCategoryName


