from pipelines.props_pipeline import PropsPipeline
from repositories.props_repository import PropsRepository
from schemas.OddsAPIResponses import OddsAPIBookmaker, OddsAPIMarket, OddsAPIOutcome, OddsAPIProp


class DummyRepo:
    def __init__(self, existing=None):
        self.existing = existing

    def get_props_by_composite_key(self, **kwargs):
        return self.existing


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


class DummyPlayersRepository:
    def get_player_by_id(self, player_id, sport_key):
        class Player:
            pass

        player = Player()
        player.id = player_id
        player.team_id = 12
        return player


class DummyTeamsRepository:
    def get_teams(self, sport):
        class Team:
            pass

        home = Team()
        home.name = 'tampa bay rays'
        home.id = 12

        away = Team()
        away.name = 'los angeles angels'
        away.id = 13

        return [home, away]


def make_prop(player_id, point=1.5, price=-110):
    return OddsAPIProp(
        id='evt1',
        sport_key='baseball_mlb',
        sport_title='MLB',
        commence_time='2024-01-01T00:00:00Z',
        home_team='Tampa Bay Rays',
        away_team='Los Angeles Angels',
        bookmakers=[
            OddsAPIBookmaker(
                key='draftkings',
                title='DraftKings',
                markets=[
                    OddsAPIMarket(
                        key='batter_hits',
                        last_update='2024-01-01T00:00:00Z',
                        outcomes=[
                            OddsAPIOutcome(
                                name='Over',
                                price=price,
                                description='Jonathan Aranda',
                                point=point,
                                player_id=player_id,
                            )
                        ],
                    )
                ],
            )
        ],
    )


def make_existing(player_id, point=1.0, price=-105):
    class Existing:
        pass

    existing = Existing()
    existing.event_id = 'evt1'
    existing.bookmaker = 'draftkings'
    existing.market_key = 'batter_hits'
    existing.outcome_name = 'over'
    existing.outcome_point = point
    existing.outcome_description = 'jonathan aranda'
    existing.commence_time = '2024-01-01T00:00:00Z'
    existing.sport_key = 'baseball_mlb'
    existing.home_team = 'tampa bay rays'
    existing.away_team = 'los angeles angels'
    existing.market_last_update = '2024-01-01T00:00:00Z'
    existing.outcome_price = price
    existing.player_id = player_id
    return existing


def make_pipeline(repo):
    return PropsPipeline(
        db=repo,
        api=None,
        hit_rate_event_queue_repo=DummyEventQueueRepo(),
        odds_api_prop_history_repo=DummyHistoryRepo(),
        teams_repository=DummyTeamsRepository(),
        players_repository=DummyPlayersRepository(),
    )


def test_detect_and_produce_hit_rate_events_uses_outcome_player_id_for_new_prop():
    repo = DummyRepo(existing=None)
    pipeline = make_pipeline(repo)
    prop = make_prop(player_id=58)

    pipeline.detect_and_produce_hit_rate_events([prop])

    assert len(pipeline.hit_rate_event_queue_repo.events) == 1
    assert pipeline.hit_rate_event_queue_repo.events[0].player_id == 58
    assert pipeline.hit_rate_event_queue_repo.events[0].player_team_id == 12
    assert pipeline.hit_rate_event_queue_repo.events[0].home_team_id == 12
    assert pipeline.hit_rate_event_queue_repo.events[0].away_team_id == 13


def test_detect_and_produce_hit_rate_events_falls_back_to_existing_player_id():
    repo = DummyRepo(existing=make_existing(player_id=58))
    pipeline = make_pipeline(repo)
    prop = make_prop(player_id=None, point=1.5)

    pipeline.detect_and_produce_hit_rate_events([prop])

    assert len(pipeline.hit_rate_event_queue_repo.events) == 1
    assert pipeline.hit_rate_event_queue_repo.events[0].player_id == 58
    assert pipeline.hit_rate_event_queue_repo.events[0].player_team_id == 12
    assert pipeline.hit_rate_event_queue_repo.events[0].home_team_id == 12
    assert pipeline.hit_rate_event_queue_repo.events[0].away_team_id == 13
    assert pipeline.odds_api_prop_history_repo.history[0].player_id == 58


def test_flatten_oddsapi_props_preserves_player_id():
    prop = make_prop(player_id=58)

    flattened = PropsRepository._flatten_oddsapi_props([prop])

    assert flattened[0]['player_id'] == 58