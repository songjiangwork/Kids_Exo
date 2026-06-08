# Lesson Model Design

## Purpose

Kids Exo already supports printable worksheets and online practice sessions. The next content type should be a lesson: a structured teaching experience that explains a concept before, during, or after practice.

This document prepares the lesson domain model without implementing a full lesson UI yet. The important boundary is:

- A `Lesson` teaches.
- A `PracticeSession` measures answers.
- A plugin generates questions or evaluates answers.
- A lesson may link to plugins, but a lesson is not itself a plugin.

## Product Direction

Lessons should help a learner understand a skill, not just complete more questions. Good early examples include:

- Multiplying by 11 with no carrying and with carrying.
- Same tens, ones sum to 10.
- French alphabet sounds.
- French family-word listening practice.

Lessons can later contain animations, worked examples, audio, and short checkpoints. They should be reusable from both Parent-managed learning flows and future Admin-managed content publishing.

## Core Domain Objects

### Lesson

```python
@dataclass(frozen=True)
class Lesson:
    lesson_id: str
    subject: str
    topic: str
    title: str
    grade_range: tuple[int, int] | None
    locale: str
    steps: tuple[LessonStep, ...]
    linked_plugin_ids: tuple[str, ...] = ()
    release_stage: str = "draft"
```

`Lesson` is the stable content definition. It should be versionable later, because a learner's historical progress should still make sense after lesson content changes.

Suggested fields:

| Field | Meaning |
| --- | --- |
| `lesson_id` | Stable content identifier, such as `math.multiply_by_11.intro.en_ca`. |
| `subject` | Broad subject, such as `Math` or `French`. |
| `topic` | More focused grouping, such as `Mental Multiplication` or `Pronunciation`. |
| `title` | User-visible title. |
| `grade_range` | Optional approximate grade suitability. |
| `locale` | Primary lesson language. |
| `steps` | Ordered teaching sequence. |
| `linked_plugin_ids` | Plugins that can support examples or mini-practice. |
| `release_stage` | `draft`, `beta`, `published`, or `archived`. |

### LessonStep

```python
@dataclass(frozen=True)
class LessonStep:
    step_id: str
    step_type: str
    content_payload: dict[str, Any]
    linked_plugin_id: str | None = None
    linked_skill_tags: tuple[str, ...] = ()
```

`LessonStep` describes one unit in a lesson. The `content_payload` is intentionally flexible at first, because math animation, audio pronunciation, and plain explanations need different payloads.

Suggested step types:

| Step type | Purpose |
| --- | --- |
| `explanation` | Text or simple visual explanation of the idea. |
| `worked_example` | A static example with guided steps. |
| `animation` | A dynamic demonstration, such as moving digits for multiplying by 11. |
| `audio` | A listen-first step for language learning. |
| `mini_practice` | A short generated practice block, usually 1 to 5 questions. |
| `checkpoint` | A small understanding check with a stored result. |
| `summary` | Wrap-up rule, reminder, or next recommendation. |

### LessonProgress

```python
@dataclass(frozen=True)
class LessonProgress:
    learner_id: int
    lesson_id: str
    lesson_version: str
    status: str
    current_step_id: str | None
    completed_step_ids: tuple[str, ...]
    started_at: datetime
    completed_at: datetime | None = None
```

`LessonProgress` is learner-specific state. It should be separate from `PracticeSession` because watching an explanation or animation is not the same as answering a graded practice question.

Suggested statuses:

- `not_started`
- `in_progress`
- `completed`
- `skipped`

### PracticeSession

The existing `PracticeSession` remains the source of truth for graded exercises:

- generated questions
- expected answers and evaluation payloads
- attempts
- correctness
- timing
- mistake notebook and analytics

If a lesson includes a `mini_practice` step, that step can create or reference a real `PracticeSession`, but the lesson should only store a link to it. This keeps statistics and mistake tracking consistent with the rest of the system.

## Relationship To Plugins

Plugins should remain focused on generating questions, validating settings, and supporting answer evaluation.

A lesson can reference a plugin in three ways:

- Use a plugin id to generate mini-practice questions.
- Use plugin settings to create examples that match the lesson topic.
- Use skill tags to connect lesson progress with later analytics.

The lesson must not import UI components or directly own plugin internals. It should call the same domain services that Parent Studio and Student Practice already use.

