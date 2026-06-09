# Learner Dashboard API Plan

The current Learner Dashboard uses frontend-only pagination, filtering, and sorting. This is enough for the prototype because each learner has a small amount of data today. Before real families or classrooms accumulate large histories, the dashboard should move the long record views to server-side pagination.

## Current State

- `GET /api/learners/{learner_id}/analytics` returns aggregate learner analytics, skill breakdown, and mistake notebook data.
- `GET /api/learners/{learner_id}/sessions` returns the full session list.
- The Angular dashboard tables paginate, filter, and sort these full in-memory arrays.
- No existing API behavior should change until the server-side endpoints are implemented.

## Future Endpoints

```text
GET /api/learners/{learner_id}/dashboard-summary
```

Returns compact overview data for the dashboard landing tab:

- summary metric cards;
- latest practice sessions;
- weakest skills;
- most frequent mistakes;
- future badge summary.

```text
GET /api/learners/{learner_id}/sessions
  ?page=1
  &page_size=20
  &sort=-created_at
  &status=completed
  &plugin=multiply_by_11
  &subject=Math
```

Returns paginated practice history rows.

```text
GET /api/learners/{learner_id}/mistakes
  ?page=1
  &page_size=20
  &sort=-times_missed
  &plugin=multiply_by_11
  &min_missed=2
  &q=...
```

Returns paginated mistake notebook rows.

```text
GET /api/learners/{learner_id}/skills
  ?sort=accuracy
  &subject=Math
```

Returns skill breakdown rows, eventually with optional trend fields.

```text
GET /api/learners/{learner_id}/badges
  ?status=awarded
```

Returns awarded and in-progress badges after the badge system exists.

## Paged Response Shape

Paged endpoints should use a consistent envelope:

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total_items": 0,
  "total_pages": 0
}
```

## Sorting And Filtering Rules

- Use `sort=field` for ascending and `sort=-field` for descending.
- Keep stable secondary ordering, usually newest first or `id` descending.
- Validate sort fields server-side; unknown sort fields should return a clear 422 response.
- Text search should be case-insensitive.
- Filtering by `subject`, `plugin`, and `status` should use exact values from stored sessions.

## Migration Timing

Implement backend pagination before any of these happen:

- learner session histories commonly exceed a few hundred rows;
- teacher/classroom mode introduces many learners per account;
- charts depend on longer time ranges;
- badge rules query large histories repeatedly.

Until then, frontend-only pagination keeps the prototype simpler while preserving the UI structure needed for server-side pagination later.
