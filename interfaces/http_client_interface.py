from abc import ABC, abstractmethod

class HTTPClient(ABC):
    @abstractmethod
    def get(self, url, params=None, headers=None):
        """
        Perform a GET request.
        Args:
            url (str): The URL to request.
            params (dict, optional): Query parameters.
            headers (dict, optional): Request headers.
        Returns:
            Response object or dict.
        """
        pass
