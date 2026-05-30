import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models.base import Base
from db.models.player import Player
from repositories.players_repository import PlayersRepository

def setup_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()

def test_get_player_by_name_single_match():
    db = setup_db()
    repo = PlayersRepository(db)
    player = Player(id=1, first_name="lebron", last_name="james", team_id=23, sport_key="basketball_nba")
    db.add(player)
    db.commit()
    result = repo.get_player_by_name("lebron", "james", "basketball_nba")
    assert len(result) == 1
    assert result[0].id == 1

def test_get_player_by_name_multiple_matches():
    db = setup_db()
    repo = PlayersRepository(db)
    player1 = Player(id=1, first_name="john", last_name="smith", team_id=10, sport_key="basketball_nba")
    player2 = Player(id=2, first_name="john", last_name="smith", team_id=11, sport_key="basketball_nba")
    db.add_all([player1, player2])
    db.commit()
    result = repo.get_player_by_name("john", "smith", "basketball_nba")
    assert len(result) == 2
    ids = {p.id for p in result}
    assert ids == {1, 2}

def test_get_player_by_name_no_match():
    db = setup_db()
    repo = PlayersRepository(db)
    result = repo.get_player_by_name("stephen", "curry", "basketball_nba")
    assert result == []
