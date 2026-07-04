# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I asked my AI coding assistant (Claude Code) to add a third algorithmic capability to my 
Scheduler beyond the core sorting/filtering/conflict/recurrence requirements: a 
`find_next_available_slot(tasks, duration)` method that finds the earliest free time slot 
in the day for a new task of a given duration, treating existing incomplete tasks as 
occupied time ranges. I also asked for a demo in `main.py` and pytest coverage.

**What did the agent do?**

The agent implemented `find_next_available_slot()` in `pawpal_system.py`, along with two 
static helper methods (`_to_minutes` and `_to_hhmm`) to convert between "HH:MM" strings 
and minutes-since-midnight for arithmetic. The algorithm walks candidate start times on a 
15-minute grid from 00:00, skips completed tasks, and uses a half-open interval overlap 
test (`candidate < existing_end and existing_start < candidate_end`) to find the first 
non-conflicting slot, returning `None` if the day is fully booked. It also added a demo 
section to `main.py` and five new pytest tests (free slot found, skips an early conflict, 
fully booked returns `None`, empty task list returns the start of day, and completed tasks 
are correctly ignored).

**What did you have to verify or fix manually?**

I reviewed the overlap-detection logic manually to confirm the half-open interval test was 
correct (this is the standard, textbook-correct approach for interval overlap checks). I 
also caught that the initial `main.py` demo wasn't illustrative — it returned `00:00` 
trivially, since the existing demo tasks (07:30 and 08:00) didn't block the very start of 
the day, so the algorithm never had to actually search past a conflict. I asked the agent 
to add an early-morning "Sleep/quiet hours" block (00:00–07:00) to force the search to walk 
past multiple occupied intervals before landing on a real free slot (08:30), which made the 
demo actually demonstrate the algorithm's behavior instead of just confirming a trivial 
default. I also confirmed the docstring honestly documents the method's real limitations — 
it doesn't consult `available_minutes`, and it can miss off-grid slots narrower than the 
15-minute step — rather than overselling what the algorithm actually does.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->