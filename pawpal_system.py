"""PawPal+ — pet care scheduling app.

Core domain model from the UML design: Owner, Pet, Task, and Scheduler.
Task creation, pet/owner management, time-based and priority planning,
filtering, recurring-task handling, conflict detection, and plan
explanation are all implemented.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import IntEnum
from typing import Dict, List, Optional


class Priority(IntEnum):
    """Task priority. Ordered so higher value == more urgent, which lets
    sort_by_priority sort on the enum directly."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Task:
    description: str
    duration: int
    priority: Priority
    preferred_time: str
    completed: bool = False
    frequency: str = ""
    # Calendar day this task is due. Defaults to today; default_factory (not a
    # bare date.today()) ensures it's evaluated per-instance, not once at import.
    due_date: date = field(default_factory=date.today)
    # Back-reference to the owning Pet. Excluded from repr/compare to avoid
    # infinite recursion and equality cycles through the Pet <-> Task graph.
    pet: Optional[Pet] = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> Optional[Task]:
        """Mark this task completed.

        For a recurring task (frequency "daily"/"weekly"), spawn the next
        occurrence: a fresh incomplete copy at the same preferred_time, added
        to the same pet, with due_date advanced past this one (a daily task
        respawns one day later, a weekly task seven days later). Returns the
        new task, or None for one-off tasks.
        """
        self.completed = True
        step = {"daily": timedelta(days=1), "weekly": timedelta(days=7)}.get(self.frequency)
        if step is None:
            return None
        next_task = Task(
            description=self.description,
            duration=self.duration,
            priority=self.priority,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
            due_date=self.due_date + step,
        )
        if self.pet is not None:
            self.pet.add_task(next_task)  # add_task sets the back-reference
        return next_task


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and set its back-reference to this pet."""
        self.tasks.append(task)
        task.pet = self  # keep the back-reference in sync

    def get_tasks(self) -> List[Task]:
        """Return this pet's list of tasks."""
        return self.tasks


class Owner:
    def __init__(self, name: str, pets: List[Pet] = None, preferences: Dict = None):
        """Create an owner with an optional starting list of pets and preferences."""
        self.name = name
        self.pets: List[Pet] = pets if pets is not None else []
        self.preferences: Dict = preferences if preferences is not None else {}

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Task]:
        """Return a flat list of every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.get_tasks()]


class Scheduler:
    def __init__(self, owner: Owner, available_minutes: int):
        """Create a scheduler for an owner with a daily time budget in minutes."""
        self.owner = owner
        self.available_minutes = available_minutes

    def generate_plan(self) -> List[Task]:
        """Build today's plan from the owner's tasks, sorted by time."""
        tasks = self.owner.get_all_tasks()
        return self.sort_by_time(tasks)

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return the tasks most-urgent first, tie-broken by earlier time.

        Priority is an IntEnum with HIGH == 3, so sorting on -priority puts
        HIGH ahead of LOW; equal-priority tasks fall back to preferred_time.
        """
        return sorted(tasks, key=lambda task: (-task.priority, task.preferred_time))

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return the tasks sorted chronologically by preferred_time."""
        # preferred_time is "HH:MM" 24-hour; string sort matches chronological
        # order for that fixed-width format.
        return sorted(tasks, key=lambda task: task.preferred_time)

    def filter_tasks(
        self,
        tasks: List[Task],
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> List[Task]:
        """Return tasks matching the given filters.

        Each filter is optional; passing None ignores it. So filter_tasks(tasks)
        returns everything, filter_tasks(tasks, pet_name="Rex", completed=False)
        returns Rex's outstanding tasks.
        """
        result = tasks
        if pet_name is not None:
            result = [t for t in result if t.pet is not None and t.pet.name == pet_name]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        return result

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return a description for each time slot holding 2+ outstanding tasks.

        Completed tasks are ignored since a finished task can't conflict.
        """
        by_time: Dict[str, List[Task]] = {}
        for task in tasks:
            if task.completed:
                continue
            by_time.setdefault(task.preferred_time, []).append(task)

        conflicts: List[str] = []
        for time in sorted(by_time):
            clashing = by_time[time]
            if len(clashing) > 1:
                labels = ", ".join(
                    f"{t.description} ({t.pet.name if t.pet else 'Unassigned'})"
                    for t in clashing
                )
                conflicts.append(f"{time}: {labels}")
        return conflicts

    def find_next_available_slot(
        self, tasks: List[Task], duration: int, step: int = 15
    ) -> Optional[str]:
        """Find the earliest "HH:MM" today where a `duration`-minute task fits.

        Approach: treat each *incomplete* existing task as occupying the
        half-open interval [preferred_time, preferred_time + its duration).
        Walk candidate start times from 00:00 through the end of the day in
        `step`-minute increments (default 15). Return the first candidate whose
        own [start, start + duration) interval fits before end of day
        (24:00 / 1440 minutes) and overlaps none of the occupied intervals.
        Return None if the day is too full for the task to fit anywhere.

        Completed tasks are ignored — a finished task no longer blocks time.

        Limitations:
        - Only checks slots on the `step` grid, so it can miss a valid slot
          that starts off-grid (e.g. a 10-min gap at 08:05 is invisible on a
          15-min grid). It favors simplicity over optimal packing.
        - Does NOT consult the scheduler's available_minutes budget: it reports
          where a task *could* go in the day, not whether the owner still has
          spare time in their daily allotment.
        - Assumes zero-padded "HH:MM" preferred_time (the same assumption
          sort_by_time relies on); non-padded times parse incorrectly.
        """
        end_of_day = 24 * 60  # 1440 — the exclusive end boundary (midnight)

        # Build the occupied intervals from incomplete tasks only.
        occupied = []  # list of (start_minute, end_minute)
        for task in tasks:
            if task.completed:
                continue
            start = self._to_minutes(task.preferred_time)
            occupied.append((start, start + task.duration))

        candidate = 0
        while candidate + duration <= end_of_day:
            new_end = candidate + duration
            # Half-open overlap test: [candidate, new_end) vs [s, e).
            if not any(candidate < e and s < new_end for s, e in occupied):
                return self._to_hhmm(candidate)
            candidate += step
        return None

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert a zero-padded "HH:MM" string to minutes since midnight."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _to_hhmm(total_minutes: int) -> str:
        """Convert minutes since midnight back to a zero-padded "HH:MM" string."""
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    def explain_plan(self, tasks: List[Task]) -> str:
        """Return a human-readable plan: tasks in time order, then any conflicts."""
        lines = ["Today's plan:"]
        for task in self.sort_by_time(tasks):
            pet_name = task.pet.name if task.pet else "Unassigned"
            lines.append(
                f"  {task.preferred_time}  {pet_name}: {task.description} "
                f"({task.priority.name}, {task.duration} min)"
            )

        conflicts = self.detect_conflicts(tasks)
        if conflicts:
            lines.append("Conflicts:")
            lines.extend(f"  ⚠ {c}" for c in conflicts)
        else:
            lines.append("No conflicts.")
        return "\n".join(lines)


