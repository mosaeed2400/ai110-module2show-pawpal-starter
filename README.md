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
- Next available slot: finding a free slot around existing tasks, skipping completed tasks, 
  a fully booked day returning `None`, and an empty task list returning the start of day
- Data persistence: round-tripping an owner/pets/tasks graph through JSON, preserving the 
  `Priority` enum, `due_date`, and the `Task.pet` back-reference, plus a clear error on a 
  missing file
- Empty/edge states: a pet with no tasks, an owner with no pets, and an empty plan
- Three tests document **known limitations** rather than hiding them: non-zero-padded time 
  strings sort incorrectly, an unknown `frequency` value silently behaves like a one-off 
  task, and calling `mark_complete()` twice on a recurring task spawns a second new 
  occurrence. These are intentionally left as-is for this project's scope, but are called 
  out explicitly so the behavior is documented rather than silently wrong.

Sample test output:

tests/test_pawpal.py .....................................                          [ 90%]
tests/test_persistence.py ....                                                       [100%]
41 passed in 0.02s

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
| Next available slot | `Scheduler.find_next_available_slot(tasks, duration)` | Finds the earliest free "HH:MM" slot on a 15-min grid, skipping completed tasks and occupied intervals; doesn't consult `available_minutes` |

## Features

- **Owner → Pet → Task model** — an owner holds pets, each pet holds its own care tasks; tasks carry a description, duration, priority, and preferred time.
- **Priority levels** — tasks are ranked LOW / MEDIUM / HIGH via a `Priority` enum.
- **Two schedule views** — order tasks chronologically (by preferred time) or by priority (most urgent first, ties broken by earlier time).
- **Filtering** — filter tasks by pet and/or completion status.
- **Conflict detection** — flags time slots where two or more outstanding tasks are scheduled at once, shown as plain-language warnings in the UI.
- **Recurring tasks** — daily or weekly tasks respawn a fresh occurrence (with the due date advanced) when marked complete; one-off tasks simply close.
- **Next available slot finder** — given a new task's duration, finds the earliest free time today that doesn't overlap any existing incomplete task.
- **Data persistence** — save an owner's full pet/task graph to a JSON file and reload it later, preserving priority, due dates, and pet-task relationships.
- **Mark complete** — tick tasks off directly in the app and watch recurring ones reappear.
- **Plan explanation** — `explain_plan()` produces a readable, time-ordered summary of the day plus any conflicts.
- **Interactive Streamlit UI** — add tasks, toggle sort/filter, generate the day's schedule, and complete tasks from the browser.
- **Tested** — automated test suite covering sorting, filtering, conflict detection, recurrence, slot-finding, and persistence.

## Known Limitations

- **`available_minutes` is not enforced.** The `Scheduler` accepts a daily time budget, but `generate_plan()` currently only sorts tasks — it does not cap the plan or drop tasks that exceed the budget.
- **`Owner.preferences` is stored but unused.** The field exists on the model, but no scheduling logic reads from it yet.
- **`find_next_available_slot()` checks a 15-minute grid**, so it can miss a valid but narrower off-grid gap, and it doesn't consult `available_minutes` either.
- **Persistence is manual and CLI-only.** `save_to_json`/`load_from_json` exist in `pawpal_system.py` and are demonstrated in `main.py`, but the Streamlit UI (`app.py`) does not yet call them — the browser app's data still resets each session.

## 💾 Data Persistence

PawPal+ can save an owner's entire pet/task graph to a JSON file and reload it later, so data isn't lost between runs of `main.py`.

**How it works:**
- `save_to_json(owner, filepath)` walks the object graph (`Owner` → `Pet` → `Task`) and converts each object to a plain dictionary using hand-written helper functions (`_owner_to_dict`, `_pet_to_dict`, `_task_to_dict`) — no external serialization library is used, to keep dependencies minimal.
- Three details needed special handling:
  - **The `Priority` enum** is stored as its name (`"HIGH"`) rather than its raw integer value, so the file stays human-readable and isn't tied to the enum's internal numbering. It's restored with `Priority[name]`.
  - **The `due_date` field** (a Python `date`) is stored as an ISO 8601 string (`"2026-07-04"`) via `.isoformat()`, and restored with `date.fromisoformat()`.
  - **The circular `Task.pet` back-reference** is never serialized at all (it would create a cycle in the JSON). On load, each task is reattached to its pet via `pet.add_task(task)` — the same method used everywhere else in the app to keep that back-reference in sync — so the reconstructed object graph is identical in shape to a freshly built one.
- `load_from_json(filepath)` reverses the process, rebuilding a full `Owner` with all its `Pet`s and `Task`s. A missing file raises a standard `FileNotFoundError` rather than a custom error, since that's already the clearest signal for this situation.

**Files modified:** `pawpal_system.py` (added `save_to_json`, `load_from_json`, and their private `_to_dict`/`_from_dict` helpers), `main.py` (added a demo section), `tests/test_persistence.py` (new file, 4 tests).

## 📸 Demo Walkthrough

**Main UI features:** PawPal+ lets a user enter basic owner and pet details, add care 
tasks with a title, duration, priority, preferred time, and repeat frequency (one-time, 
daily, or weekly), then view those tasks in a live table. From there, the user can toggle 
between two sort views (by time or by priority), filter the list by completion status, 
mark individual tasks complete, and generate a full daily schedule.

**Example workflow:**
1. Enter an owner name and add a pet (e.g., "Mochi", a dog).
2. Add a few care tasks with different priorities and times — for example, a daily 
   "Morning walk" at 09:00 (HIGH priority) and a weekly "Swimming" session at 11:00 
   (MEDIUM priority).
3. Toggle "Sort by" between **By Time** and **By Priority** to see the task list reorder.
4. Filter the list to **Incomplete** or **Completed** to narrow what's shown.
5. Click **Generate schedule** to see the full day's plan in time order, along with either 
   a success message ("No scheduling conflicts") or a plain-language warning if two tasks 
   land on the same time slot.
6. Click **Mark complete** on a recurring task — a confirmation message shows the task was 
   completed and states when the next occurrence is due, since daily/weekly tasks 
   automatically respawn with an advanced due date.

**Key Scheduler behaviors demonstrated:** chronological and priority-based sorting, 
pet/status filtering, conflict detection with owner-friendly warning text, automatic 
recurrence via `due_date` advancement, and finding the next available time slot around 
existing commitments.

**Sample CLI output** (from running `python3 main.py`, which exercises the same Scheduler 
logic outside the UI):