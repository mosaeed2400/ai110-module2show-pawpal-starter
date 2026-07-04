# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Today's Schedule
========================================
07:30  Whiskers: Feeding (MEDIUM)
08:00  Rex: Morning walk (HIGH)
18:00  Rex: Evening medication (HIGH)

## 🧪 Testing PawPal+

Run the full test suite:

python -m pytest

Run with coverage:

pytest --cov

**What the tests cover:**
- Task completion and task addition (happy path)
- Sorting correctness: chronological order, priority ordering with time tie-break, and 
  stability when two tasks share the same time
- Filtering: by pet name, by completion status, both combined, and the `None` vs `False` 
  distinction for `completed`
- Recurring tasks: daily/weekly respawn with `due_date` correctly advanced via `timedelta` 
  (including a month-boundary case), plus detached (no-pet) respawn
- Conflict detection: same-time clashes, multi-task clashes, completed-task exclusion, and 
  unassigned-pet labeling
- Empty/edge states: a pet with no tasks, an owner with no pets, and an empty plan
- Three tests document **known limitations** rather than hiding them: non-zero-padded time 
  strings sort incorrectly, an unknown `frequency` value silently behaves like a one-off 
  task, and calling `mark_complete()` twice on a recurring task spawns a second new 
  occurrence. These are intentionally left as-is for this project's scope, but are called 
  out explicitly so the behavior is documented rather than silently wrong.

Sample test output:

tests/test_pawpal.py ................................                          [100%]
32 passed in 0.03s

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5)

I'm confident the core scheduling logic (sorting, filtering, conflict detection, and 
recurrence) behaves correctly for the scenarios a typical pet owner would hit. I'm holding 
back one star because of the three documented known limitations above — none of these 
would surprise a real user under normal use, but they're real gaps I'd want to close before 
calling this production-ready.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_by_priority()` | Time sort compares zero-padded "HH:MM" strings directly; priority sort ranks HIGH > MEDIUM > LOW, tie-broken by time |
| Filtering | `Scheduler.filter_tasks(pet_name=..., completed=...)` | Filters compose — pass either, both, or neither to narrow by pet and/or completion status |
| Conflict handling | `Scheduler.detect_conflicts()` | Groups tasks by exact `preferred_time`; flags any time slot with 2+ incomplete tasks, across any pet |
| Recurring tasks | `Task.mark_complete()` | Daily/weekly tasks automatically spawn a fresh incomplete copy with `due_date` advanced via `timedelta` (+1 day or +7 days) |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->