## Example: Multiply By 11 Intro

```python
Lesson(
    lesson_id="math.mental_multiplication.multiply_by_11.intro.en_ca",
    subject="Math",
    topic="Mental Multiplication",
    title="Multiply by 11",
    grade_range=(4, 6),
    locale="en-CA",
    linked_plugin_ids=("multiply_by_11",),
    steps=(
        LessonStep(
            step_id="rule-no-carrying",
            step_type="explanation",
            content_payload={
                "heading": "When the digit sum is less than 10",
                "body": "Keep the outside digits and put their sum in the middle.",
            },
        ),
        LessonStep(
            step_id="worked-example-34",
            step_type="worked_example",
            content_payload={
                "expression": "34 x 11",
                "steps": ["Keep 3 and 4 outside.", "3 + 4 = 7.", "Answer: 374."],
            },
            linked_plugin_id="multiply_by_11",
            linked_skill_tags=("mental_multiplication", "multiply_by_11", "no_carrying"),
        ),
        LessonStep(
            step_id="animation-57",
            step_type="animation",
            content_payload={
                "animation_type": "multiply_by_11_digits",
                "multiplicand": 57,
            },
            linked_plugin_id="multiply_by_11",
            linked_skill_tags=("mental_multiplication", "multiply_by_11", "with_carrying"),
        ),
        LessonStep(
            step_id="try-three",
            step_type="mini_practice",
            content_payload={
                "question_count": 3,
                "plugin_settings": {
                    "multiplicand_digits": [2],
                    "strategies": ["no_carrying", "with_carrying"],
                },
            },
            linked_plugin_id="multiply_by_11",
        ),
    ),
)
```

## Example: French Alphabet Sounds Intro

```python
Lesson(
    lesson_id="french.pronunciation.alphabet_sounds.intro.en_ca",
    subject="French",
    topic="Pronunciation",
    title="French Alphabet Sounds",
    grade_range=None,
    locale="en-CA",
    linked_plugin_ids=("french_alphabet_sounds",),
    steps=(
        LessonStep(
            step_id="listen-first",
            step_type="audio",
            content_payload={
                "heading": "Listen carefully",
                "body": "French letter names can sound different from English letter names.",
                "audio_group": "fr-FR-DeniseNeural/alphabet",
            },
        ),
        LessonStep(
            step_id="short-check",
            step_type="mini_practice",
            content_payload={
                "question_count": 5,
                "plugin_settings": {
                    "strategies": ["letter_name_to_letter"],
                },
            },
            linked_plugin_id="french_alphabet_sounds",
        ),
    ),
)
```

## API Shape Later

Future read-only catalog routes can be small:

```text
GET /api/lessons
GET /api/lessons/{lesson_id}
POST /api/learners/{learner_id}/lessons/{lesson_id}/start
PATCH /api/learners/{learner_id}/lesson-progress/{progress_id}
```

The first implementation can keep lesson definitions in code, similar to plugin metadata. A database-backed content model can wait until Admin publishing exists.

## Frontend Shape Later

Suggested future Angular areas:

```text
web-client/src/app/learn/lesson-player/
web-client/src/app/manage/lessons/
```

The Student lesson player should be visually close to Student Practice, but less test-like:

- larger explanations
- calmer pacing
- optional audio controls
- optional animation steps
- small checkpoints instead of long drills

Parent Studio can eventually show recommended lessons next to practice creation, especially when a learner struggles with a skill.

## Persistence Notes

Do not mix lesson progress into practice attempts.

Future persistence can use ORM/Alembic tables such as:

| Table | Purpose |
| --- | --- |
| `lesson_progress` | Learner progress through lesson steps. |
| `lesson_step_events` | Optional events such as viewed, replayed audio, or completed checkpoint. |
| `lesson_practice_links` | Link a mini-practice step to an existing practice session. |

No handwritten SQL should be used. Migrations should follow the existing SQLAlchemy 2.0 ORM + Alembic convention.

## Acceptance Criteria For Phase 6

- Lesson, LessonStep, LessonProgress, and PracticeSession are clearly separated.
- Lessons can link to plugins without becoming plugins.
- Mini-practice uses existing practice-session infrastructure.
- No current PDF, online practice, learner management, or printable worksheet behavior changes.
