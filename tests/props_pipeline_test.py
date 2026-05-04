import pytest
from pytest_mock import mocker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from apis.api_config import APIConfig
from apis.the_odds_api import TheOddsAPI
from schemas.OddsAPIResponses import OddsAPIEvent, OddsAPIProp, OddsAPIBookmaker, OddsAPIMarket, OddsAPIOutcome
from db.models.base import Base
from schemas.OddsAPIResponses import OddsAPIEvent
from interfaces.betting_data_api_interface import BettingDataAPIInterface
from pipelines.props_pipeline import PropsPipeline
from interfaces.http_client_interface import HTTPClient
from repositories.props_repository import PropsRepository
from interfaces.props_repository_interface import PropsRepositoryInterface


@pytest.fixture(scope="function")
def db_session():
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def http_client(mocker) -> HTTPClient:
    http_client_mock = mocker.Mock(spec=HTTPClient)
    return http_client_mock

@pytest.fixture
def betting_data_api(http_client, mocker) -> BettingDataAPIInterface:
    betting_data_api_mock = mocker.Mock(spec=BettingDataAPIInterface)
    return betting_data_api_mock


def test_props_pipeline_get_props_successful_insertion(db_session, betting_data_api):
    # Mock API responses
    import datetime
    now = datetime.datetime.utcnow().replace(microsecond=0)
    commence_time = (now + datetime.timedelta(hours=1)).replace(microsecond=0).isoformat() + 'Z'
    mock_events = [
        OddsAPIEvent(
            id="event1",
            sport_key="basketball_nba",
            sport_title="NBA Basketball",
            commence_time=commence_time,
            home_team="Lakers",
            away_team="Warriors"
        )
    ]
    mock_props = [
        OddsAPIProp(
            id="event1",
            sport_key="basketball_nba",
            sport_title="NBA Basketball",
            commence_time=commence_time,
            home_team="Lakers",
            away_team="Warriors",
            bookmakers=[
                OddsAPIBookmaker(
                    key="draftkings",
                    title="DraftKings",
                    markets=[
                        OddsAPIMarket(
                            key="player_points",
                            last_update=commence_time,
                            outcomes=[
                                OddsAPIOutcome(
                                    name="Over",
                                    price=-110,
                                    description="LeBron James",
                                    point=27.5
                                )
                            ]
                        )
                    ]
                )
            ]
        )
    ]
    betting_data_api.get_events.return_value = mock_events
    betting_data_api.get_props_based_on_events.return_value = mock_props

    # Create repository and pipeline
    repository = PropsRepository(db_session)
    pipeline = PropsPipeline(db=repository, api=betting_data_api)
    # Run pipeline
    pipeline.get_props(hours_ahead=24, sport="basketball_nba", markets="player_points")
    # Verify props were saved in the database
    results = repository.get_props_by_hours_ahead(24)

    assert len(results) == 1
    assert results[0].event_id == "event1"
    assert results[0].bookmaker == "draftkings"
    assert results[0].outcome_name == "Over"
    assert results[0].outcome_price == -110




