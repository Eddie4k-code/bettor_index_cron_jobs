import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.PlayerStatsProcessing import PlayerStatsProcessing
from repositories.player_stats_processing_repository import PlayerStatsProcessingRepository

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

@pytest.fixture
def repo(db_session):
    return PlayerStatsProcessingRepository(db_session)

def test_mark_and_check_processed(repo):
    player_id = 1
    game_id = 100
    season = 2023
    sport_key = "basketball_nba"

    # Should not be processed initially
    assert not repo.is_processed(player_id, game_id, season, sport_key)

    # Mark as processed
    repo.mark_processed(player_id, game_id, season, sport_key)

    # Should now be processed
    assert repo.is_processed(player_id, game_id, season, sport_key)