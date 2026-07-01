---
name: api-wrapper-pipeline-cron
description: Create a pipeline from an existing API wrapper that runs as a cron-style command. Use when adding a new pipeline, wiring an API wrapper into repositories, following repo patterns from games_pipeline, players_pipeline, player_stats_pipeline, or props_pipeline, and adding unit tests for each pipeline method and success path.
disable-model-invocation: false
---

# API Wrapper Pipeline Cron

## What This Skill Does

This skill creates a new pipeline around an existing API wrapper in this repository and carries the work through the repo's normal execution path:

- pipeline class under `pipelines/`
- interface when a pipeline-specific abstraction is needed under `interfaces/`
- repository integration using existing repository interfaces and models
- command wiring in `main.py` when the cron is triggered through the CLI
- unit tests that cover each pipeline method and the success path for each method

It is for repo-specific pipeline work, not generic job scheduler setup or jobs-module scaffolding.

## When to Use

Use this skill when:

- you already have an API wrapper and need a pipeline that consumes it
- you need to follow the patterns used by `GamesPipeline`, `PlayersPipeline`, `PlayerStatsPipeline`, or `PropsPipeline`
- the pipeline will run on a cron cadence or cron-style command
- you need unit tests for every public pipeline method and every internal method that contains decision logic or data mapping
- you need to wire the new pipeline into the repo's CLI entrypoint in `main.py`

Do not use this skill when:

- you are only building or fixing the API wrapper
- you are only changing repository persistence logic
- you need a full external scheduler or deployment configuration
- you want this skill to generate a separate `jobs/` module by default
- the task is just a one-off script rather than a reusable pipeline

## Repo Pattern To Follow

The existing repo establishes these conventions:

1. API wrappers normalize provider payloads into Pydantic schemas before the pipeline sees them.
2. Pipelines orchestrate cross-repository work and map schema objects into DB models.
3. Pipelines branch by sport or mode only when the repo already does that in the owning abstraction.
4. CLI execution is wired in `main.py` by constructing repositories, APIs, and pipelines inside the sport-specific branch.
5. Tests are narrow and use mocks for repositories and APIs unless the existing test pattern intentionally uses a real DB session.

Reference implementations:

- `pipelines/games_pipeline.py`
- `pipelines/players_pipeline.py`
- `pipelines/player_stats_pipeline.py`
- `pipelines/props_pipeline.py`
- `tests/games_pipeline_test.py`
- `tests/players_pipeline_test.py`
- `tests/player_stats_pipeline_test.py`
- `tests/props_pipeline_test.py`

For concrete examples from this repo, see [reference.md](reference.md).

## Procedure

1. Start from the wrapper contract.
Determine the exact wrapper method or methods the pipeline will call, the response schema they return, and whether the wrapper already normalizes provider-specific naming. If the wrapper contract is still unstable, stabilize that before writing the pipeline.

2. Choose the owning pipeline boundary.
Decide whether this work belongs in a new pipeline file or inside an existing pipeline. Create a new pipeline when the workflow has its own orchestration steps, dependencies, or persistence target. Extend an existing pipeline only when the new behavior is the same workflow with a nearby branch.

3. Define constructor dependencies explicitly.
Match the existing repo style: inject repositories and APIs through the constructor, type against interfaces where those interfaces already exist, and avoid creating dependencies inside the pipeline body.

4. Define the public pipeline method first.
Choose the cron entrypoint method name based on the workflow, such as `get_games`, `get_players`, `get_player_stats`, or another task-specific verb. Keep the public method small and let it delegate to helper methods when the workflow branches by sport, record type, or mapping mode.

5. Map schema objects into DB models inside the pipeline.
Follow the current repo pattern where pipelines convert schema objects into DB model instances before calling repository insert methods. Normalize casing and date handling the same way nearby pipelines do. Keep provider-specific field interpretation out of repositories when the pipeline is the orchestration layer.

6. Handle branching and skips deliberately.
If the workflow branches by sport or status, use explicit branch methods like `process_nba_games` or `_process_mlb_player_stats`. If records should be skipped, encode the skip rule in the pipeline and test it directly.

7. Wire the cron entrypoint in `main.py` when the task requires runnable execution.
Follow the existing pattern in the sport-specific branch:

- initialize repositories
- initialize shared HTTP client and API configs
- initialize the API wrapper
- initialize the pipeline
- add a command branch that invokes the pipeline method

Do not create a dedicated `jobs/` module by default for this skill. If the codebase later introduces a separate jobs module, keep the pipeline reusable and let the job call the pipeline rather than embedding workflow logic in the job.

8. Add unit tests for every involved method.
At minimum, cover:

- the public pipeline method success path
- every helper method that contains branching, filtering, mapping, or skip behavior
- unsupported sport or missing dependency branches when relevant
- repository insert calls and the mapped model field values
- API wrapper calls with the expected arguments

When the pipeline transforms dates, team names, player names, or scores, assert those normalized values directly.

9. Validate narrowly first.
Run the focused pipeline test file before broader regression checks. If the pipeline touches shared schema or wrapper code, run the nearest wrapper tests too.

## Decision Points

### New pipeline or extend existing

- Create a new pipeline when the workflow has its own persistence destination, schedule, or orchestration sequence.
- Extend an existing pipeline when the new behavior is just a nearby branch of the same lifecycle.

### Public method only or helper methods too

- Keep only one public method when the workflow is linear.
- Split into helper methods when there is sport-specific processing, repeated mapping logic, or meaningful skip/filter branches that deserve direct tests.

### CLI wiring now or later

- Wire `main.py` now if the user asked for a cron-style runnable command in this repo.
- Defer entrypoint wiring if the task is intentionally limited to the pipeline class and tests.

### Mock-only tests or DB-backed tests

- Prefer mock-based unit tests for pipeline orchestration.
- Use DB-backed tests only when following an established pattern for persistence-heavy pipeline behavior, like some props flows.

## Quality Criteria

The skill is complete when:

- the pipeline consumes an existing API wrapper rather than raw provider JSON
- constructor dependencies are injected cleanly
- the public pipeline method matches the workflow entrypoint
- mapping and skip logic live in the pipeline, not ad hoc in `main.py`
- `main.py` is wired when runnable cron-style execution is part of scope
- unit tests cover each involved pipeline method and every success path
- focused tests pass before widening scope

## Completion Checklist

- pipeline file created or updated under `pipelines/`
- interface created or updated if the repo already models that boundary
- repository dependencies selected and injected
- wrapper method calls aligned with existing schema contracts
- mapped DB model fields asserted in tests
- command or cron-style entrypoint wired if requested
- focused pytest file added or updated
- focused tests executed successfully

## Example Prompts

- `@api-wrapper-pipeline-cron Create an injuries pipeline from BallDontLieMlbAPI that stores MLB player injuries and expose it through the existing baseball CLI path`
- `@api-wrapper-pipeline-cron Build a pipeline for a new wrapper method, following player_stats_pipeline patterns and adding unit tests for each method`
- `@api-wrapper-pipeline-cron Add a cron-style pipeline around an API wrapper and wire the command in main.py with mocked pipeline tests`
