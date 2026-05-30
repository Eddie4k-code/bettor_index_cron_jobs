import pytest
from unittest.mock import MagicMock
from db.models.odds_api_props_history import OddsAPIPropHistory
from db.models.hit_rate_event_queue import HitRateEventQueue
from pipelines.props_pipeline import PropsPipeline

class DummyRepo:
    def __init__(self):
        self.saved = []
    def get_props_by_composite_key(self, **kwargs):
        return self.existing
    def save_props(self, props):
        self.saved.append(props)

class DummyEventQueueRepo:
    def __init__(self):
        self.events = []
    def produce_event(self, event):
        self.events.append(event)

class DummyHistoryRepo:
    def __init__(self):
        self.history = []
    def insert_props_history(self, history):
        self.history.append(history)

class DummyAPI:
    def get_events(self, sport, hours_ahead):
        return []
    def get_props_based_on_events(self, sport, events, markets):
        return self.props

def make_existing(point, price):
    class Obj:
        pass
    o = Obj()
    o.event_id = 'evt1'
    o.bookmaker = 'bm'
    o.market_key = 'mk'
    o.outcome_name = 'Over'
    o.outcome_point = point
    o.outcome_price = price
    o.outcome_description = 'desc'
    o.commence_time = '2024-01-01T00:00:00Z'
    o.sport_key = 'basketball_nba'
    o.home_team = 'Lakers'
    o.away_team = 'Warriors'
    o.market_last_update = '2024-01-01T00:00:00Z'
    o.created_at = '2024-01-01T00:00:00Z'
    return o

def make_prop(point, price):
    class Outcome:
        pass
    class Market:
        pass
    class Bookmaker:
        pass
    class Prop:
        pass
    outcome = Outcome()
    outcome.name = 'Over'
    outcome.point = point
    outcome.price = price
    outcome.description = 'desc'
    market = Market()
    market.key = 'mk'
    market.last_update = '2024-01-01T01:00:00Z'
    market.outcomes = [outcome]
    bookmaker = Bookmaker()
    bookmaker.key = 'bm'
    bookmaker.markets = [market]
    prop = Prop()
    prop.event_id = 'evt1'
    prop.bookmakers = [bookmaker]
    return prop

@pytest.mark.parametrize("old_point,old_price,new_point,new_price,expect_event,expect_type", [
    (10.5, 100, 10.5, 120, False, 'PriceChange'), # price only
    (10.5, 100, 12.5, 100, True, 'PointChange'),  # point only
    (10.5, 100, 12.5, 120, True, 'PointChange'),  # both
    (10.5, 100, 10.5, 100, False, None),          # no change
])
def test_history_and_event_logic(old_point, old_price, new_point, new_price, expect_event, expect_type):
    repo = DummyRepo()
    repo.existing = make_existing(old_point, old_price)
    event_repo = DummyEventQueueRepo()
    history_repo = DummyHistoryRepo()
    api = DummyAPI()
    prop = make_prop(new_point, new_price)
    api.props = [prop]
    pipeline = PropsPipeline(repo, api, event_repo, history_repo)
    pipeline.detect_and_produce_hit_rate_events([prop])
    if expect_event:
        assert len(event_repo.events) == 1, "Should produce event"
    else:
        assert len(event_repo.events) == 0, "Should not produce event"
    if expect_type:
        assert len(history_repo.history) == 1, "Should record history"
        assert history_repo.history[0].change_type == expect_type
        assert history_repo.history[0].old_point == old_point
        assert history_repo.history[0].new_point == new_point
        assert history_repo.history[0].old_price == old_price
        assert history_repo.history[0].new_price == new_price
    else:
        assert len(history_repo.history) == 0, "Should not record history"