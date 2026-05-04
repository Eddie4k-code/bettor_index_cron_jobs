import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.odds_api_prop import OddsAPIProp
from repositories.props_repository import PropsRepository
import datetime

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
def repository(db_session):
    return PropsRepository(db_session)

def test_save_and_get_odds_api_props_flat(repository):
    now = datetime.datetime.utcnow()
    prop_data = {
        'event_id': 'event1',
        'sport_key': 'basketball_nba',
        'sport_title': 'NBA Basketball',
        'commence_time': now + datetime.timedelta(hours=1),
        'home_team': 'Lakers',
        'away_team': 'Warriors',
        'bookmaker': 'draftkings',
        'market_key': 'player_points',
        'market_last_update': now,
        'outcome_name': 'Over',
        'outcome_price': -110,
        'outcome_point': 27.5,
        'outcome_description': 'LeBron James',
        'created_at': now
    }
    repository.save_props([prop_data])
    results = repository.get_props_by_hours_ahead(2)
    assert len(results) == 1
    assert results[0].event_id == 'event1'
    assert results[0].bookmaker == 'draftkings'
    assert results[0].outcome_name == 'Over'
    assert results[0].outcome_price == -110

def test_save_odds_api_props_with_different_outcomes(repository):
    now = datetime.datetime.utcnow()
    prop_data = {
        'event_id': 'event2',
        'sport_key': 'basketball_nba',
        'sport_title': 'NBA Basketball',
        'commence_time': now + datetime.timedelta(hours=3),
        'home_team': 'Celtics',
        'away_team': 'Bulls',
        'bookmaker': 'fanduel',
        'market_key': 'player_rebounds',
        'market_last_update': now,
        'outcome_name': 'Under',
        'outcome_price': 120,
        'outcome_point': 10.5,
        'outcome_description': 'Nikola Vucevic',
        'created_at': now
    }
    repository.save_props([prop_data])
    results = repository.get_props_by_hours_ahead(4)
    assert len(results) == 1
    assert results[0].event_id == 'event2'
    assert results[0].market_key == 'player_rebounds'
    assert results[0].outcome_name == 'Under'
    assert results[0].outcome_price == 120

def test_idempotent_save_odds_api_props(repository):
    now = datetime.datetime.utcnow()
    prop_data = {
        'event_id': 'event3',
        'sport_key': 'basketball_nba',
        'sport_title': 'NBA Basketball',
        'commence_time': now + datetime.timedelta(hours=5),
        'home_team': 'Heat',
        'away_team': 'Knicks',
        'bookmaker': 'betmgm',
        'market_key': 'player_assists',
        'market_last_update': now,
        'outcome_name': 'Over',
        'outcome_price': 130,
        'outcome_point': 8.5,
        'outcome_description': 'Jalen Brunson',
        'created_at': now
    }
    repository.save_props([prop_data])
    # Save again with updated price
    prop_data_updated = dict(prop_data)
    prop_data_updated['outcome_price'] = 150
    repository.save_props([prop_data_updated])
    results = repository.get_props_by_hours_ahead(6)
    assert len(results) == 1
    assert results[0].outcome_price == 150
