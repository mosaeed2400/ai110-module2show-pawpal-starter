"""PawPal+ — pet care scheduling app.

Core domain model from the UML design: Owner, Pet, Task, and Scheduler.
Task creation, pet/owner management, time-based and priority planning,
filtering, recurring-task handling, conflict detection, and plan
explanation are all implemented.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
    # Back-reference to the owning Pet. Excluded from repr/compare to avoid
    # infinite recursion and equality cycles through the Pet <-> Task graph.
    pet: Optional[Pet] = field(default=None, repr=False, compare=False)

    def mark_complete(self) -> Optional[Task]:
        """Mark this task completed.

        For a recurring task (frequency "daily"/"weekly"), spawn the next
        occurrence: a fresh incomplete copy at the same preferred_time, added
        to the same pet. Returns the new task, or None for one-off tasks.
        """
        self.completed = True
        if self.frequency not in ("daily", "weekly"):
            return None
        next_task = Task(
            description=self.description,
            duration=self.duration,
            priority=self.priority,
            preferred_time=self.preferred_time,
            frequency=self.frequency,
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
