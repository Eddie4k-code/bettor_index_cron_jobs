## Plan: Split NBA and MLB Game Processing

Keep `get_games` as the public entry point, but turn it into a dispatcher that routes each API response through sport-specific processing helpers. This fixes the root issue that NBA and MLB game payloads do not share the same field names or completed-status values, while minimizing interface and CLI churn.

**Steps**
1. Refactor `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/pipelines/games_pipeline.py` so `get_games(sport, season)` remains the public method and only orchestrates: fetch teams, call `api.get_games`, extract `games`, and dispatch to an NBA-specific or MLB-specific processor based on `sport`.
2. Implement an NBA-specific helper in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/pipelines/games_pipeline.py` that maps `GamesSchema` fields directly into `Game` records using the current NBA field names: `home_team`, `away_team`, `home_team_score`, `away_team_score`, `date`, and `status`. This step depends on step 1.
3. Implement an MLB-specific helper in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/pipelines/games_pipeline.py` that maps `BallDontLieMLBGameSchema` fields into `Game` records using the MLB field names: `home_team_name`, `away_team_name`, `home_runs`, `away_runs`, `date`, and `status`. This step depends on step 1.
4. Add sport-specific completed-game filtering inside each helper in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/pipelines/games_pipeline.py`: NBA should continue using the API-Sports completed status convention; MLB should use BallDontLie’s completed status convention rather than reusing the NBA string. This step depends on steps 2 and 3.
5. Normalize only the fields required by the shared `Game` model in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/db/models/games.py`, without changing repository behavior. In practice this means each helper should translate its source schema into the shared model contract before calling `insert_games`. This step depends on steps 2 and 3.
6. Decide whether MLB date strings need conversion before persistence based on the `Game.date` SQLAlchemy type and current repository/test expectations. If conversion is needed, do it in the MLB helper only; if the existing runtime already tolerates the string, keep the change scoped to field-name/status mapping. This step depends on step 3.
7. Add or rewrite pipeline tests in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/games_pipeline_test.py` to cover both helper paths separately: one NBA case asserting insertion from `GamesSchema`, and one MLB case asserting insertion from `BallDontLieMLBGameSchema`. Include a negative case proving non-completed MLB games are skipped. This step depends on steps 2 through 6.
8. Verify the CLI path in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/main.py` still works without interface changes, because `get_games` remains the public entry point. This can run in parallel with step 7 once step 1 is done.

**Relevant files**
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/pipelines/games_pipeline.py` — current mixed mapping logic in `get_games`, plus empty `process_nba_games` and `process_mlb_games` stubs that can be repurposed.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/schemas/sports_stats_api_responses.py` — source shape differences between `GamesSchema` and `BallDontLieMLBGameSchema`.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/apis/api_sports_io_api.py` — NBA game mapping source and current `status` field source (`game["status"]["long"]`).
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/apis/ball_dont_lie_mlb_api.py` — MLB game mapping source and raw BallDontLie `status`, `home_team_name`, `away_team_name`, `home_runs`, and `away_runs` fields.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/db/models/games.py` — shared persistence contract all processors must satisfy.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/interfaces/games_pipeline_interface.py` — likely unchanged if `get_games` stays public.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/main.py` — call site that should remain stable after the refactor.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/games_pipeline_test.py` — test coverage should be updated to exercise both sport-specific paths; current file content appears out of sync with its name and should be checked during implementation.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/api_sports_io_api_test.py` — reference fixture shape for NBA game responses.
- `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/ball_dont_lie_mlb_api_test.py` — reference fixture shape for MLB game responses and observed status strings.

**Verification**
1. Run the focused pipeline tests for `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/games_pipeline_test.py` after adding NBA and MLB cases.
2. Run the BallDontLie adapter tests in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/ball_dont_lie_mlb_api_test.py` to confirm the plan’s expected MLB response shape still matches reality.
3. Run the NBA adapter tests in `/Users/eddieoconnor/Documents/projects/betting_agent/revised_engine/tests/api_sports_io_api_test.py` to confirm the NBA mapping assumptions remain unchanged.
4. Optionally run the `games` CLI once for `basketball_nba` and once for `baseball_mlb` in a non-production database to confirm the dispatcher path and completed-game filtering behave correctly end to end.

**Decisions**
- Keep `get_games` as the public pipeline method and use internal sport-specific helpers rather than widening the interface.
- Persist only completed games, but determine completion with sport-specific logic instead of a shared hard-coded status check.
- Keep the repository and shared `Game` model unchanged unless the MLB date format forces a targeted conversion.
- Included scope: pipeline dispatch, sport-specific mapping, completed-game filtering, and tests.
- Excluded scope: repository redesign, broader API adapter rewrites, and unrelated status normalization outside game ingestion.

**Further Considerations**
1. BallDontLie completion values should be confirmed against live responses before hard-coding the MLB completed-status rule; current repo fixtures show `Final`, while the pipeline currently checks for `finished`.
2. If MLB and NBA mappings continue to diverge, a small internal translator function returning a shared dict payload before `Game(...)` creation may be cleaner than embedding all field translation inline in each helper.
