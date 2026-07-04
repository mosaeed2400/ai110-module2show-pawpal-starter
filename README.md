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

## Features

- **Owner → Pet → Task model** — an owner holds pets, each pet holds its own care tasks; tasks carry a description, duration, priority, and preferred time.
- **Priority levels** — tasks are ranked LOW / MEDIUM / HIGH via a `Priority` enum.
- **Two schedule views** — order tasks chronologically (by preferred time) or by priority (most urgent first, ties broken by earlier time).
- **Filtering** — filter tasks by pet and/or completion status.
- **Conflict detection** — flags time slots where two or more outstanding tasks are scheduled at once, shown as plain-language warnings in the UI.
- **Recurring tasks** — daily or weekly tasks respawn a fresh occurrence (with the due date advanced) when marked complete; one-off tasks simply close.
- **Mark complete** — tick tasks off directly in the app and watch recurring ones reappear.
- **Plan explanation** — `explain_plan()` produces a readable, time-ordered summary of the day plus any conflicts.
- **Interactive Streamlit UI** — add tasks, toggle sort/filter, generate the day's schedule, and complete tasks from the browser.
- **Tested** — automated test suite covering sorting, filtering, conflict detection, and recurrence.

## Known Limitations

- **`available_minutes` is not enforced.** The `Scheduler` accepts a daily time budget, but `generate_plan()` currently only sorts tasks — it does not cap the plan or drop tasks that exceed the budget.
- **`Owner.preferences` is stored but unused.** The field exists on the model, but no scheduling logic reads from it yet.

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
pet/status filtering, conflict detection with owner-friendly warning text, and automatic 
recurrence via `due_date` advancement.

**Sample CLI output** (from running `python3 main.py`, which exercises the same Scheduler 
logic outside the UI):

Insertion Order (as added)
18:00  Rex: Evening medication
08:00  Rex: Morning walk
07:30  Whiskers: Feeding
Time-Sorted
07:30  Whiskers: Feeding
08:00  Rex: Morning walk
18:00  Rex: Evening medication
Rex's Incomplete Tasks
08:00  Morning walk
Recurring Task (daily)
Original: Daily walk  due 2026-07-04  (completed=False)
Respawned: Daily walk  due 2026-07-05  (completed=False)
→ new due_date is 1 day later, as expected for a daily task