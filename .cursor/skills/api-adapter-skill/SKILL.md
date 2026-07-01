---
name: api-adapter-skill
description: Create or update external API wrappers, interfaces, response schemas, and unit tests. Use when adding a new third-party API, refactoring an adapter, fixing payload parsing, aligning wrapper output with Pydantic schemas, or refreshing focused wrapper tests.
disable-model-invocation: false
---

# API Adapter Skill

## What This Skill Does

This skill standardizes how this codebase wraps third-party APIs.

Use it to:
- add a new external API wrapper
- update an existing adapter when the provider payload changes
- align wrapper output with repository-facing schemas
- enforce the project's interface, HTTP client, and testing conventions

The goal is to keep provider-specific details inside the wrapper layer so the rest of the codebase depends on stable internal contracts.

## When to Use

Use this skill when you need to:
- wrap a new external API behind an internal interface
- fix contract drift between a provider payload and our schemas
- change request parameters, auth headers, pagination, or response parsing in an adapter
- add or update unit tests for a wrapper
- switch providers later without rewriting pipeline or repository code

Do not use this skill for:
- internal repository or DB-only changes
- pipeline-only changes that do not touch an external API contract
- frontend or UI work

## Project Conventions

Follow these conventions in this repository:

1. Any external API we use should be wrapped behind our own interface.
2. The implementation should depend on our wrapper interface rather than raw provider calls.
3. The wrapper should take our HTTP client abstraction, `HTTPClient`, instead of making direct requests with a library client.
4. Wrapper methods should return Pydantic response schemas, not raw provider JSON.
5. Wrapper behavior must be covered by unit tests with mocked HTTP responses.

Relevant existing patterns:
- `interfaces/sports_stats_api_interface.py`
- `interfaces/http_client_interface.py`
- `apis/`
- `schemas/sports_stats_api_responses.py`
- `tests/*_api_test.py`

For concrete examples from this repo, see [reference.md](reference.md).

## Procedure

1. Identify the correct abstraction boundary.
   - If an existing interface already represents the API category, implement that interface.
   - If no suitable interface exists, create one first and define the methods the rest of the app should depend on.

2. Define the internal contract before coding the wrapper.
   - Decide what methods the wrapper should expose.
   - Decide what Pydantic schemas should be returned.
   - Keep the return contract shaped for the application, not for the provider.

3. Create or update the wrapper in `apis/`.
   - Accept configuration and our `HTTPClient` interface in the constructor.
   - Keep authentication, pagination, request parameters, and response parsing inside the wrapper.
   - Normalize provider-specific field names and response shapes here.

4. Keep provider drift out of downstream layers.
   - Pipelines, repositories, and jobs should not need to understand raw provider payloads.
   - If the provider changes shape, fix the wrapper and schemas first.

5. Create or update Pydantic schemas in `schemas/`.
   - Return typed schema objects from wrapper methods.
   - Model nullable fields explicitly.
   - If the provider sends mixed types for a field, choose a clear internal contract and encode it in the schema.

6. Test the wrapper with mocked HTTP responses.
   - Mock the `HTTPClient`.
   - Use realistic sample payloads from the provider.
   - Assert on the returned schema objects and normalized field values.
   - Cover pagination, mixed-type fields, optional fields, and malformed-response edge cases when relevant.

7. Validate in the narrowest order.
   - Run the focused wrapper test file first.
   - If adapter output affects a pipeline, run the nearest pipeline tests next.
   - Widen test scope only if necessary.

## Decision Points

### Reuse or create an interface
- Reuse an existing interface if the API fits an existing domain contract.
- Create a new interface if introducing a new API category or capability boundary.

### Normalize in wrapper or schema
- Normalize in the wrapper when the provider naming or nesting is inconsistent.
- Widen the schema when the provider legitimately returns multiple scalar types for the same field and the app can tolerate that contract.

### Required versus optional fields
- Keep required fields required when downstream code depends on them.
- Do not relax fields just to silence parsing failures if the real issue is incorrect response mapping.

## Completion Checklist

A task using this skill is complete when:

- an internal interface exists and is the dependency boundary
- the wrapper accepts `HTTPClient`
- provider-specific parsing stays inside the wrapper
- wrapper methods return Pydantic schemas
- focused unit tests exist for the wrapper
- realistic mocked payloads are used in tests
- the focused wrapper tests pass
- any affected downstream tests also pass

## Example Prompts

- `@api-adapter-skill Add a wrapper for a new odds API behind an internal interface`
- `@api-adapter-skill Fix a provider payload mismatch in an existing adapter and update its tests`
- `@api-adapter-skill Add Pydantic response models and unit tests for a new sports stats wrapper`
- `@api-adapter-skill Refactor an adapter to use HTTPClient instead of direct HTTP calls`
