class DivarError(Exception):
    default_message = "Divar error occurred"

    def __init__(self, message=None):
        super().__init__(message or self.default_message)

class HttpError(DivarError):
    default_message = "API Request failed"

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"<HTTP {status_code}>: {message}")

class AuthorizationError(DivarError):
    default_message = "Authorization failed"

class AuthorizeRequired(DivarError):
    default_message = "Authorize required"

class SessionExpired(DivarError):
    default_message = "Session is expired"

class MaxRetriesError(DivarError):
    default_message = "Request failed after maximum retry attempts"

class InvalidResponse(DivarError):
    default_message = "Invalid response occurred"
    def __init__(self, message=None, response=None):
        self.response = response
        super().__init__(message or self.default_message)

class CaptchaRequired(DivarError):
    default_message = "Captcha verification required"