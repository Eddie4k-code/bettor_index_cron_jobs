from datetime import datetime
from unittest.mock import Mock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models.base import Base
from db.models.mlb_player_stats import MLBPlayerStats
from repositories.mlb_player_stats_repository import MLBPlayerStatsRepository


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
    return MLBPlayerStatsRepository(db_session)


def test_insert_player_stats_persists_record(repo):
    player_stats = MLBPlayerStats(
        player_id=99,
        first_name="shohei",
        last_name="ohtani",
        team_name="dodgers",
        game_id=12345,
        season=2024,
        at_bats=4,
        hits=2,
        hr=1,
        rbi=3,
        bb=1,
        k=0,
        avg="0.333",
        obp="0.400",
        slg="0.700",
        doubles=1,
        triples=0,
        stolen_bases=1,
        plate_appearances=5,
        total_bases=5,
        ip="1.0",
        p_k=2,
        p_bb=0,
        er=0,
        era="2.50",
        pitch_count=14,
        wins=1,
        losses=0,
        saves=0,
        games_started=0,
        sport_key="baseball_mlb",
        commence_time=datetime.fromisoformat("2024-04-05T19:10:00+00:00"),
    )

    inserted_player_stats = repo.insert_player_stats(player_stats)

    result = repo.db.query(MLBPlayerStats).filter_by(
        player_id=99,
        game_id=12345,
        season=2024,
        sport_key="baseball_mlb",
    ).first()

    assert inserted_player_stats == player_stats
    assert result is not None
    assert result.first_name == "shohei"
    assert result.last_name == "ohtani"
    assert result.hits == 2
    assert result.hr == 1
    assert result.ip == "1.0"
    assert result.era == "2.50"


def test_insert_player_stats_raises_when_commit_fails():
    mock_db = Mock()
    mock_db.commit.side_effect = RuntimeError("commit failed")
    repo = MLBPlayerStatsRepository(mock_db)
    player_stats = MLBPlayerStats(
        player_id=99,
        first_name="shohei",
        last_name="ohtani",
        game_id=12345,
        season=2024,
        sport_key="baseball_mlb",
        commence_time=datetime.fromisoformat("2024-04-05T19:10:00+00:00"),
    )

    with pytest.raises(RuntimeError, match="commit failed"):
        repo.insert_player_stats(player_stats)

    mock_db.merge.assert_called_once_with(player_stats)
    mock_db.rollback.assert_called_once()