# --- Persistence -----------------------------------------------------------
#
# Serialize an Owner (with its Pets and Tasks) to a plain JSON file using
# hand-written dict conversion — no third-party serialization library. Three
# fields need special handling:
#   * Priority is stored as its name ("HIGH") for readability, restored via
#     Priority[name].
#   * due_date (a date) is stored as an ISO string, restored via fromisoformat.
#   * Task.pet is a back-reference that forms a cycle (Pet <-> Task), so it is
#     NOT serialized; on load it is re-established with Pet.add_task(), exactly
#     as normal task creation does.


def _task_to_dict(task: Task) -> Dict:
    """Convert a Task to a JSON-safe dict. The pet back-reference is omitted
    on purpose — it forms a cycle and is reconstructed on load."""
    return {
        "description": task.description,
        "duration": task.duration,
        "priority": task.priority.name,  # e.g. "HIGH", not the int value
        "preferred_time": task.preferred_time,
        "completed": task.completed,
        "frequency": task.frequency,
        "due_date": task.due_date.isoformat(),  # "YYYY-MM-DD"
    }


def _pet_to_dict(pet: Pet) -> Dict:
    """Convert a Pet and its tasks to a JSON-safe dict."""
    return {
        "name": pet.name,
        "species": pet.species,
        "breed": pet.breed,
        "tasks": [_task_to_dict(t) for t in pet.tasks],
    }


def _owner_to_dict(owner: Owner) -> Dict:
    """Convert an Owner and its full pet/task graph to a JSON-safe dict."""
    return {
        "name": owner.name,
        "preferences": owner.preferences,
        "pets": [_pet_to_dict(p) for p in owner.pets],
    }


def save_to_json(owner: Owner, filepath: str) -> None:
    """Serialize an Owner (with all Pets and their Tasks) to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(_owner_to_dict(owner), f, indent=2)


def _task_from_dict(data: Dict) -> Task:
    """Reconstruct a Task from its dict form. The pet back-reference is left
    as None here; the caller attaches it via Pet.add_task()."""
    return Task(
        description=data["description"],
        duration=data["duration"],
        priority=Priority[data["priority"]],  # name -> enum member
        preferred_time=data["preferred_time"],
        completed=data["completed"],
        frequency=data["frequency"],
        due_date=date.fromisoformat(data["due_date"]),
    )


def _pet_from_dict(data: Dict) -> Pet:
    """Reconstruct a Pet and its tasks from dict form, re-establishing each
    task's back-reference through add_task()."""
    pet = Pet(name=data["name"], species=data["species"], breed=data["breed"])
    for task_data in data["tasks"]:
        # add_task appends the task AND sets task.pet -> pet, restoring the
        # back-reference exactly as it was created originally.
        pet.add_task(_task_from_dict(task_data))
    return pet


def load_from_json(filepath: str) -> Owner:
    """Reconstruct a full Owner (with Pets and Tasks, back-references intact)
    from a JSON file written by save_to_json.

    Raises FileNotFoundError if the file does not exist — the standard, clear
    error for a missing path, left to propagate rather than masked.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    owner = Owner(name=data["name"], preferences=data.get("preferences", {}))
    for pet_data in data["pets"]:
        owner.add_pet(_pet_from_dict(pet_data))
    return owner
