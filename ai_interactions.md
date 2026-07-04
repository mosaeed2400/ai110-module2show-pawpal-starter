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
| **Model / tool used** | Claude Code (VS Code) | GitHub Copilot (VS Code) |
| **Prompt** | "I have a Task class with a frequency field ('daily'/'weekly') and a due_date field. Write a Python method that, when a weekly task is marked complete, calculates the next occurrence's due date, correctly handling month and year boundaries." | Same prompt |
| **Response summary** | Explained that `date + timedelta` arithmetic already handles month/year rollover automatically, then proposed a standalone `next_due_date()` method as an optional addition — without modifying my existing `mark_complete()` code. Verified the approach with a manual script testing three boundary cases (year rollover, leap-year February, non-leap February) before suggesting anything be changed. | Read my existing `Task`/`mark_complete()` code directly, then autonomously implemented a `next_due_date()` method, refactored `mark_complete()` to call it instead of an inline dict lookup, added new boundary-crossing tests to `test_pawpal.py`, and ran the test suite — all without asking first. |
| **What was useful** | The explanation of *why* `date + timedelta` handles rollovers correctly (calendar-aware arithmetic through the underlying day count) was genuinely educational, and the manual verification with real dates (2026-12-29 → 2027-01-05, leap year Feb 26 → Mar 4) built confidence in the approach before any code changed. | Moved faster end-to-end — implemented, tested, and verified in one pass. The refactor correctly preserved existing `mark_complete()` behavior (verified by running my full suite, which went from 41 to 43 passing tests, meaning nothing broke and real new coverage was added). |
| **Problems noticed** | Only proposed a plan — I would have needed a follow-up prompt to actually apply it, which is slower if I already trusted the approach. | Modified my actual codebase directly without asking permission first, meaning I had to review a completed change after the fact via `git diff` rather than approve a plan beforehand. For a change touching core recurrence logic, I would have preferred to review the plan before it was applied to my working code. |
| **Decision** | Kept Copilot's applied refactor, since I verified via `git diff` and a full test run (43 passed) that it was behaviorally safe and didn't alter any existing test outcomes — including the two "known limitation" tests documenting `mark_complete()`'s current behavior around unknown frequencies and double-completion. | — |

**Which approach did you use in your final implementation and why?**

I ended up keeping Copilot's applied `next_due_date()` refactor rather than reverting to my original inline `mark_complete()` logic, since it's a safe, behavior-preserving extraction that also makes the due-date calculation independently reusable and testable. However, I valued Claude Code's more cautious, explain-before-acting workflow more as a *process* — for a change touching core scheduling logic that my existing tests depend on, I'd generally prefer to review a proposed diff before it's applied, rather than review a change that's already been made to my working tree. This reinforced a lesson from earlier in the project: agent autonomy is useful for speed, but for logic with existing test coverage riding on exact behavior, a "propose then apply" workflow gives me more control as the lead architect than a "do then explain" workflow.