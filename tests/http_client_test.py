import pytest
from custom_exceptions.not_authorized import NotAuthorizedError
from custom_exceptions.too_many_requests import TooManyRequestsError
from pytest_mock import MockerFixture
from clients.httpx_client import HTTPXClient
import httpx

def test_429_error_handling(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 429
    
    mocker.patch('httpx.get', return_value=mock_response)
    mocker.patch('time.sleep', return_value=None)

    client = HTTPXClient()
    
    with pytest.raises(TooManyRequestsError):
        client.get("http://test.com")
    
    assert httpx.get.call_count == 10  # Should retry 10 times before giving up


def test_401_error_thrown(mocker):
    mock_response = mocker.Mock()
    mock_response.status_code = 401
    
    mocker.patch('httpx.get', return_value=mock_response)

    client = HTTPXClient()
    
    with pytest.raises(NotAuthorizedError):
        client.get("http://test.com")