---
name: model-repository-crud
description: 'Create or update a repository around a DB model in this repo. Use when given a SQLAlchemy model and a set of required operations, and you need a repository class, optional interface, focused tests, merge-based writes, try/except commits, rollback on commit failure, and logging for repository errors.'
argument-hint: 'What model needs a repository, and which operations should the repository support?'
user-invocable: true
disable-model-invocation: false
---

# Model Repository CRUD

## What This Skill Does

This skill creates or updates a repository around an existing DB model in this repository.

It is designed for repo operations such as:

- insert or upsert methods
- get-by-id and filtered lookup methods
- simple list or query helpers
- repository interface alignment when the repo already models that boundary
- focused unit tests for the repository behavior that was added or changed

It encodes the repository conventions already present in this codebase:

- use `self.db.merge(...)` for writes unless the task explicitly requires a different persistence strategy
- wrap writes in `try/except`
- call `self.db.commit()` on success
- call `self.db.rollback()` if commit fails
- log errors with `logger.error(...)`

## When to Use

Use this skill when:

- you already have a SQLAlchemy model and need a repository for it
- the user specifies repository operations such as insert, get, update, list, or filtered fetches
- you need the repository to follow the local commit, rollback, and logging conventions
- you need to add or update the matching repository interface in `interfaces/`

Do not use this skill when:

- you need to design the DB model first
- the task is primarily pipeline orchestration rather than persistence
- the task is primarily API wrapper work
- you need a custom transaction strategy that intentionally differs from the repo default

## Repo Pattern To Follow

The repository layer in this codebase currently follows these rules:

1. Repositories accept `db` in the constructor and store it on `self.db`.
2. Write methods usually call `self.db.merge(model_instance)`.
3. Write methods wrap `self.db.commit()` in `try/except`.
4. On write failure, repositories call `self.db.rollback()`, log the error, and re-raise.
5. Read methods usually wrap the query in `try/except`, log errors, and re-raise.
6. Logging uses a module-level `logger = logging.getLogger(__name__)`.

Reference implementations:

- `repositories/players_repository.py`
- `repositories/mlb_player_stats_repository.py`
- nearby repository and interface pairs under `repositories/` and `interfaces/`

## Procedure

1. Start from the model and requested operations.
Identify the exact DB model and the minimum repository methods needed, such as `insert_*`, `get_*`, `list_*`, or a filtered lookup. Do not invent broad CRUD if the user only asked for a narrow set of operations.

2. Confirm the ownership boundary.
Choose the repository file under `repositories/` and determine whether a matching interface already exists under `interfaces/`. If the codebase already uses an interface for that repository family, update or create the interface too.

3. Create the repository skeleton.
Follow the local structure:

- import `logging`
- import the DB model
- import the repository interface if one exists
- define `logger = logging.getLogger(__name__)`
- accept `db` in `__init__`

4. Implement write methods with the local persistence pattern.
For insert or upsert-style operations:

- call `self.db.merge(model_instance)` before commit
- wrap `self.db.commit()` in `try/except`
- on success, optionally return the model instance if the surrounding repo family does that
- on failure, call `self.db.rollback()`, log the error with identifying fields, and re-raise

5. Implement read methods with logging and re-raise behavior.
For query methods:

- use `self.db.query(Model)` with the narrowest filter needed
- wrap query execution in `try/except` when following the surrounding repo pattern
- log the failing lookup context and re-raise on failure

6. Keep method names aligned with repo conventions.
Examples:

- `insert_player`
- `insert_player_stats`
- `get_players`
- `get_player_by_name`

Prefer descriptive names over generic `save` or `fetch` if nearby repositories use more specific verbs.

7. Add or update the interface when needed.
If this repository family uses an interface, add abstract methods only for the operations that actually exist on the repository. Keep the interface narrow.

8. Add focused tests for the methods you touched.
At minimum, cover:

- successful write path
- rollback behavior when `commit()` fails for write methods
- successful read path for each new query method
- raised exception behavior on failed query methods when that path is part of the repo pattern

Prefer mock-based unit tests unless the existing repository tests for that area already rely on a DB session fixture.

9. Validate narrowly.
Run the focused repository test file first. If the repository affects a nearby pipeline or adapter contract, run the nearest dependent tests next.

## Decision Points

### Merge or another write strategy

- Use `merge` by default.
- Only choose `add` or a custom write path when the user explicitly asks for behavior that `merge` should not provide.

### Interface or no interface

- Create or update an interface if that repository category already uses one in `interfaces/`.
- Skip creating a new interface only if the repo pattern around that area clearly does not use interfaces.

### Return value or no return value

- Return the written model if nearby repositories in that family already do so or the caller needs it.
- Otherwise keep the method side-effect oriented and consistent with adjacent repositories.

### Mock tests or DB-backed tests

- Prefer mocks for commit, rollback, merge, and query interaction checks.
- Use DB-backed tests only when the repo already has fixture-based persistence tests and the new behavior is query-heavy enough to justify it.

## Quality Criteria

The skill is complete when:

- the repository only exposes the requested operations
- write methods use `merge`, `commit`, `rollback`, and `logger.error` consistently
- read methods log failures and re-raise consistently with nearby repos
- the interface is updated when that boundary exists
- focused tests cover the changed methods and the main error path for writes
- the narrow test file passes

## Completion Checklist

- repository file created or updated under `repositories/`
- matching interface created or updated under `interfaces/` when appropriate
- constructor accepts `db`
- write methods use `merge`
- commit is wrapped in `try/except`
- rollback occurs on failed commit
- logging is present for repository failures
- focused tests added or updated
- focused tests executed successfully

## Example Prompts

- `/model-repository-crud Create a repository for a new MLB injuries model with insert and get-by-team operations`
- `/model-repository-crud Given this SQLAlchemy model, add the repository methods needed for upsert and filtered reads`
- `/model-repository-crud Update this repository to support a new query method and add rollback and logging coverage tests`