# French Learning Design

## Direction

French support starts as a small language-learning track inside the online practice system. The first goal is not full fluency or speech recognition. The first goal is to help a learner hear, recognize, and later spell simple French sounds using short focused practice sessions.

## Initial Scope

### Phase 1: Alphabet Sounds

- Subject: French
- Domain: Pronunciation
- Activity: Alphabet Sounds
- Student task: listen to a French letter name or simple word, then choose the matching answer.
- Audio source: browser text-to-speech, preferring `fr-CA` and falling back to `fr-FR` or any available French voice.
- Examples: simple high-frequency words such as `ami`, `chat`, `lune`, `école`, `maman`, and `papa`.

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
- Do not require speech recognition in the first phase.
- Do not save audio or student voice data in the first phase.
