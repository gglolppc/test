class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, error_type=None):
        super().__init__(message)
        self.message = message
        self.error_type = error_type or self.__class__.__name__
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {
            'error': self.error_type,
            'message': self.message,
            'status': self.status_code
        }

class AuthError(APIError):
    def __init__(self, message="Wrong password or email"):
        super().__init__(message, status_code=401, error_type="AuthError")

class NotFoundError(APIError):
    def __init__(self, message="Not found"):
        super().__init__(message, status_code=404, error_type="NotFound")
