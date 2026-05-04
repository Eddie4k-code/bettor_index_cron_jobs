import httpx
from interfaces.http_client_interface import HTTPClient
import logging
from custom_exceptions.too_many_requests import TooManyRequestsError
import time

logger = logging.getLogger(__name__)

class HTTPXClient(HTTPClient):
    def get(self, url, params=None, headers=None):
        attempts = 10
        base_wait=60

        for attempt in range(attempts):
            try:
                response = httpx.get(url, params=params, headers=headers)
                if response.status_code == 429:
                    logger.warning(f"Received 429 Too Many Requests. Attempt {attempt + 1} of {attempts}. Retrying...")
                    raise TooManyRequestsError("Too many requests. Please try again later.")
                return response.json()
            except TooManyRequestsError:
                if attempt < attempts - 1:
                    time.sleep(base_wait * (2 ** attempt))  # Exponential backoff
                    continue  # Retry on TooManyRequestsError
                else:
                    logger.error("Exceeded maximum retry attempts due to too many requests.")
                    raise
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
        
