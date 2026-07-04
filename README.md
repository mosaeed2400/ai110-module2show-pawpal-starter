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
pytest

Run with coverage:
pytest --cov

Sample test output:

# Paste your pytest output here

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