# French Learning Design

## Direction

French support starts as a small language-learning track inside the online practice system. The first goal is not full fluency or speech recognition. The first goal is to help a learner hear, recognize, and later spell simple French sounds using short focused practice sessions.

## Initial Scope

### Phase 1: Alphabet Sounds

- Subject: French
- Domain: Pronunciation
- Activity: Alphabet Sounds
- Student task: listen to a French letter name, then choose the matching letter.
- Audio source: browser text-to-speech, preferring `fr-CA` and falling back to `fr-FR` or any available French voice.

### Phase 1b: Common Word Sounds

- Subject: French
- Domain: Pronunciation
- Activity: Common Word Sounds
- Student task: listen to a common French word, then choose the matching word and English meaning.
- First category: family words such as `maman`, `papa`, `parents`, `famille`, `bébé`, `enfant`, `fils`, `fille`, `frère`, `sœur`, `grand-mère`, `grand-père`, `grands-parents`, `oncle`, `tante`, `cousin`, `cousine`, `mari`, and `femme`.
- Later categories can include animals, school objects, colors, food, nature, and greetings.

### Phase 2: Letter Combinations

Planned sound groups:

- `ou`: `nous`, `vous`
- `oi`: `moi`, `toi`
- `ai` / `ei`: `maison`, `neige`
- `au` / `eau`: `eau`, `chaud`
- nasal sounds: `an` / `en`, `on`, `in` / `ain` / `ein`
- consonant groups: `ch`, `gn`, `ill`, `qu`

### Phase 3: Spelling Practice

Planned activity types:

- hear a word and type it
- fill in a missing letter or accent
- choose the correct spelling from similar options
- match a simple English meaning to a French word

## Architecture Notes

Language activities need richer question metadata than numeric math drills:

- `question_type`: `numeric` or `multiple_choice`
- `choices`: answer labels for choice-based questions
- `speech_text`: text to speak when the learner presses the audio button
- `speech_locale`: preferred language for browser TTS

The first implementation stores multiple-choice answers as one-based numeric choice indexes. That keeps scoring compatible with the current persistence model while opening the door for richer language activities. A later version can add text-answer normalization for spelling and accent-aware scoring.

## Product Notes

- Keep the activity short and friendly. The first version should feel like listening practice, not a formal test.
- Prefer common words and predictable examples.
- Do not require speech recognition in the first pronunciation phases.
- Do not save audio or student voice data unless the parent explicitly enables a speaking-practice feature later.

## Speaking-Practice Notes

Pronunciation comparison can be added later, but it should be treated as its own feature because it touches microphone permissions, privacy, and scoring quality.

Suggested rollout:

- First add record-and-replay, so learners can compare themselves with the standard audio without automatic grading.
- Then add browser speech recognition where supported, using the recognized text as a loose pass/fail signal.
- Later add real pronunciation scoring through a speech assessment service or model if we need reliable phoneme-level feedback.

## Visual Choice Notes

Language multiple-choice questions can later support cartoon image choices. A likely data shape is to add choice-level metadata, such as `image_url` and `alt_text`, instead of only storing plain string labels. This should wait until we have a small illustration style and a reliable asset workflow.
