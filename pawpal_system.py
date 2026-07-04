"""PawPal+ — pet care scheduling app.

Core domain model from the UML design: Owner, Pet, Task, and Scheduler.
Task creation, pet/owner management, and time-based planning are
implemented; priority sorting, filtering, conflict detection, and plan
explanation are stubbed for Phase 4.
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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


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
        """Return the tasks sorted by priority (Phase 4)."""
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return the tasks sorted chronologically by preferred_time."""
        # preferred_time is "HH:MM" 24-hour; string sort matches chronological
        # order for that fixed-width format.
        return sorted(tasks, key=lambda task: task.preferred_time)

    def filter_tasks(self, tasks: List[Task], criteria) -> List[Task]:
        """Return the tasks matching the given criteria (Phase 4)."""
        pass

    def detect_conflicts(self, tasks: List[Task]) -> List[str]:
        """Return descriptions of any scheduling conflicts among the tasks (Phase 4)."""
        pass

    def explain_plan(self, tasks: List[Task]) -> str:
        """Return a human-readable explanation of the plan (Phase 4)."""
        pass
