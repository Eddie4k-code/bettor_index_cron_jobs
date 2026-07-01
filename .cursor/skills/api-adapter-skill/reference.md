# API Adapter Reference

Concrete patterns from this repository.

## Interfaces

| Interface | File | Domain |
|-----------|------|--------|
| `HTTPClient` | `interfaces/http_client_interface.py` | HTTP abstraction all wrappers depend on |
| `SportsStatsAPIInterface` | `interfaces/sports_stats_api_interface.py` | Sports stats (games, players, injuries) |
| `BettingDataAPIInterface` | `interfaces/betting_data_api_interface.py` | Odds and betting events |

## Wrappers

| Wrapper | Interface | Test file |
|---------|-----------|-----------|
| `TheOddsAPI` | `BettingDataAPIInterface` | `tests/the_odds_api_test.py` |
| `BallDontLieMLBAPI` | `SportsStatsAPIInterface` | `tests/ball_dont_lie_mlb_api_test.py` |
| `APISportsIOAPI` | `SportsStatsAPIInterface` | `tests/api_sports_io_api_test.py` |

All wrappers live in `apis/` and accept `(api_config: APIConfig, http_client: HTTPClient)` in the constructor.

## Wrapper shape

```python
from interfaces.betting_data_api_interface import BettingDataAPIInterface
from apis.api_config import APIConfig
from interfaces.http_client_interface import HTTPClient
from schemas.OddsAPIResponses import OddsAPIEvent

class TheOddsAPI(BettingDataAPIInterface):
    def __init__(self, api_config: APIConfig, http_client: HTTPClient):
        self.api_key = api_config.get_api_key()
        self.http_client = http_client

    def get_events(self, sport: str, hours_ahead: int) -> list[OddsAPIEvent]:
        response = self.http_client.get(url, params=params)
        return [OddsAPIEvent(**event) for event in response.json()]
```

## Test shape

```python
@pytest.fixture
def http_client_mock(mocker):
    return mocker.Mock(spec=HTTPClient)

def test_odds_api_get_events(mock_api_config, http_client_mock):
    odds_api = TheOddsAPI(api_config=mock_api_config, http_client=http_client_mock)
    http_client_mock.get.return_value.json.return_value = [{"id": "event1", ...}]

    events = odds_api.get_events(sport="basketball_nba", hours_ahead=24)

    assert all(isinstance(event, OddsAPIEvent) for event in events)
```

## Schemas

- `schemas/sports_stats_api_responses.py` — sports stats response models
- `schemas/OddsAPIResponses.py` — odds API response models

## Validation commands

```bash
pytest tests/the_odds_api_test.py -v
pytest tests/ball_dont_lie_mlb_api_test.py -v
pytest tests/api_sports_io_api_test.py -v
```
