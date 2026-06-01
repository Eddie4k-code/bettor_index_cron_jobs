# Plan: BallDontLie MLB API Wrapper

Wrap the BallDontLie MLB REST API (`https://api.balldontlie.io`) behind `SportsStatsAPIInterface`, following the same pattern as `SportsIOAPI`. Three deliverables: new MLB schemas, a new wrapper class, and unit tests.

---

## Phase 1: New MLB Schemas — `schemas/sports_stats_api_responses.py`

Add MLB-specific Pydantic models to the **existing** file:

1. `BallDontLieMLBTeamSchema` — `id`, `abbreviation`, `display_name`, `name`, `location`, `league`, `division`
2. `BallDontLieMLBTeamResponse` — `teams: List[BallDontLieMLBTeamSchema]`
3. `BallDontLieMLBGameSchema` — `id`, `season`, `date`, `status`, `home_team_name`, `home_team_id`, `away_team_name`, `away_team_id`, `home_runs`, `away_runs` (optional)
4. `BallDontLieMLBGamesResponse` — `games: List[BallDontLieMLBGameSchema]`
5. `BallDontLieMLBPlayerStatsSchema` — `player_id`, `firstname`, `lastname`, `team_name`, `game_id`, `season`, plus batting stats (`at_bats`, `hits`, `hr`, `rbi`, `bb`, `k`, `avg`, `obp`, `slg`, `doubles`, `triples`, `stolen_bases`, `plate_appearances`, `total_bases`) and key pitching stats (`ip`, `p_k`, `p_bb`, `er`, `era`, `pitch_count`, `wins`, `losses`, `saves`, `games_started`) — all `Optional`
6. `BallDontLieMLBPlayerStatsResponse` — `stats: List[BallDontLieMLBPlayerStatsSchema]`

**Reused as-is**: `PlayersSchema` and `SportsStatsAPIPlayersResponse` — player names and ID are universal.

---

## Phase 2: API Wrapper — `apis/ball_dont_lie_mlb_api.py` (new file)

Create `BallDontLieMlbAPI(SportsStatsAPIInterface)`:

- **Auth**: `{"Authorization": api_key}` header (different from SportsIO's `x-apisports-key`)
- **Response key**: `data` (not `response`)
- **Base URL**: `https://api.balldontlie.io`

| Method | Endpoint | Notes |
|---|---|---|
| `get_teams(sport)` | `GET /mlb/v1/teams` | Returns `BallDontLieMLBTeamResponse` |
| `get_games(sport, season, team_id)` | `GET /mlb/v1/games?team_ids[]={id}&seasons[]={season}` | Runs from `home_team_data.runs` / `away_team_data.runs` |
| `get_players(team_id, season)` | `GET /mlb/v1/players?team_ids[]={id}` | Returns `SportsStatsAPIPlayersResponse`; season param accepted but not forwarded |
| `get_player_stats(player_id, season, sport)` | `GET /mlb/v1/stats?player_ids[]={id}&seasons[]={season}` | Returns `BallDontLieMLBPlayerStatsResponse` |

---

## Phase 3: Unit Tests — `tests/ball_dont_lie_mlb_api_test.py` (new file)

Mirrors the pattern of `tests/api_sports_io_api_test.py`:

- Fixtures: `mock_api_config`, `http_client_mock`, `api`
- 4 tests: `test_get_teams_200`, `test_get_games_200`, `test_get_players_200`, `test_get_player_stats_200`
- Each mocks `http_client_mock.get.return_value.json.return_value` with realistic MLB API payloads, then asserts on response type and key field values

---

## Relevant Files

- `schemas/sports_stats_api_responses.py` — extend with MLB schemas
- `apis/ball_dont_lie_mlb_api.py` — new wrapper (does not exist yet)
- `tests/ball_dont_lie_mlb_api_test.py` — new tests (does not exist yet)
- `interfaces/sports_stats_api_interface.py` — reference only, no changes
- `apis/api_config.py` — reused as-is

## Verification

1. `pytest tests/ball_dont_lie_mlb_api_test.py -v` — all 4 tests pass with no real HTTP calls
2. `pytest` full suite — no regressions

## Decisions

- MLB-specific schemas rather than mapping baseball data into NBA-shaped models — the fields are too different
- `SportsStatsAPIInterface` is not modified
- Scope is limited to the 4 core interface methods; season stats, standings, odds, pitch-type stats are excluded
- `season` param in `get_players` is accepted but not forwarded (API does not support season filter on players endpoint)
