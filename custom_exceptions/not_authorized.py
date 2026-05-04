class NotAuthorizedError(Exception):
    """Exception raised when the user is not authorized to perform an action."""
    def __init__(self, message="You are not authorized to perform this action."):
        self.message = message
        super().__init__(self.message)