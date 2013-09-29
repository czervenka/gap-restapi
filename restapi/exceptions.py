
class ApiException(Exception):

    CODE = 500

    def __init__(self, message, exception=None, code=None, description=None):
        if code is None:
            code = self.CODE
        self.code = code
        self.message = message
        self.orig_exception = exception
        self.description = description

    def __str__(self):
        return "%r %r" % (self.code, self.message)


class InvalidRequestException(ApiException):
    CODE = 400

class NotFoundException(InvalidRequestException):
    CODE = 404

class MethodNotAllowedException(InvalidRequestException):
    CODE = 405

class InternalServerErrorException(ApiException):
    CODE = 500
