class TooManyRequestsError(Exception):
    """Exception raised when the API rate limit is exceeded."""
    def __init__(self, message="Too many requests. Please try again later."):
        self.message = message
        super().__init__(self.message)