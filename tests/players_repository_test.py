import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.player import Player
from repositories.players_repository import PlayersRepository

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
    return PlayersRepository(db_session)

def test_get_players(repo, db_session):
    # Insert some players
    player1 = Player(id=1, first_name="lebron", last_name="james", team_id=1, sport_key="basketball_nba")
    player2 = Player(id=2, first_name="stephen", last_name="curry", team_id=2, sport_key="basketball_nba")
    player3 = Player(id=3, first_name="mike", last_name="trout", team_id=3, sport_key="baseball_mlb")
    db_session.add_all([player1, player2, player3])
    db_session.commit()

    # Should return only NBA players
    nba_players = repo.get_players("basketball_nba")
    assert len(nba_players) == 2
    assert any(p.first_name == "lebron" for p in nba_players)
    assert any(p.first_name == "stephen" for p in nba_players)
    # Should not return MLB player
    assert all(p.sport_key == "basketball_nba" for p in nba_players)
