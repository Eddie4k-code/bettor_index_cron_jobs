import httpx
from interfaces.http_client_interface import HTTPClient
import logging
from custom_exceptions.too_many_requests import TooManyRequestsError
from custom_exceptions.not_authorized import NotAuthorizedError
import time

logger = logging.getLogger(__name__)

class HTTPXClient(HTTPClient):
    def get(self, url, params=None, headers=None):
        attempts = 10
        base_wait=60

        for attempt in range(attempts):
            try:
                response = httpx.get(url, params=params, headers=headers)
                print(f"HTTP GET Request to {url} and returned status code {response.status_code}")
                if response.status_code == 429:
                    logger.warning(f"Received 429 Too Many Requests. Attempt {attempt + 1} of {attempts}. Retrying...")
                    raise TooManyRequestsError("Too many requests. Please try again later.")
                
                if response.status_code == 401:
                    logger.error("Unauthorized access - check your API key.")
                    raise NotAuthorizedError("Unauthorized access - check your API key.")
                
                if response.status_code == 422:
                    logger.error("Unprocessable Entity - check your request parameters.")
                    raise httpx.HTTPStatusError("Unprocessable Entity - check your request parameters.", request=response.request, response=response)

                return response
            

                
            except TooManyRequestsError:
                if attempt < attempts - 1:
                    time.sleep(base_wait * (2 ** attempt))  # Exponential backoff
                    continue  # Retry on TooManyRequestsError
                else:
                    logger.error("Exceeded maximum retry attempts due to too many requests.")
                    raise

            except httpx.TimeoutException as e:
                if attempt < attempts - 1:
                    logger.warning(f"Request timed out. Attempt {attempt + 1} of {attempts}. Retrying...")
                    time.sleep(base_wait * (2 ** attempt))  # Exponential backoff
                    continue  # Retry on timeout
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error occurred: {e}")
                raise
        
