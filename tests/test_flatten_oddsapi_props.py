import pytest
from repositories.props_repository import PropsRepository
from schemas.OddsAPIResponses import OddsAPIProp, OddsAPIBookmaker, OddsAPIMarket, OddsAPIOutcome
import datetime
from dateutil import parser

def make_nested_oddsapiprop():
    now = datetime.datetime.utcnow().isoformat()
    return OddsAPIProp(
        id="event123",
        sport_key="basketball_nba",
        sport_title="NBA Basketball",
        commence_time=now,
        home_team="Lakers",
        away_team="Warriors",
        bookmakers=[
            OddsAPIBookmaker(
                key="draftkings",
                title="DraftKings",
                markets=[
                    OddsAPIMarket(
                        key="player_points",
                        last_update=now,
                        outcomes=[
                            OddsAPIOutcome(
                                name="Over",
                                price=-110,
                                description="LeBron James",
                                point=27.5
                            ),
                            OddsAPIOutcome(
                                name="Under",
                                price=100,
                                description="LeBron James",
                                point=27.5
                            )
                        ]
                    )
                ]
            )
        ]
    )

def test_flatten_oddsapi_props():
    nested = make_nested_oddsapiprop()
    flat = PropsRepository._flatten_oddsapi_props([nested])
    assert isinstance(flat, list)
    assert len(flat) == 2
    for row in flat:
        assert row['event_id'] == "event123"
        assert row['bookmaker'] == "draftkings"
        assert row['market_key'] == "player_points"
        assert row['outcome_description'] == "LeBron James"
        assert row['sport_key'] == "basketball_nba"
        assert row['home_team'] == "Lakers"
        assert row['away_team'] == "Warriors"
        assert row['commence_time'] == parser.parse(nested.commence_time)
        assert row['market_last_update'] == parser.parse(nested.bookmakers[0].markets[0].last_update)
        assert row['outcome_point'] == 27.5
        assert row['outcome_name'] in ("Over", "Under")
        assert row['outcome_price'] in (-110, 100)
