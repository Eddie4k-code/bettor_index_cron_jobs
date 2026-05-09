import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from repositories.players_repository import PlayersRepository

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
    return PlayersRepository(db_session)

def test_insert_player(repository):
    from db.models.player import Player
    # Arrange: create a player instance
    player = Player(id=1, first_name="LeBron", last_name="James", team_id=23, sport_key="basketball_nba")

    # Act: insert the player
    repository.insert_player(player)
    repository.db.commit()

    # Assert: query the database for the player
    result = repository.db.query(Player).filter_by(id=1, sport_key="basketball_nba").first()
    assert result is not None
    assert result.first_name == "LeBron"
    assert result.last_name == "James"
    assert result.team_id == 23
    assert result.sport_key == "basketball_nba"
