import pytest
from pytest_mock import MockerFixture
from db.db import get_db

def test_get_db_returns_session(mocker: MockerFixture):
    mock_session = mocker.MagicMock()
    mocker.patch('db.db.SessionLocal', return_value=mock_session)
    with get_db() as session:
        assert session is mock_session
    mock_session.close.assert_called_once()

